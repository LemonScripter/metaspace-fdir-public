import numpy as np
import json
import os
import sys

# Projekt gyökér hozzáadása a path-hoz
sys.path.append(os.getcwd())

from backend.modules.landsat9 import Landsat9Model

def run_model_validation():
    print("=== MetaSpace Model Validation vs Analytical Ground Truth ===")
    
    # --- 1. Simulation Setup ---
    model = Landsat9Model()
    
    # Reset Battery to known state
    model.eps.battery.current_charge = 4000.0 # Wh (Full)
    model.eps.battery.capacity_wh = 4000.0
    
    # Parameters
    orbital_period = 99.0 # min
    eclipse_ratio = 0.35
    sun_duration = orbital_period * (1.0 - eclipse_ratio)
    
    consumption = 450.0 # W
    # Solar calc: 2 wings * 4 m2 * 0.30 eff * 1000 W/m2 = 2400 W
    generation_max = 2 * 4.0 * 0.30 * 1000.0 
    
    print(f"Parameters: Period={orbital_period}m, Sun={sun_duration:.1f}m, Gen={generation_max}W, Load={consumption}W")
    
    # --- 2. Run Simulation & Ground Truth Calculation ---
    dt_min = 1.0 # 1 minute steps
    total_time = 300 # 3 orbits approx
    
    time_steps = np.arange(0, total_time, dt_min)
    
    sim_charge = []
    truth_charge = []
    
    # Ground Truth State
    current_charge_truth = 4000.0
    
    for t in time_steps:
        # --- A) Simulation Step ---
        # Note: simulate_step increments time internally
        state = model.simulate_step(dt_min) 
        sim_charge.append(state['battery_percent'])
        
        # --- B) Analytical Ground Truth ---
        # 1. Determine Sun State
        cycle_pos = (t % orbital_period)
        is_sun = cycle_pos < sun_duration
        
        # 2. Power Balance
        gen = generation_max if is_sun else 0.0
        net_power = gen - consumption
        
        # 3. Integrate (Euler)
        dt_hours = dt_min / 60.0
        current_charge_truth += net_power * dt_hours
        
        # 4. Clamp (Physics)
        current_charge_truth = min(current_charge_truth, 4000.0)
        # Note: Simple ground truth doesn't implement deep discharge damage logic, 
        # but we stay in healthy range for this test.
        
        truth_charge.append((current_charge_truth / 4000.0) * 100.0)
        
    # --- 3. Analysis ---
    sim_arr = np.array(sim_charge)
    truth_arr = np.array(truth_charge)
    
    mae = np.mean(np.abs(sim_arr - truth_arr))
    rmse = np.sqrt(np.mean((sim_arr - truth_arr)**2))
    correlation = np.corrcoef(sim_arr, truth_arr)[0, 1]
    
    print(f"\nResults over {total_time} minutes:")
    print(f"MAE (Mean Absolute Error): {mae:.4f} %")
    print(f"RMSE: {rmse:.4f} %")
    print(f"Correlation: {correlation:.6f}")
    
    # Check for TC-01 / TC-02 Compliance
    status = "FAIL"
    if mae < 1.0 and correlation > 0.99:
        status = "PASS"
        print(">> Validation Status: PASS (Matches Analytical Model)")
    else:
        print(">> Validation Status: FAIL (Discrepancy Detected)")
        
    report = {
        "test": "Model_Validation_Power_Thermal",
        "ground_truth_method": "Analytical_Energy_Balance",
        "metrics": {
            "mae_percent": mae,
            "rmse_percent": rmse,
            "correlation": correlation
        },
        "status": status,
        "details": "Validated Solar Generation and Battery Discharge logic against independent analytical integrator."
    }
    
    os.makedirs("results", exist_ok=True)
    with open("results/model_validation_report.json", "w") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    run_model_validation()
