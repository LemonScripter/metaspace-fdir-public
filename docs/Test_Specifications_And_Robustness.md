# Test Specifications & Robustness Analysis

**System:** MetaSpace.bio FDIR
**Date:** 2026-01-10

---

## 1. Test Specifications

The following specifications define the conditions under which the FDIR system was verified.

### 1.1 Global Parameters
- **Simulation Time Step ($\Delta t$):** 10 ms (0.01 s)
- **Solver:** Runge-Kutta 4 (RK4)
- **Precision:** Float64 (Double Precision)
- **Hardware Latency Simulation:** Uniform Random Distribution [5ms, 15ms] (Simulating FPGA/Bus jitter)

### 1.2 Test Cases (TC)

#### TC-GPS-01: GPS Spoofing Injection
- **Trigger:** Immediate step change in GPS Position Error.
- **Amplitude:** > 60m error magnitude (Threshold: 50m).
- **Physics:** Spoofing signal bypasses redundancy logic (Common Mode Attack).
- **Pass Criteria:** Detection within 100ms.

#### TC-SOLAR-01: Solar Panel Failure
- **Trigger:** Instantaneous drop in Solar Array power output to 0W or 50%.
- **Context:** Test performed during "Daylight" orbital phase.
- **Pass Criteria:** Detection before Battery SOC drops < 99%.

#### TC-BATT-01: Critical Battery Failure
- **Trigger:** Sudden drop in Battery Voltage / Charge State to 0% (Short Circuit model).
- **Pass Criteria:** Immediate transition to Safe Mode (Dead Bus protection).

---

## 2. Robustness Analysis

Robustness is the ability of the FDIR system to distinguish between **Faults** and **Nominal Disturbances** (Noise, Jitter).

### 2.1 Noise Immunity Thresholds
The Invariant Observers utilize "Gap Thresholds" to filter out sensor noise.

| Sensor | Noise Floor ($3\sigma$) | FDIR Threshold | Margin Factor |
|--------|-------------------------|----------------|---------------|
| GPS Position | $\pm 5$ m | $\pm 50$ m | **10x** |
| Power Bus | $\pm 5$ W | $\pm 500$ W | **100x** |
| Attitude | $\pm 0.01^\circ$ | $\pm 0.5^\circ$ | **50x** |

**Conclusion:** The system is highly robust against nominal sensor noise, requiring a signal deviation of at least 10x the noise floor to trigger a fault. This explains the **0.0 False Alarm Rate** observed in testing.

### 2.2 Sensitivity Analysis
The system is most sensitive to **Binary Physics Violations** (e.g. Energy created from nothing).
- **Critical Parameter:** Power Budget Balance.
- **Sensitivity:** The system detects a 50% loss of power generation within 1 simulation step.
- **Parameter Variation:** Changes in satellite mass ($\pm 10\%$) or inertia ($\pm 20\%$) do not trigger false alarms due to the adaptive nature of the dynamic model references.

---

## 3. Configuration Management

All tests were performed using the software version:
- **Core:** MetaSpace v2.0
- **Build Tag:** `meta-fdir-validation-v2.0-final-2026-01-10`
- **Python Runtime:** 3.10.x
