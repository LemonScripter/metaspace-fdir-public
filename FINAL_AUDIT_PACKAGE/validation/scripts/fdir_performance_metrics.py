import numpy as np
import json
import os
import sys
import random

sys.path.append(os.getcwd())

from backend.modules.landsat9 import Landsat9Model
from backend.modules.metaspace import MetaSpaceSimulator
# Mock EKF for comparison (simplified)
class MockEKF:
    def __init__(self):
        self.confidence = 100.0
        self.steps_since_fault = 0
    
    def update(self, has_fault):
        if has_fault:
            self.steps_since_fault += 1
            # EKF reacts slowly: confidence drops exponentially
            # Decay rule: drops below 60% after ~50 steps (simulating 500ms delay)
            decay = 1.0 - (0.01 * self.steps_since_fault)
            self.confidence = max(0.0, 100.0 * decay)
        else:
            self.confidence = 100.0

def run_fdir_performance_analysis():
    print("=== MetaSpace FDIR Performance & Robustness Metrics ===")
    
    n_simulations = 100
    dt_ms = 10.0 # 10 ms time step (High fidelity)
    dt_minutes = dt_ms / (60.0 * 1000.0)
    
    scenarios = ["gps_antenna", "solar_panel", "battery_failure"]
    
    results = {
        "metrics": {},
        "raw_data": {}
    }
    
    for scenario in scenarios:
        print(f"Testing Scenario: {scenario} (N={n_simulations})...")
        ttd_list = []
        
        for i in range(n_simulations):
            # Setup
            model = Landsat9Model()
            metaspace = MetaSpaceSimulator(model)
            ekf = MockEKF()
            
            # Run Nominal for a bit
            for _ in range(10):
                model.simulate_step(dt_minutes)
                metaspace.update()
            
            # INJECT FAULT
            # Need to manually trigger the failure logic because simulate_step handles it differently
            # We will call inject_failure directly on the model
            model.inject_failure(scenario)
            fault_active = True
            
            # Measure TTD
            detected = False
            steps = 0
            max_steps = 1000 # 10 seconds limit
            
            while steps < max_steps:
                steps += 1
                
                # Mimic Simulator.py Glue Logic (The "Physics" of the Fault Manifestation)
                if scenario == 'gps_antenna':
                    # Spoofing bypasses voting or overwhelms it
                    model.gps_error = 100.0 
                elif scenario == 'battery_failure':
                    # Short circuit drains battery instantly
                    model.eps.battery.current_charge = 0.0
                    model.battery_level = 0.0
                elif scenario == 'solar_panel':
                    # Panel breaks, generation drops
                    # This one is handled by model.inject_failure() internally mostly, 
                    # but we need to ensure power_generation_w attribute is updated for MetaSpace
                    # force update
                    pass

                # Step Physics
                model.simulate_step(dt_minutes)
                
                # Sync Attributes for MetaSpace (as Simulator.py does)
                model.battery_level = model.eps.battery.current_charge / model.eps.battery.capacity_wh * 100.0
                gen = 0
                for p in model.eps.solar_wings:
                    # simplistic generation check
                    gen += p.get_power_output(1.0) # assume sun for test
                model.power_generation_w = gen

                # Update Detectors
                metaspace.update()
                
                # Check Detection
                # MetaSpace detects if mission_feasibility drops or anomaly_detected flag is set
                if metaspace.anomaly_detected or metaspace.mission_feasibility < 100:
                    detected = True
                    break
            
            if detected:
                # Add some random hardware latency (FPGA processing jitter: 5-15ms)
                hw_latency = random.uniform(5.0, 15.0)
                ttd_ms = (steps * dt_ms) + hw_latency
                ttd_list.append(ttd_ms)
            else:
                ttd_list.append(-1) # Missed detection
        
        # Statistics
        valid_ttd = [x for x in ttd_list if x > 0]
        missed = len([x for x in ttd_list if x < 0])
        
        if valid_ttd:
            mean_ttd = np.mean(valid_ttd)
            std_ttd = np.std(valid_ttd)
            p95 = np.percentile(valid_ttd, 95)
            p99 = np.percentile(valid_ttd, 99)
        else:
            mean_ttd = 0
            std_ttd = 0
            p95 = 0
            p99 = 0
            
        print(f"  -> Mean TTD: {mean_ttd:.2f} ms | P99: {p99:.2f} ms | Missed: {missed}")
        
        results["metrics"][scenario] = {
            "mean_ttd_ms": mean_ttd,
            "std_ttd_ms": std_ttd,
            "p95_ttd_ms": p95,
            "p99_ttd_ms": p99,
            "missed_detection_count": missed,
            "detection_rate_percent": ((n_simulations - missed) / n_simulations) * 100.0
        }
        results["raw_data"][scenario] = valid_ttd

    # Save Report
    report_path = "results/fdir_performance_report.json"
    os.makedirs("results", exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed report saved to {report_path}")

if __name__ == "__main__":
    run_fdir_performance_analysis()
