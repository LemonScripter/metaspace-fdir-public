# SIL 3 Probability of Failure on Demand (PFD) Calculation

**Date:** 2026-01-10
**System:** MetaSpace.bio FDIR
**Architecture:** 1oo2 (One-out-of-Two) Redundant System

---

## 1. Methodology

The PFD calculation follows **IEC 61508-6** simplified equations for a Low Demand Mode safety function with hardware redundancy.

### Formula
For a 1oo2 architecture, the average Probability of Failure on Demand ($PFD_{avg}$) is dominated by the Common Cause Failures (CCF).

$$ PFD_{avg} \approx PFD_{CCF} + PFD_{independent} $$

Where:
$$ PFD_{CCF} = \frac{\beta \cdot \lambda_{total} \cdot T_{proof}}{2} $$
$$ PFD_{independent} \approx \frac{(\lambda_{DU} \cdot T_{proof})^2}{3} $$

Since $PFD_{independent}$ is typically orders of magnitude smaller than $PFD_{CCF}$ in high-reliability systems with high diagnostic coverage, we use the conservative approximation:

$$ PFD_{avg} \approx \frac{\beta \cdot \lambda_{total} \cdot T_{proof}}{2} $$

---

## 2. Input Parameters

| Parameter | Symbol | Value | Unit | Source |
|-----------|--------|-------|------|--------|
| Total Failure Rate | $\lambda_{total}$ | $8.50 \times 10^{-7}$ | $h^{-1}$ | MIL-HDBK-217F (Sum of GPS, IMU, CPU, Power) |
| Diagnostic Coverage | $DC$ | $99.0$ | % | Invariant Observer Analysis (See *Diagnostic Coverage Analysis*) |
| Dangerous Undetected Rate | $\lambda_{DU}$ | $8.50 \times 10^{-9}$ | $h^{-1}$ | $\lambda_{total} \times (1 - DC)$ |
| Proof Test Interval | $T_{proof}$ | $3$ | years | Maintenance Schedule (26,280 hours) |
| Common Cause Beta Factor | $\beta$ | $0.05$ | - | IEC 61508 Standard (Typical for redundant avionics) |

---

## 3. Calculation Steps

### Step 1: Calculate Beta-Factor contribution (CCF)
$$ \lambda_{CCF} = \beta \times \lambda_{total} = 0.05 \times 8.50 \times 10^{-7} = 4.25 \times 10^{-8} h^{-1} $$

### Step 2: Calculate PFD due to CCF
$$ PFD_{CCF} = \frac{4.25 \times 10^{-8} \times 26280}{2} = \frac{1.1169 \times 10^{-3}}{2} = 5.58 \times 10^{-4} $$

### Step 3: Verify Independent Channel contribution (Optional Check)
$$ PFD_{ind} = \frac{(8.5 \times 10^{-9} \times 26280)^2}{3} = \frac{(2.23 \times 10^{-4})^2}{3} \approx 1.6 \times 10^{-8} $$
*Note: This is negligible compared to $5.58 \times 10^{-4}$.*

---

## 4. Result & Conclusion

**Calculated $PFD_{avg}$:** $5.58 \times 10^{-4}$

### SIL Classification Check
| SIL Level | PFD Range (Low Demand) | Compliance |
|-----------|------------------------|------------|
| SIL 4 | $10^{-5}$ to $10^{-4}$ | No |
| **SIL 3** | **$10^{-4}$ to $10^{-3}$** | **YES** |
| SIL 2 | $10^{-3}$ to $10^{-2}$ | Yes |
| SIL 1 | $10^{-2}$ to $10^{-1}$ | Yes |

**Conclusion:** The MetaSpace.bio FDIR system meets the quantitative requirements for **Safety Integrity Level 3 (SIL 3)**.
