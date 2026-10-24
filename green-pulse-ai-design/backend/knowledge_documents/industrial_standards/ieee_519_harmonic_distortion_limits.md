# Industrial Engineering Standard: IEEE 519-2022 Harmonic Limits & Power Quality
**Standard Title:** IEEE Standard for Harmonic Control in Electric Power Systems  
**Designation:** IEEE Std 519-2022  
**Classification:** Power Quality Compliance Standard  
**Page:** 1 of 3

---

## 1. Point of Common Coupling (PCC) Definition
The Point of Common Coupling (PCC) is the 33 kV metering kiosk at the boundary of GreenPulse Facility #4 connecting to the state utility grid.

## 2. Voltage Distortion Limits at PCC (Page 2)
For bus voltages rated 1 kV to 69 kV:
- **Maximum Individual Harmonic Voltage Distortion:** 3.0%
- **Total Harmonic Distortion Voltage (THD-V):** Strictly ≤ 5.0%
- **High-Frequency Harmonics:** Frequencies above 50th order must be attenuated using line reactors or RC snubber circuits.

## 3. Current Distortion Limits (Total Demand Distortion - TDD) (Page 3)
Based on plant Short Circuit Ratio ($I_{sc} / I_L$ where $I_{sc} = 18.5\text{ kA}$, $I_L = 43.7\text{ A}$ at 33 kV):
- $I_{sc} / I_L > 100$: Maximum permissible TDD is **15.0%**.
- Harmonic orders $h < 11$: Max individual harmonic current 12.0%.
- Harmonic orders $11 \le h < 17$: Max individual harmonic current 5.5%.
- Harmonic orders $17 \le h < 23$: Max individual harmonic current 5.0%.
- Harmonic orders $23 \le h < 35$: Max individual harmonic current 2.0%.
- Exceeding TDD limits results in severe transformer neutral overheating, nuisance tripping of electronic relays, and capacitor dielectric puncture.
