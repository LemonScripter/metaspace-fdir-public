import numpy as np
import matplotlib.pyplot as plt
import json
import os

def analytical_damped_oscillator(t, x0, v0, zeta, omega_n):
    """
    Analytical solution for underdamped harmonic oscillator (zeta < 1).
    Equation: x'' + 2*zeta*omega_n*x' + omega_n^2*x = 0
    """
    wd = omega_n * np.sqrt(1 - zeta**2)
    A = x0
    B = (v0 + zeta * omega_n * x0) / wd
    
    return np.exp(-zeta * omega_n * t) * (A * np.cos(wd * t) + B * np.sin(wd * t))

def rk4_step(f, t, y, dt):
    """
    Runge-Kutta 4th order integration step.
    dy/dt = f(t, y)
    """
    k1 = f(t, y)
    k2 = f(t + 0.5*dt, y + 0.5*dt*k1)
    k3 = f(t + 0.5*dt, y + 0.5*dt*k2)
    k4 = f(t + dt, y + dt*k3)
    
    return y + (dt/6.0) * (k1 + 2*k2 + 2*k3 + k4)

def oscillator_dynamics(t, state, zeta, omega_n):
    """
    State space representation:
    state = [x, v]
    dx/dt = v
    dv/dt = -2*zeta*omega_n*v - omega_n^2*x
    """
    x, v = state
    dxdt = v
    dvdt = -2 * zeta * omega_n * v - omega_n**2 * x
    return np.array([dxdt, dvdt])

def run_mms_verification():
    print("=== MetaSpace MMS Verification & Numerical Stability Analysis ===")
    
    # Parameters (Satellite Flexible Appendage Simulation)
    zeta = 0.1      # Damping ratio
    omega_n = 2.0   # Natural frequency (rad/s)
    x0 = 1.0        # Initial displacement
    v0 = 0.0        # Initial velocity
    
    t_start = 0.0
    t_end = 10.0
    
    # Grid Refinement Levels
    time_steps = [0.1, 0.05, 0.025] # r = 2 refinement ratio
    results = {}
    
    errors = []
    
    for dt in time_steps:
        t_values = np.arange(t_start, t_end + dt, dt)
        y_numerical = []
        y_analytical = []
        
        state = np.array([x0, v0])
        
        for t in t_values:
            # Analytical
            exact = analytical_damped_oscillator(t, x0, v0, zeta, omega_n)
            y_analytical.append(exact)
            
            # Numerical Store
            y_numerical.append(state[0])
            
            # Step
            f = lambda t_, y_: oscillator_dynamics(t_, y_, zeta, omega_n)
            state = rk4_step(f, t, state, dt)
            
        # Error calculation (L2 Norm)
        y_num_arr = np.array(y_numerical)
        y_ana_arr = np.array(y_analytical)
        
        # Truncate to match length if necessary
        min_len = min(len(y_num_arr), len(y_ana_arr))
        rmse = np.sqrt(np.mean((y_num_arr[:min_len] - y_ana_arr[:min_len])**2))
        
        print(f"DT: {dt:.4f}s | RMSE: {rmse:.8f}")
        errors.append(rmse)
        results[f"dt_{dt}"] = {"time": t_values.tolist(), "numerical": y_numerical, "analytical": y_analytical}

    # Order of Convergence Calculation
    # p = ln( (f3-f2) / (f2-f1) ) / ln(r) roughly, or using errors
    # Since error ~ C * dt^p
    # p ~ log(error_coarse / error_fine) / log(r)
    
    r = 2.0
    p_est_1 = np.log(errors[0] / errors[1]) / np.log(r)
    p_est_2 = np.log(errors[1] / errors[2]) / np.log(r)
    
    print(f"\nObserved Order of Accuracy (p):")
    print(f"Between dt=0.1 and 0.05:  p = {p_est_1:.4f}")
    print(f"Between dt=0.05 and 0.025: p = {p_est_2:.4f}")
    print(f"Theoretical RK4 p: 4.0000")
    
    # GCI Calculation (Grid Convergence Index)
    # GCI = Fs * |epsilon| / (r^p - 1)
    # Fs = 1.25 (Safety factor for 3 grids)
    fs = 1.25
    epsilon = (errors[1] - errors[2]) / errors[1] # Relative error change
    gci = fs * abs(epsilon) / (r**p_est_2 - 1)
    
    print(f"\nGCI Calculation (Grid Convergence Index):")
    print(f"GCI = {gci*100:.6f}%")
    
    report = {
        "test": "MMS_Damped_Oscillator",
        "method": "RK4",
        "theoretical_order": 4,
        "observed_order": float(p_est_2),
        "gci_percent": float(gci * 100),
        "status": "PASS" if p_est_2 > 3.5 else "WARN"
    }
    
    os.makedirs("results", exist_ok=True)
    with open("results/mms_verification_report.json", "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"\nReport saved to results/mms_verification_report.json")

if __name__ == "__main__":
    run_mms_verification()
