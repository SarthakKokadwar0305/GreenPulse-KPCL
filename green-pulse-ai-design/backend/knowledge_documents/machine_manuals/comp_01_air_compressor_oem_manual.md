# OEM Manual: Industrial Rotary Screw Air Compressor (COMP-01)
**Model:** Atlas Copco GA-160 VSD+ FF  
**Serial Number:** AC-2023-VSD-99812  
**Tag Name:** COMP-01 (Utility Compressed Air Plant)  
**Rated Power:** 160 kW (215 HP) Variable Speed Drive  
**Document Code:** OEM-MAN-AC-GA160-EN  
**Page:** 1 of 5

---

## 1. Technical Specifications
- **Operating Pressure Range:** 4.0 to 13.0 bar (e) [Factory Setpoint: 7.2 bar (e)]
- **Free Air Delivery (FAD):** 5.5 to 31.8 m³/min (194 to 1,123 cfm)
- **Specific Power Consumption (SEC):** 5.85 kW / (m³/min) at 7.0 bar
- **Motor Type:** Permanent Magnet iPM IE5 Super-Premium Efficiency Motor
- **Modbus TCP Address:** 192.168.10.15:502 (Unit ID 1)

## 2. Preventive Maintenance Schedule (Page 2)
- **Every 500 Hours:** Clean air intake filter element; verify condensate drain trap operation.
- **Every 2,000 Hours (Quarterly):** Lubricate motor bearings with synthetic Polyurea grease (25 grams per point); inspect oil separator differential pressure (Must be < 0.8 bar; if > 1.0 bar, replace separator element).
- **Every 4,000 Hours:** Oil sampling and replacement with Atlas Copco Roto-Xtend Duty Fluid.
- **Every 8,000 Hours:** Overhaul minimum pressure valve (MPV) and thermostatic expansion valve.

## 3. Critical Alarm Codes & Troubleshooting (Page 3)
### Alarm E-401: High Element Discharge Temperature (EDT)
- **Threshold:** Warning at 100°C; Automatic Emergency Trip at 110°C.
- **Root Causes:**
  1. Oil cooler fins clogged with airborne lint and metal dust.
  2. Low synthetic lubricant level in sump sight glass.
  3. Thermostatic valve bypass failure stuck in open recirculation mode.
- **Corrective Action:** Shut down machine, lock out electrical isolator, clean heat exchanger matrix with 3 bar dry nitrogen, and check thermostatic bypass spring tension.

### Alarm E-420: Elevated Vibration Severity (Drive End Bearing)
- **Threshold:** Normal < 2.8 mm/s RMS; Warning > 4.5 mm/s; Critical Trip > 7.1 mm/s (ISO 10816-3 Class II).
- **Root Cause:** Rotor unbalance or loose foundation jacking bolts.

## 4. Energy Conservation Optimization (Page 4)
- **Pressure Reduction Savings:** Lowering network delivery pressure by 1.0 bar reduces compressor electrical power draw by approximately 7.0%.
- **Artificial Demand Waste:** Unregulated air leaks across pneumatic fittings waste up to 25% of compressor output. Conduct ultrasonic leak detector sweep monthly.
