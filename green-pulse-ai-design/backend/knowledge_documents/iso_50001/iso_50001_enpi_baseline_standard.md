# ISO 50001:2018 Energy Management Systems - EnPI & Baseline Guidelines
**Standard:** International Standard ISO 50001:2018 (Clause 6.3 - 6.5)  
**Document Ref:** GP-ISO50001-ENPI-MAN-V2  
**Classification:** Corporate Management System  
**Page:** 1 of 4

---

## 1. Energy Baseline (EnB) Determination (Clause 6.5)
The Energy Baseline represents the quantitative reference against which future energy performance is evaluated.
- **Baseline Period:** Calendar Year 2024 (January 1 to December 31).
- **Relevant Variables:** Ambient dry-bulb temperature, relative humidity, manufacturing volume (units/month), raw material tensile hardness, and plant operating shifts.
- **Static Factors:** Facility floor area (42,000 m²), transformer rated capacity (2 × 2.5 MVA), machine fleet inventory.

## 2. Energy Performance Indicators (EnPIs) (Page 2)
GreenPulse Facility #4 tracks four primary EnPIs:
1. **Plant-Level SEC (Specific Energy Consumption):** Total MWh / Total Metric Tons produced (Target: ≤ 0.452 MWh/ton).
2. **Compressor System Efficiency:** kW per 100 cfm delivered air (Target: ≤ 17.5 kW/100 cfm at 7.0 bar).
3. **Furnace Specific Melting Energy:** kWh per metric ton of alloy melted (Target: ≤ 560 kWh/ton).
4. **Thermal HVAC COP (Coefficient of Performance):** Net cooling kW / Electrical kW input (Target: ≥ 4.2).

## 3. Significant Energy Uses (SEUs) (Page 3)
Under Clause 6.3, assets accounting for > 5% of total plant energy consumption are designated as Significant Energy Uses (SEUs):
- **SEU 1:** Induction Furnace (FURN-01) - 34.2% of plant consumption.
- **SEU 2:** Compressed Air Fleet (COMP-01, COMP-02) - 22.8% of plant consumption.
- **SEU 3:** CNC Machining Bay (CNC-01, CNC-02) - 18.4% of plant consumption.
- **SEU 4:** Facility HVAC & Clean Room Chillers (HVAC-01) - 11.2% of plant consumption.

## 4. Normalization & Verification (Page 4)
When comparing monthly energy performance, raw energy consumption must be normalized using multi-variable regression:
$$\text{Normalized Energy} = \beta_0 + \beta_1 \cdot \text{Production} + \beta_2 \cdot \text{Cooling Degree Days} + \beta_3 \cdot \text{Shift Hours}$$
Residual differences between predicted and actual consumption constitute valid ISO 50001 energy savings.
