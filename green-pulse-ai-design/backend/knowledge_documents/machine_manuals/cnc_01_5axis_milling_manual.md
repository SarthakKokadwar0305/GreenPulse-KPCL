# OEM Manual: 5-Axis Heavy Machining Center (CNC-01)
**Machine Model:** DMG MORI DMU 95 monoBLOCK  
**Tag Name:** CNC-01 (Precision Bay 1)  
**Spindle Power:** 35 kW / 40 kW (40% DC) | 20,000 RPM speedMaster  
**Document Ref:** OEM-MAN-DMG-DMU95-REV4  
**Page:** 1 of 4

---

## 1. Electrical & Thermal Specifications
- **Operating Voltage:** 415 V AC ± 10%, 3-Phase, 50 Hz
- **Total Connected Load:** 58 kVA (Peak Spindle + Servo Drives + High-Pressure Coolant Pump)
- **Spindle Motor Bearing Cooling:** Chilled glycol closed-loop refrigeration unit (Set to 20°C ± 1°C).
- **PLC Controller:** Siemens SINUMERIK ONE with integrated OPC-UA server at port 4840.

## 2. Machine Health & Vibration Limits (Page 2)
- **Spindle Vibration RMS Limits:**
  - Optimal condition: < 1.2 mm/s
  - Maintenance Warning: 2.2 mm/s
  - Critical Stop: 4.5 mm/s (To prevent catastrophic ceramic hybrid spindle bearing failure).
- **Spindle Thermal Drift Warning:** Bearing temperature must not exceed 48°C during continuous 14,000 RPM roughing cuts.

## 3. High Energy Consumption Root Causes (Page 3)
When CNC-01 energy draw exceeds nominal baselines (> 22.5 kWh/hr during standard billet cycles):
1. **Dull/Chipped Tool Inserts:** Tool wear increases spindle cutting torque by 30-45%, forcing higher drive current draw.
2. **Coolant Filtration Clog:** 70-bar through-spindle coolant pump draws excessive current when 10-micron cartridge filter differential pressure exceeds 4.5 bar.
3. **Axis Guide Friction:** Ball screw pre-load degradation or inadequate central way lube pressure.

## 4. Operator Interventions & Safety (Page 4)
- Operators must check lubrication reservoir sight glass at start of shift.
- Never override spindle temperature warning interlocks.
- Tool replacement alerts must be executed within 3 workpiece cycles.
