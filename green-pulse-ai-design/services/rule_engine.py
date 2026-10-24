"""
GreenPulse AI - Industrial Intelligence Layer: Industrial Rule Engine
Modular, rule-based reasoning engine that evaluates telemetry, ML forecasts, dynamic thresholds,
and business constraints against the 60 industrial domain rules in the Business Rule Registry.
"""
from typing import Dict, Any, List, Optional
import numpy as np

from services.config.rule_registry import BUSINESS_RULES
from services.config.industrial_constants import (
    PEAK_HOURS,
    OFF_PEAK_HOURS,
    PEAK_TARIFF_INR_PER_KWH,
    BASE_TARIFF_INR_PER_KWH,
    OFF_PEAK_TARIFF_INR_PER_KWH,
    CONTRACTED_MAX_DEMAND_KW,
    DEMAND_WARNING_THRESHOLD_KW,
    DEMAND_CRITICAL_THRESHOLD_KW,
    GRID_EMISSION_FACTOR_KG_PER_KWH,
)
from services.config.machine_config import MACHINES
from services.config.department_config import DEPARTMENTS


class IndustrialRuleEngine:
    """
    Evaluates plant telemetry and operational context against 60 modular industrial rules.
    Outputs fired rules, triggered actions, explanations, and financial/carbon impacts.
    """

    def __init__(self):
        self.rules = BUSINESS_RULES
        self.machines = MACHINES
        self.departments = DEPARTMENTS

    def evaluate_rules(
        self,
        machine_id: str,
        telemetry: Dict[str, Any],
        threshold_evals: List[Dict[str, Any]],
        ml_forecast: Optional[Dict[str, float]] = None,
        anomaly_result: Optional[Dict[str, Any]] = None,
        plant_context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Runs comprehensive rule evaluation for a specific machine and context.
        
        Returns:
            List of fired rule records with detailed triggers, reasoning, and savings estimates.
        """
        fired_rules: List[Dict[str, Any]] = []
        ctx = plant_context or {}
        machine_meta = self.machines.get(machine_id, {})
        dept_id = machine_meta.get("department_id", "DEPT-MACHINING")
        dept_meta = self.departments.get(dept_id, {})

        # Contextual variables
        hour = ctx.get("hour", telemetry.get("hour", 10))
        shift = ctx.get("shift", telemetry.get("shift", "A"))
        is_weekend = ctx.get("is_weekend", telemetry.get("is_weekend", False))
        total_plant_demand = ctx.get("total_plant_demand_kw", 195.0)
        solar_generation_kw = ctx.get("solar_generation_kw", 0.0)

        # Telemetry metrics
        power_kw = telemetry.get("power_kw", 0.0)
        temp_c = telemetry.get("temperature_c", telemetry.get("ambient_temp_c", 30.0))
        machine_state = telemetry.get("machine_state", "running")
        idle_duration = telemetry.get("idle_duration_minutes", 0)
        power_factor = telemetry.get("power_factor", 0.94)
        vibration_rms = telemetry.get("vibration_rms", 1.8)
        suction_pressure = telemetry.get("suction_pressure_bar", 1.5)
        discharge_temp = telemetry.get("discharge_temp_c", 72.0)
        parts_produced = telemetry.get("parts_produced_in_interval", 1)

        # Check threshold status
        threshold_violations = {
            t.get("metric"): t for t in threshold_evals if t.get("severity") in ["Warning", "Critical"]
        }

        # Anomaly status
        is_anom = anomaly_result.get("is_anomaly", False) if anomaly_result else False
        anom_score = anomaly_result.get("anomaly_score", 0.0) if anomaly_result else 0.0

        # Forecast metrics
        forecast_peak = ml_forecast.get("target_peak_kw", power_kw) if ml_forecast else power_kw
        forecast_cost = ml_forecast.get("target_cost_inr", 0.0) if ml_forecast else 0.0

        # ---------------------------------------------------------------------
        # RULE DISPATCH MATRIX (Testing all 60 rules across domain conditions)
        # ---------------------------------------------------------------------
        for rule in self.rules:
            rule_id = rule["rule_id"]
            fired = False
            condition_observed = ""
            confidence = 0.90

            # MODULE 1: ENERGY EFFICIENCY
            if rule_id == "RULE-EE-001":
                # Excessive Idle Power Cut-off
                idle_thresh = machine_meta.get("idle_warning_threshold_kw", 3.0)
                max_idle = machine_meta.get("max_allowable_idle_minutes", 20)
                if machine_state in ["idle", "standby"] and power_kw > idle_thresh and idle_duration >= max_idle:
                    fired = True
                    condition_observed = f"State is '{machine_state}', power {power_kw:.1f} kW > {idle_thresh:.1f} kW for {idle_duration} min (limit {max_idle} min)."

            elif rule_id == "RULE-EE-002":
                # Compressor Unloader Valve Diaphragm Internal Leakage
                if "COMP" in machine_id and machine_state in ["idle", "standby"] and power_kw > 10.5:
                    fired = True
                    condition_observed = f"Compressor in unloaded state drawing {power_kw:.1f} kW (expected baseline < 6.5 kW)."

            elif rule_id == "RULE-EE-003":
                # Compressed Air Header Pressure Setpoint Reduction
                header_p = telemetry.get("header_pressure_bar", 7.6)
                if "COMP" in machine_id and header_p > 7.3:
                    fired = True
                    condition_observed = f"Header pressure at {header_p:.2f} bar exceeds optimal 6.8 bar setpoint."

            elif rule_id == "RULE-EE-004":
                # Furnace Refractory Upper Door Perimeter Thermal Loss
                shell_temp = telemetry.get("shell_temp_c", 54.0)
                if machine_id == "FURN-01" and shell_temp > 50.0:
                    fired = True
                    condition_observed = f"Furnace exterior skin temp {shell_temp:.1f}°C > 50°C indicates refractory seal wear."

            elif rule_id == "RULE-EE-005":
                # Dry-Cycle Spindle Rotation Parasitic Draw
                spindle_rpm = telemetry.get("spindle_rpm", 0)
                if "CNC" in machine_id and spindle_rpm > 1000 and parts_produced == 0 and idle_duration > 15:
                    fired = True
                    condition_observed = f"Spindle rotating at {spindle_rpm} RPM with 0 parts produced for {idle_duration} min."

            elif rule_id == "RULE-EE-006":
                # Weekend Ghost Load Elimination
                if is_weekend and power_kw > (machine_meta.get("idle_baseline_power_kw", 1.0) * 1.8):
                    fired = True
                    condition_observed = f"Weekend power {power_kw:.1f} kW exceeds standby threshold on non-working day."

            elif rule_id == "RULE-EE-007":
                # Paint Booth Exhaust Blower Run-On Overrun
                if machine_id == "PAINT-01" and telemetry.get("curing_finished", False) and power_kw > 14.0:
                    fired = True
                    condition_observed = f"Paint booth drying cycle complete, exhaust blower drawing {power_kw:.1f} kW."

            elif rule_id == "RULE-EE-008":
                # Cooling Water Over-Circulation Throttling
                ret_temp = telemetry.get("cooling_return_temp_c", 22.5)
                if machine_id == "PUMP-01" and ret_temp < 24.0:
                    fired = True
                    condition_observed = f"Coolant return temp {ret_temp:.1f}°C is too cool (< 24°C), indicating excess pumping volume."

            elif rule_id == "RULE-EE-009":
                # HVAC Economizer Free-Cooling Opportunity
                amb_temp = telemetry.get("ambient_temp_c", 18.0)
                if machine_id == "HVAC-01" and amb_temp < 19.0 and power_kw > 7.5:
                    fired = True
                    condition_observed = f"Ambient temp {amb_temp:.1f}°C is suitable for free air-side economizer cooling."

            elif rule_id == "RULE-EE-010":
                # Transformer No-Load Standby De-energization
                sub_load = ctx.get("substation_bus_b_load_pct", 4.2)
                if sub_load < 5.0 and ctx.get("bus_b_idle_hours", 5) > 4:
                    fired = True
                    condition_observed = f"Substation Bus B load at {sub_load:.1f}% for > 4 hours incurring core excitation losses."

            # MODULE 2: TARIFF OPTIMIZATION
            elif rule_id == "RULE-TO-011":
                # Heat Furnace Peak Tariff Window Delay
                if machine_id == "FURN-01" and hour in [9, 17] and telemetry.get("batch_queued", True):
                    fired = True
                    condition_observed = f"Current hour {hour}:00 approaches Peak Tariff band ({PEAK_HOURS}) where energy costs ₹10.368/kWh."

            elif rule_id == "RULE-TO-012":
                # Chilled Water Thermal Storage Pre-Cooling
                chw_temp = telemetry.get("chilled_water_temp_c", 9.2)
                if machine_id == "HVAC-01" and hour in [8, 9, 16, 17] and chw_temp > 8.0:
                    fired = True
                    condition_observed = f"Pre-cooling opportunity in hour {hour}:00 before peak tariff window."

            elif rule_id == "RULE-TO-013":
                # Shift Batch Annealing to Off-Peak Shift C
                if machine_id == "FURN-01" and shift in ["A", "B"] and telemetry.get("flexible_batch_queue", True):
                    fired = True
                    condition_observed = f"Flexible batch queued during Shift {shift}; transferring to Shift C saves ₹5.168/kWh."

            elif rule_id == "RULE-TO-014":
                # Peak Tariff Machine Startup Interlock
                if hour in PEAK_HOURS and machine_state in ["starting", "off"] and telemetry.get("start_requested", False):
                    fired = True
                    condition_observed = f"Machine startup requested during peak tariff hour {hour}:00."

            elif rule_id == "RULE-TO-015":
                # Compressor Lead/Lag Swap Prior to Peak Tariff
                if machine_id == "COMP-01" and hour in [9, 17] and telemetry.get("is_lead", True):
                    fired = True
                    condition_observed = f"Fixed-speed COMP-01 is lead entering peak tariff window; VFD COMP-02 should lead."

            elif rule_id == "RULE-TO-016":
                # Peak Tariff HVAC Setpoint Relaxation
                zone_temp = telemetry.get("zone_temp_c", 22.0)
                if machine_id == "HVAC-01" and hour in PEAK_HOURS and zone_temp < 23.5:
                    fired = True
                    condition_observed = f"Peak tariff active; zone temperature {zone_temp:.1f}°C can be relaxed to 24.0°C."

            elif rule_id == "RULE-TO-017":
                # Automated Solar Self-Consumption Alignment
                if hour in [11, 12, 13, 14] and solar_generation_kw > 50.0 and total_plant_demand < (solar_generation_kw + 20.0):
                    fired = True
                    condition_observed = f"Solar generation at {solar_generation_kw:.1f} kW exceeds local demand; align heavy batches."

            elif rule_id == "RULE-TO-018":
                # Avoid Peak Window Compressed Air Tank Bleed Down
                drain_open = telemetry.get("drain_valve_open_sec", 0)
                if "COMP" in machine_id and hour in PEAK_HOURS and drain_open > 30:
                    fired = True
                    condition_observed = f"Condensate drain open for {drain_open}s during peak tariff hour {hour}:00."

            elif rule_id == "RULE-TO-019":
                # Non-Critical Coolant Filtration Backwash Deferral
                if machine_id == "PUMP-01" and hour in PEAK_HOURS and telemetry.get("backwash_requested", False):
                    fired = True
                    condition_observed = f"Filter backwash requested during peak hour {hour}:00 with safe differential pressure."

            elif rule_id == "RULE-TO-020":
                # Shift C Intensive Battery / Storage Recharge
                storage_soc = ctx.get("bess_soc_pct", 75.0)
                if hour in OFF_PEAK_HOURS and storage_soc < 90.0:
                    fired = True
                    condition_observed = f"Off-peak tariff active (₹5.20/kWh) with battery SOC at {storage_soc:.1f}%."

            # MODULE 3: EQUIPMENT HEALTH & RELIABILITY
            elif rule_id == "RULE-EH-021":
                # Pump Suction Strainer Blockage & Cavitation
                if machine_id == "PUMP-01" and (suction_pressure < 1.1 or vibration_rms > 3.2):
                    fired = True
                    condition_observed = f"Suction pressure {suction_pressure:.2f} bar (< 1.1 bar) and vibration {vibration_rms:.2f} mm/s indicate cavitation."

            elif rule_id == "RULE-EH-022":
                # Compressor Discharge High Temperature
                if "COMP" in machine_id and discharge_temp > 88.0:
                    fired = True
                    condition_observed = f"Compressor discharge temp {discharge_temp:.1f}°C exceeds safe oil thermal threshold (88°C)."

            elif rule_id == "RULE-EH-023":
                # CNC Spindle Bearing Micro-Vibration Degradation
                spindle_vib = telemetry.get("spindle_vibration_g", 1.2)
                if "CNC" in machine_id and (spindle_vib > 1.7 or (is_anom and "active_power_kw" in threshold_violations)):
                    fired = True
                    condition_observed = f"Spindle vibration {spindle_vib:.2f}g with elevated friction power draw."

            elif rule_id == "RULE-EH-024":
                # Motor 3-Phase Current Imbalance
                imbalance = telemetry.get("phase_current_unbalance_pct", 1.8)
                if imbalance > 2.8:
                    fired = True
                    condition_observed = f"Phase current unbalance {imbalance:.2f}% exceeds NEMA 2.5% derating threshold."

            elif rule_id == "RULE-EH-025":
                # Excessive Motor Start/Stop Cycling Frequency
                starts_hr = telemetry.get("starts_in_last_hour", 1)
                max_starts = machine_meta.get("max_starts_per_hour", 4)
                if starts_hr > max_starts:
                    fired = True
                    condition_observed = f"Motor started {starts_hr} times in last hour (maximum allowed: {max_starts})."

            elif rule_id == "RULE-EH-026":
                # Furnace Heating Element Bank Resistance Drift
                element_var = telemetry.get("phase_impedance_variance_pct", 3.2)
                if machine_id == "FURN-01" and element_var > 7.0:
                    fired = True
                    condition_observed = f"Heating bank phase resistance drift {element_var:.1f}% indicates micro-crack in Zone 2 element."

            elif rule_id == "RULE-EH-027":
                # HVAC Chiller Condenser Tube Scaling
                appr_temp = telemetry.get("condenser_approach_temp_c", 2.8)
                if machine_id == "HVAC-01" and appr_temp > 4.2:
                    fired = True
                    condition_observed = f"Condenser approach temp {appr_temp:.1f}°C exceeds clean baseline (2.0°C)."

            elif rule_id == "RULE-EH-028":
                # Paint Booth HEPA Exhaust Filter High Pressure Drop
                dp_filter = telemetry.get("filter_dp_pa", 280)
                if machine_id == "PAINT-01" and dp_filter > 340:
                    fired = True
                    condition_observed = f"Exhaust filter differential pressure {dp_filter} Pa exceeds 340 Pa changeover limit."

            elif rule_id == "RULE-EH-029":
                # Coolant Pump Mechanical Seal Leakage
                if machine_id == "PUMP-01" and telemetry.get("seal_quench_pressure_spike", False):
                    fired = True
                    condition_observed = "Seal quench chamber pressure spike detected; seal face ingress imminent."

            elif rule_id == "RULE-EH-030":
                # VFD Inverter DC Bus Harmonic Ripple Warning
                ripple_pct = telemetry.get("dc_bus_voltage_ripple_pct", 2.1)
                if ripple_pct > 4.2:
                    fired = True
                    condition_observed = f"DC bus voltage ripple {ripple_pct:.1f}% indicates capacitor bank aging."

            # MODULE 4: DEMAND MANAGEMENT
            elif rule_id == "RULE-DM-031":
                # Contract Demand Warning (85%)
                if total_plant_demand >= DEMAND_WARNING_THRESHOLD_KW:
                    fired = True
                    condition_observed = f"Plant total demand {total_plant_demand:.1f} kW exceeds 85% contract threshold ({DEMAND_WARNING_THRESHOLD_KW:.1f} kW)."

            elif rule_id == "RULE-DM-032":
                # Contract Demand Critical (95%)
                if total_plant_demand >= DEMAND_CRITICAL_THRESHOLD_KW:
                    fired = True
                    condition_observed = f"Plant total demand {total_plant_demand:.1f} kW exceeds 95% contract threshold ({DEMAND_CRITICAL_THRESHOLD_KW:.1f} kW)."

            elif rule_id == "RULE-DM-033":
                # Power Factor Penalty Exposure (< 0.90)
                if power_factor < 0.90 and power_kw > 10.0:
                    fired = True
                    condition_observed = f"Power factor {power_factor:.2f} is below utility penalty threshold (0.90)."

            elif rule_id == "RULE-DM-034":
                # Excessive Apparent Power (kVA) Reactive Drift
                kva = telemetry.get("apparent_power_kva", power_kw * 1.1)
                if power_kw > 5.0 and (kva / power_kw) > 1.18:
                    fired = True
                    condition_observed = f"kVA/kW ratio {kva / power_kw:.2f} indicates excessive reactive current."

            elif rule_id == "RULE-DM-035":
                # THD-V Voltage Pollution
                thd_v = telemetry.get("thd_voltage_pct", 3.2)
                if thd_v > 4.8:
                    fired = True
                    condition_observed = f"Voltage THD {thd_v:.1f}% exceeds IEEE-519 5.0% threshold."

            elif rule_id == "RULE-DM-036":
                # Simultaneous Cold Startup Interlock
                if machine_state == "starting" and ctx.get("simultaneous_heavy_start", False):
                    fired = True
                    condition_observed = "Simultaneous high-power machine startup detected."

            elif rule_id == "RULE-DM-037":
                # Substation Main Busbar Voltage Sag (< 385V)
                v_line = telemetry.get("line_voltage_v", 412.0)
                if v_line < 388.0:
                    fired = True
                    condition_observed = f"Busbar line voltage {v_line:.1f}V is below 388V nominal threshold."

            elif rule_id == "RULE-DM-038":
                # Feeder Cable Thermal Overload
                cable_load = telemetry.get("feeder_cable_load_pct", 72.0)
                if cable_load > 88.0:
                    fired = True
                    condition_observed = f"Feeder cable load {cable_load:.1f}% approaches thermal ampacity limit (90%)."

            elif rule_id == "RULE-DM-039":
                # Peak Demand Forecast Breach
                if forecast_peak > (machine_meta.get("rated_power_kw", 25.0) * 0.92):
                    fired = True
                    condition_observed = f"ML forecast predicts peak load {forecast_peak:.1f} kW nearing rated capacity."

            elif rule_id == "RULE-DM-040":
                # Leading Power Factor Over-Correction
                if telemetry.get("pf_leading", False) and power_factor < 0.96:
                    fired = True
                    condition_observed = f"Leading power factor {power_factor:.2f} risks over-voltage resonance."

            # MODULE 5: CARBON & SUSTAINABILITY
            elif rule_id == "RULE-CS-041":
                # High Grid Carbon Intensity Dispatch Throttling
                grid_c = ctx.get("grid_carbon_factor", GRID_EMISSION_FACTOR_KG_PER_KWH)
                if grid_c > 0.88 and telemetry.get("is_non_critical", False):
                    fired = True
                    condition_observed = f"Grid carbon intensity {grid_c:.3f} kg/kWh is exceptionally high."

            elif rule_id == "RULE-CS-042":
                # Hourly Carbon Emission Budget Exceedance
                hourly_carbon = ctx.get("hourly_plant_carbon_kg", 185.0)
                if hourly_carbon > 220.0:
                    fired = True
                    condition_observed = f"Hourly carbon {hourly_carbon:.1f} kg exceeds 220 kg ESG ceiling."

            elif rule_id == "RULE-CS-043":
                # Specific Carbon Intensity per Finished Part
                sec_c = telemetry.get("carbon_kg_per_part", 0.45)
                if sec_c > 0.65:
                    fired = True
                    condition_observed = f"Carbon intensity {sec_c:.3f} kg CO2e/part exceeds 0.50 kg benchmark."

            elif rule_id == "RULE-CS-044":
                # Rooftop Solar Curtailment Prevention
                if ctx.get("solar_curtailed", False):
                    fired = True
                    condition_observed = "Solar generation being curtailed while factory drawing grid power."

            elif rule_id == "RULE-CS-045":
                # Diesel Generator Non-Emergency Run Avoidance
                if ctx.get("dg_running", False) and ctx.get("grid_healthy", True):
                    fired = True
                    condition_observed = "Diesel generator active while utility grid is fully energized."

            elif rule_id == "RULE-CS-046":
                # Furnace Excess Air Ratio Combustion Optimization
                flue_o2 = telemetry.get("flue_o2_pct", 3.2)
                if machine_id == "FURN-01" and flue_o2 > 5.5:
                    fired = True
                    condition_observed = f"Flue gas O2 at {flue_o2:.1f}% indicates excess air cooling flame."

            elif rule_id == "RULE-CS-047":
                # Chiller Refrigerant Micro-Leak Detection
                if machine_id == "HVAC-01" and telemetry.get("refrigerant_subcooling_drop", False):
                    fired = True
                    condition_observed = "Refrigerant subcooling drop detected; micro-leak in progress."

            elif rule_id == "RULE-CS-048":
                # Compressed Air Fugitive Leak Carbon Penalty
                leak_pct = telemetry.get("pneumatic_leak_load_pct", 22.0)
                if "COMP" in machine_id and leak_pct > 25.0:
                    fired = True
                    condition_observed = f"Pneumatic distribution leak baseline is {leak_pct:.1f}% of compressor capacity."

            elif rule_id == "RULE-CS-049":
                # Cooling Tower Fan VFD Cycling
                wet_bulb_m = telemetry.get("wet_bulb_margin_c", 3.0)
                if wet_bulb_m > 4.5 and telemetry.get("tower_fan_pct", 100) == 100:
                    fired = True
                    condition_observed = f"Favorable wet-bulb margin ({wet_bulb_m:.1f}°C); fan can be modulated to 65%."

            elif rule_id == "RULE-CS-050":
                # ISO 50001 EnPI Deviation
                cusum_dev = ctx.get("cusum_energy_deviation_pct", 3.8)
                if cusum_dev > 5.0:
                    fired = True
                    condition_observed = f"CUSUM energy performance indicator deviation at {cusum_dev:.1f}%."

            # MODULE 6: PRODUCTION & OPERATIONAL ALIGNMENT
            elif rule_id == "RULE-PA-051":
                # SEC Deterioration Warning
                sec_val = telemetry.get("kwh_per_part", 0.52)
                if sec_val > 0.75:
                    fired = True
                    condition_observed = f"Specific energy consumption {sec_val:.3f} kWh/part exceeds 0.55 benchmark (+36%)."

            elif rule_id == "RULE-PA-052":
                # Energy Consumption with Zero Production
                if power_kw > (machine_meta.get("rated_power_kw", 20.0) * 0.35) and parts_produced == 0 and idle_duration > 30:
                    fired = True
                    condition_observed = f"Drawing {power_kw:.1f} kW for {idle_duration} min with zero finished parts."

            elif rule_id == "RULE-PA-053":
                # Shift Changeover Energy Coasting
                mins_to_change = ctx.get("minutes_to_shift_change", 45)
                if mins_to_change <= 15 and machine_state == "idle":
                    fired = True
                    condition_observed = f"Machine idling {mins_to_change} min before scheduled shift changeover."

            elif rule_id == "RULE-PA-054":
                # Furnace Partial Load Batch Under-utilization
                batch_kg = telemetry.get("batch_load_kg", 450.0)
                if machine_id == "FURN-01" and batch_kg < 250.0 and machine_state == "running":
                    fired = True
                    condition_observed = f"Furnace running batch weight {batch_kg:.1f} kg (< 50% hearth capacity)."

            elif rule_id == "RULE-PA-055":
                # Scrap Rate Surge Energy Multiplier Warning
                scrap_pct = telemetry.get("scrap_rate_pct", 1.5)
                if scrap_pct > 5.5:
                    fired = True
                    condition_observed = f"Scrap rate surge {scrap_pct:.1f}% wastes embedded electrical energy."

            elif rule_id == "RULE-PA-056":
                # Conveyor Running Empty Parasitic Load
                if telemetry.get("conveyor_empty_running", False):
                    fired = True
                    condition_observed = "Parts conveyor operating empty for > 10 minutes."

            elif rule_id == "RULE-PA-057":
                # Sub-Optimal Cutting Tool Feed Rate Drag
                if "CNC" in machine_id and telemetry.get("spindle_cutting_overtorque", False):
                    fired = True
                    condition_observed = "Cutting tool spindle torque 25% above nominal; inserts dull."

            elif rule_id == "RULE-PA-058":
                # Paint Booth Temperature Overshoot on Pre-Heat
                plenum_temp = telemetry.get("drying_plenum_temp_c", 65.0)
                if machine_id == "PAINT-01" and plenum_temp > 74.0:
                    fired = True
                    condition_observed = f"Plenum temp {plenum_temp:.1f}°C overshoots 68°C curing setpoint."

            elif rule_id == "RULE-PA-059":
                # Compressor Running During Break
                if "COMP" in machine_id and ctx.get("break_time_active", False) and power_kw > 20.0:
                    fired = True
                    condition_observed = f"Compressor drawing {power_kw:.1f} kW during scheduled plant meal break."

            elif rule_id == "RULE-PA-060":
                # Bottleneck Production Pacing Alignment
                if "CNC" in machine_id and telemetry.get("buffer_queue_overflow", False):
                    fired = True
                    condition_observed = "Downstream bottleneck buffer queue full (> 90%); pacing required."

            # If rule fired, record structured trigger
            if fired:
                tariff_rate = PEAK_TARIFF_INR_PER_KWH if hour in PEAK_HOURS else BASE_TARIFF_INR_PER_KWH
                kwh_hr = rule.get("typical_kwh_reduction_hr", 10.0)
                inr_hr = rule.get("typical_savings_inr_hr", kwh_hr * tariff_rate)
                carbon_hr = round(kwh_hr * GRID_EMISSION_FACTOR_KG_PER_KWH, 2)

                fired_rules.append({
                    "rule_id": rule_id,
                    "rule_name": rule["name"],
                    "module": rule["module"],
                    "category": rule["category"],
                    "priority": rule["priority"],
                    "machine_id": machine_id,
                    "machine_name": machine_meta.get("name", machine_id),
                    "department": dept_meta.get("name", dept_id),
                    "condition_observed": condition_observed,
                    "condition_definition": rule["condition_desc"],
                    "reason": rule["reason"],
                    "suggested_action": rule["action"],
                    "operational_impact": rule["impact"],
                    "confidence": confidence,
                    "expected_savings": {
                        "hourly_inr": inr_hr,
                        "hourly_kwh": kwh_hr,
                        "hourly_carbon_kg": carbon_hr,
                    },
                })

        return fired_rules
