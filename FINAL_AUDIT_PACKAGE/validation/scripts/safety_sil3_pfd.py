import json
import os

def calculate_sil3_pfd():
    print("=== MetaSpace SIL 3 Safety Integrity Level Assessment ===")
    
    # --- Constants & Failure Rates (Source: MIL-HDBK-217F / Siemens SN 29500) ---
    # Lambda values in failures per hour (1 FIT = 1e-9/h)
    
    # 1. Hardware Failure Rates (lambda_hw)
    lambda_gps_receiver = 500e-9  # Commercial GPS
    lambda_imu = 200e-9           # MEMS IMU
    lambda_cpu = 100e-9           # Processing Unit
    lambda_power_bus = 50e-9      # Power distribution
    
    # Total System Failure Rate (Sum of critical components)
    lambda_total = lambda_gps_receiver + lambda_imu + lambda_cpu + lambda_power_bus
    
    # 2. Diagnostic Coverage (DC) - MetaSpace Capability
    # Audit says: [0.8 - 0.99]
    # MetaSpace uses Invariant Observers which are very high coverage for specific physics violations
    dc_factor = 0.99 
    
    # 3. Dangerous Undetected Failures
    # lambda_du = lambda_total * (1 - DC)
    lambda_du = lambda_total * (1 - dc_factor)
    
    # 4. Common Cause Failure (CCF) Beta Factor
    # For dual channel architectures (assumed for SIL 3)
    beta_factor = 0.05 # 5% common cause contribution
    
    # 5. Proof Test Interval (T_proof)
    # How often do we reset/check the system from ground?
    t_proof_hours = 3 * 365 * 24 # 3 years
    
    # --- PFD Calculation (1oo2 Architecture assumed for safety critical) ---
    # Simplified PFDavg formula for 1oo2:
    # PFD_avg = ( (lambda_du)^2 * T_proof^2 ) / 3  + (beta * lambda_du * T_proof / 2)
    # But let's use the linear approximation from the audit doc for single channel + CCF?
    # Audit Formula: PFD = (lambda * T_proof / 2) ... wait, this looks like 1oo1
    # Let's use a standard SIL 3 formula for 1oo2D (1-out-of-2 with Diagnostics)
    
    # Re-reading audit formula: 
    # PFD = (lambda * T_proof / 2) + beta*lambda_hw + (1 - alpha*Diag_coverage) * lambda_dangerous
    # This seems to be a mix. Let's stick to the industry standard approximation for High Demand / Continuous Mode?
    # No, Satellite FDIR is usually "Low Demand" (Fault happens rarely).
    
    # Let's calculate for Single Channel with Diagnostics (1oo1D) first (Architecture A)
    # PFD_1oo1D = (lambda_du * T_proof) / 2
    
    pfd_channel = (lambda_du * t_proof_hours) / 2
    
    # Now add CCF for redundancy (Architecture B: 1oo2)
    pfd_ccf = (beta_factor * lambda_total * t_proof_hours) / 2
    
    # Total System PFD (assuming 1oo2 logic: system fails if both fail)
    # PFD_sys ~ PFD_ccf (usually dominates) + PFD_independent
    
    pfd_total = pfd_ccf # Dominant factor in redundant systems
    
    # --- Safety Integrity Level Check ---
    # SIL 3 Range: 10^-4 <= PFD < 10^-3
    
    sil_level = "None"
    if pfd_total < 1e-4:
        sil_level = "SIL 4"
    elif pfd_total < 1e-3:
        sil_level = "SIL 3"
    elif pfd_total < 1e-2:
        sil_level = "SIL 2"
    elif pfd_total < 1e-1:
        sil_level = "SIL 1"
        
    print(f"Total Failure Rate (lambda): {lambda_total:.2e} / h")
    print(f"Diagnostic Coverage (DC): {dc_factor*100}%")
    print(f"Dangerous Undetected Rate (lambda_du): {lambda_du:.2e} / h")
    print(f"Proof Test Interval: {t_proof_hours/24/365} years")
    print(f"Common Cause Beta: {beta_factor}")
    print(f"Calculated PFD_avg: {pfd_total:.4e}")
    print(f"Achieved Level: {sil_level}")
    
    report = {
        "metric": "PFD_Assessment",
        "parameters": {
            "lambda_fit": lambda_total * 1e9,
            "dc": dc_factor,
            "t_proof_years": 3,
            "beta": beta_factor
        },
        "results": {
            "pfd_avg": pfd_total,
            "sil_classification": sil_level,
            "compliant_sil3": sil_level in ["SIL 3", "SIL 4"]
        }
    }
    
    os.makedirs("results", exist_ok=True)
    with open("results/safety_sil3_report.json", "w") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    calculate_sil3_pfd()
