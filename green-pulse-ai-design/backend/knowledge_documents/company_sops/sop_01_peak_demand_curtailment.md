# SOP-ENG-04: Peak Demand Management & Load Curtailment Protocol
**Document ID:** GP-SOP-ENG-04-REV3  
**Effective Date:** 15-January-2026  
**Plant Facility:** GreenPulse Manufacturing Facility #4 (FAC-IND-PUN-004)  
**Approved By:** VP Operations & Chief Energy Auditor  
**Classification:** Internal Standard Operating Procedure  
**Page:** 1 of 4

---

## 1. Objective and Scope
This Standard Operating Procedure defines mandatory engineering steps to monitor, control, and curtail electrical maximum demand (kW/kVA) to prevent exceeding the sanctioned Contracted Maximum Demand of 2,500 kW at the 33 kV incoming HT substation feeder.

## 2. Trigger Conditions
- **Stage 1 (Advisory Alert - 85% CMD / 2,125 kW):** SCADA monitoring flags demand rise exceeding 15-minute sliding average. Energy Manager receives automated SMS/Slack alert.
- **Stage 2 (Warning Alert - 92% CMD / 2,300 kW):** Audible buzzer activated on main shopfloor control desk. Supervisory load-shedding sequence initiates.
- **Stage 3 (Critical Action - 96% CMD / 2,400 kW):** Automated interlocks trip non-critical utility loads. Immediate manual intervention required within 3 minutes.

## 3. Mandatory Curtailment Sequence (Page 2)
### Section 3.1: Non-Critical Utility Shedding (Stage 2)
1. Switch HVAC Chiller Units (HVAC-01) from active chilling to thermal economizer fan mode (reduces load by 45 kW).
2. De-energize auxiliary dust extraction blowers on Bay 3 assembly line.
3. Inhibit charging of electric forklift fleet battery stations.

### Section 3.2: Machine Fleet Interlocks (Stage 3)
1. **Air Compressors (COMP-01 / COMP-02):** Unload standby compressor COMP-02 immediately if system receiver tank pressure > 6.8 bar. Run lead compressor COMP-01 at modulation speed 75%.
2. **Induction Furnace (FURN-01):** Ramp down thyristor heating power from 650 kW to 320 kW holding power for a maximum of 25 minutes. Do not dump molten heat.
3. **CNC Bay (CNC-01 / CNC-02):** Complete existing machining cycle block; inhibit automatic billet loader for subsequent parts.

## 4. Reset & Normalization Procedure (Page 3)
Once the 15-minute sliding demand curve drops below 1,950 kW (78% CMD) for two consecutive billing intervals:
1. Re-arm furnace ramp rate to normal production schedule.
2. Resume auxiliary blowers and HVAC chillers.
3. Log incident in GreenPulse Audit Log with root cause attribution (e.g., simultaneous motor start, grid frequency dip).

## 5. Penalties for Non-Compliance (Page 4)
Exceeding CMD of 2,500 kW attracts DISCOM demand penalty charges at ₹450 per kVA for the entire billing month plus 150% peak tariff surcharges on excess units. All operators must execute this SOP without delay.
