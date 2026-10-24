"""
GreenPulse AI - Industrial Intelligence Layer: Intelligent Alert Generation Engine
Combines ML forecasts, Isolation Forest anomaly telemetry, dynamic thresholds,
contractual utility limits, tariff schedules, and production context.
Never relies on naive single-sensor threshold checks alone.
"""
import uuid
import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import numpy as np

from services.config.industrial_constants import (
    CONTRACTED_MAX_DEMAND_KW,
    DEMAND_WARNING_THRESHOLD_KW,
    DEMAND_CRITICAL_THRESHOLD_KW,
    PEAK_HOURS,
    PEAK_TARIFF_INR_PER_KWH,
    BASE_TARIFF_INR_PER_KWH,
    MINIMUM_ACCEPTABLE_POWER_FACTOR,
    GRID_EMISSION_FACTOR_KG_PER_KWH,
)
from services.config.machine_config import MACHINES
from services.config.department_config import DEPARTMENTS


class AlertGenerationEngine:
    """
    Industrial Alert Synthesis Engine combining model predictions, dynamic thresholds,
    electrical power quality, and business rules to generate actionable alerts.
    """

    def __init__(self):
        self.machines = MACHINES
        self.departments = DEPARTMENTS

    def synthesize_alerts(
        self,
        machine_id: str,
        telemetry: Dict[str, Any],
        threshold_evals: List[Dict[str, Any]],
        ml_forecast: Optional[Dict[str, float]] = None,
        anomaly_result: Optional[Dict[str, Any]] = None,
        plant_context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Synthesizes composite multi-source industrial alerts.
        
        Args:
            machine_id: Target machine identifier (e.g. COMP-01, FURN-01)
            telemetry: Current sensor readings (power_kw, temp_c, voltage, pf, etc.)
            threshold_evals: List of threshold evaluation objects from AdaptiveThresholdEngine
            ml_forecast: Predictions from Phase 3A models (target_energy, target_cost, target_peak)
            anomaly_result: Output from Isolation Forest (decision_function, anomaly_score, is_anomaly)
            plant_context: Plant-wide variables (total_plant_demand_kw, hour, shift, is_weekend, solar_kw)
            
        Returns:
            List of structured industrial alert dictionaries ready for JSON serialization.
        """
        alerts: List[Dict[str, Any]] = []
        machine_meta = self.machines.get(machine_id, {})
        dept_id = machine_meta.get("department_id", "DEPT-MACHINING")
        dept_meta = self.departments.get(dept_id, {})

        now_str = datetime.now(timezone.utc).isoformat()
        plant_ctx = plant_context or {}
        hour = plant_ctx.get("hour", 10)
        shift = plant_ctx.get("shift", "A")
        is_weekend = plant_ctx.get("is_weekend", False)
        total_plant_demand = plant_ctx.get("total_plant_demand_kw", 185.0)

        # ---------------------------------------------------------------------
        # 1. CONTRACTUAL MAXIMUM DEMAND ALERTS
        # ---------------------------------------------------------------------
        forecast_peak = ml_forecast.get("target_peak_kw", 0.0) if ml_forecast else 0.0
        predicted_total_demand = total_plant_demand + (forecast_peak * 0.25)

        if total_plant_demand >= DEMAND_CRITICAL_THRESHOLD_KW or predicted_total_demand >= DEMAND_CRITICAL_THRESHOLD_KW:
            alerts.append(self._build_alert(
                alert_type="CONTRACT_DEMAND_CRITICAL",
                machine_id=machine_id,
                machine_name=machine_meta.get("name", machine_id),
                department=dept_meta.get("name", dept_id),
                severity="Emergency",
                priority="Critical",
                category="Contractual Demand Protection",
                reason=f"Total plant active demand ({total_plant_demand:.1f} kW) has breached 95% of contract limit ({CONTRACTED_MAX_DEMAND_KW:.1f} kW).",
                evidence=[
                    {"metric": "Plant Active Demand", "measured": f"{total_plant_demand:.1f} kW", "threshold": f"{DEMAND_CRITICAL_THRESHOLD_KW:.1f} kW", "deviation": f"+{total_plant_demand - DEMAND_CRITICAL_THRESHOLD_KW:.1f} kW"},
                    {"metric": "Contract Maximum Demand", "value": f"{CONTRACTED_MAX_DEMAND_KW:.1f} kW", "status": "Penalized @ ₹450/kVA surge"},
                    {"metric": "Machine Active Power", "measured": f"{telemetry.get('power_kw', 0.0):.1f} kW", "rated": f"{machine_meta.get('rated_power_kw', 0.0):.1f} kW"},
                ],
                confidence=0.98,
                suggested_action=f"Execute Level-1 automated load shed: temporarily unload {machine_meta.get('short_name', machine_id)} or defer secondary heater bank.",
                business_impact="Avoids permanent 15-minute MDI penalty reset on monthly utility bill.",
                financial_impact=18500.0,  # Estimated MDI penalty exposure
                timestamp=now_str,
            ))
        elif total_plant_demand >= DEMAND_WARNING_THRESHOLD_KW:
            alerts.append(self._build_alert(
                alert_type="CONTRACT_DEMAND_APPROACHING",
                machine_id=machine_id,
                machine_name=machine_meta.get("name", machine_id),
                department=dept_meta.get("name", dept_id),
                severity="Warning",
                priority="High",
                category="Contractual Demand Protection",
                reason=f"Plant demand ({total_plant_demand:.1f} kW) is within 15% of contract limit ({CONTRACTED_MAX_DEMAND_KW:.1f} kW).",
                evidence=[
                    {"metric": "Plant Demand", "measured": f"{total_plant_demand:.1f} kW", "threshold": f"{DEMAND_WARNING_THRESHOLD_KW:.1f} kW"},
                    {"metric": "Safety Headroom Remaining", "value": f"{CONTRACTED_MAX_DEMAND_KW - total_plant_demand:.1f} kW"},
                ],
                confidence=0.94,
                suggested_action="Inhibit simultaneous heavy motor restarts and postpone non-critical batch heating.",
                business_impact="Preserves operational buffer against utility demand penalties.",
                financial_impact=4500.0,
                timestamp=now_str,
            ))

        # ---------------------------------------------------------------------
        # 2. ISOLATION FOREST ANOMALY + TELEMETRY DIVERGENCE ALERTS
        # ---------------------------------------------------------------------
        if anomaly_result and anomaly_result.get("is_anomaly", False):
            dec_func = anomaly_result.get("decision_function", -0.05)
            anom_score = anomaly_result.get("anomaly_score", 0.85)

            alerts.append(self._build_alert(
                alert_type="ML_TELEMETRY_ANOMALY_DETECTED",
                machine_id=machine_id,
                machine_name=machine_meta.get("name", machine_id),
                department=dept_meta.get("name", dept_id),
                severity="Critical" if anom_score > 0.85 else "Warning",
                priority="High",
                category="Equipment Telemetry Anomaly",
                reason=f"Isolation Forest identified abnormal multivariable operational excursion (score: {anom_score:.2f}, decision: {dec_func:.3f}).",
                evidence=[
                    {"metric": "Anomaly Model Score", "value": f"{anom_score:.3f}", "threshold": "> 0.70", "status": "Abnormal Excursion"},
                    {"metric": "Decision Function Margin", "value": f"{dec_func:.4f}", "normal_range": "> 0.00"},
                    {"metric": "Power Lag-1 Divergence", "value": f"{telemetry.get('power_kw', 0.0) - telemetry.get('power_lag_1', telemetry.get('power_kw', 0.0)):.1f} kW delta"},
                    {"metric": "Current Power vs Rated", "measured": f"{telemetry.get('power_kw', 0.0):.1f} kW", "rated": f"{machine_meta.get('rated_power_kw', 0.0):.1f} kW"},
                ],
                confidence=round(min(0.96, 0.75 + (anom_score * 0.22)), 4),
                suggested_action="Dispatch maintenance technician to inspect machine mechanical loading, bearing temperature, and fluid pressures.",
                business_impact="Detects impending component degradation prior to unexpected catastrophic breakdown.",
                financial_impact=12400.0,
                timestamp=now_str,
            ))

        # ---------------------------------------------------------------------
        # 3. UNEXPECTED IDLE ENERGY & PARASITIC STANDBY ALERTS
        # ---------------------------------------------------------------------
        current_power = telemetry.get("power_kw", 0.0)
        machine_state = telemetry.get("machine_state", "running")
        idle_threshold = machine_meta.get("idle_warning_threshold_kw", 3.0)
        idle_minutes = telemetry.get("idle_duration_minutes", 0)

        if machine_state in ["idle", "standby"] and current_power > idle_threshold:
            excess_kw = current_power - machine_meta.get("idle_baseline_power_kw", 1.0)
            alerts.append(self._build_alert(
                alert_type="UNEXPECTED_IDLE_ENERGY",
                machine_id=machine_id,
                machine_name=machine_meta.get("name", machine_id),
                department=dept_meta.get("name", dept_id),
                severity="Warning",
                priority="Medium",
                category="Energy Waste",
                reason=f"Machine in idle state drawing {current_power:.1f} kW, exceeding normal idle baseline of {idle_threshold:.1f} kW.",
                evidence=[
                    {"metric": "Idle Active Power", "measured": f"{current_power:.1f} kW", "expected_baseline": f"{machine_meta.get('idle_baseline_power_kw', 1.0):.1f} kW", "excess": f"+{excess_kw:.1f} kW"},
                    {"metric": "Idle Duration", "duration": f"{idle_minutes} minutes"},
                    {"metric": "Tariff Band", "tariff": f"₹{PEAK_TARIFF_INR_PER_KWH if hour in PEAK_HOURS else BASE_TARIFF_INR_PER_KWH}/kWh"},
                ],
                confidence=0.92,
                suggested_action="Verify auxiliary motor shut-off or inspect pneumatic unloader valve for internal leakage.",
                business_impact="Eliminates unrecoverable energy expenditure during production pauses.",
                financial_impact=round(excess_kw * 8.5 * 1.5, 2),  # ₹/hr rate
                timestamp=now_str,
            ))

        # ---------------------------------------------------------------------
        # 4. WEEKEND / OFF-SHIFT STANDBY OPERATION ANOMALY
        # ---------------------------------------------------------------------
        if is_weekend and current_power > (machine_meta.get("idle_baseline_power_kw", 1.0) * 1.5):
            alerts.append(self._build_alert(
                alert_type="WEEKEND_OPERATION_ANOMALY",
                machine_id=machine_id,
                machine_name=machine_meta.get("name", machine_id),
                department=dept_meta.get("name", dept_id),
                severity="Warning",
                priority="High",
                category="Standby Waste",
                reason=f"High active power draw ({current_power:.1f} kW) detected during non-scheduled weekend maintenance shutdown.",
                evidence=[
                    {"metric": "Measured Weekend Power", "measured": f"{current_power:.1f} kW", "expected": f"<{machine_meta.get('idle_baseline_power_kw', 1.0):.1f} kW"},
                    {"metric": "Calendar State", "is_weekend": True, "production_scheduled": False},
                ],
                confidence=0.95,
                suggested_action="Isolate local machine power disconnect switch or trigger central PLC de-energize routine.",
                business_impact="Eliminates weekend ghost power losses across 48 non-productive hours.",
                financial_impact=round(current_power * 7.20 * 24.0, 2),
                timestamp=now_str,
            ))

        # ---------------------------------------------------------------------
        # 5. DYNAMIC THRESHOLD EXCURSION ALERTS
        # ---------------------------------------------------------------------
        for teval in threshold_evals:
            if teval.get("severity") in ["Warning", "Critical"]:
                sev = teval.get("severity")
                prio = "High" if sev == "Critical" else "Medium"
                alerts.append(self._build_alert(
                    alert_type=f"THRESHOLD_{teval.get('metric', 'PARAM').upper()}_{sev.upper()}",
                    machine_id=machine_id,
                    machine_name=machine_meta.get("name", machine_id),
                    department=dept_meta.get("name", dept_id),
                    severity=sev,
                    priority=prio,
                    category="Adaptive Threshold Breach",
                    reason=teval.get("reason", "Dynamic threshold boundary exceeded."),
                    evidence=[
                        {"metric": teval.get("metric"), "current_value": f"{teval.get('current_value')} {teval.get('unit')}", "expected": f"{teval.get('expected_value')} {teval.get('unit')}", "threshold": f"{teval.get('upper_threshold')} {teval.get('unit')}"},
                        {"metric": "Deviation %", "deviation": f"{teval.get('deviation_pct'):+.1f}%"},
                    ],
                    confidence=teval.get("confidence", 0.90),
                    suggested_action=f"Inspect {teval.get('metric')} sensor and check mechanical/electrical operating conditions.",
                    business_impact="Prevents prolonged thermal or electrical over-stress on industrial asset.",
                    financial_impact=round(abs(teval.get("deviation", 1.0)) * 14.5, 2),
                    timestamp=now_str,
                ))

        # ---------------------------------------------------------------------
        # 6. POWER FACTOR DEGRADATION ALERT
        # ---------------------------------------------------------------------
        pf = telemetry.get("power_factor", 0.95)
        if pf < MINIMUM_ACCEPTABLE_POWER_FACTOR and current_power > 5.0:
            alerts.append(self._build_alert(
                alert_type="LOW_POWER_FACTOR_WARNING",
                machine_id=machine_id,
                machine_name=machine_meta.get("name", machine_id),
                department=dept_meta.get("name", dept_id),
                severity="Warning",
                priority="Medium",
                category="Power Quality",
                reason=f"Operating power factor ({pf:.2f}) dropped below plant minimum compliance threshold ({MINIMUM_ACCEPTABLE_POWER_FACTOR:.2f}).",
                evidence=[
                    {"metric": "Power Factor cos φ", "measured": f"{pf:.2f}", "target": "0.98", "statutory_limit": f"{MINIMUM_ACCEPTABLE_POWER_FACTOR:.2f}"},
                    {"metric": "Reactive Draw kVAR", "value": f"{current_power * np.tan(np.arccos(max(0.5, pf))):.1f} kVAR"},
                ],
                confidence=0.91,
                suggested_action="Energize local capacitor step on APFC panel and check for inductive motor under-loading.",
                business_impact="Avoids power factor penalty charges on monthly utility tariff.",
                financial_impact=1850.0,
                timestamp=now_str,
            ))

        # ---------------------------------------------------------------------
        # 7. PRODUCTION VS ENERGY DECOUPLING ALERT
        # ---------------------------------------------------------------------
        units_produced = telemetry.get("units_produced_in_interval", 1)
        if current_power > (machine_meta.get("rated_power_kw", 20.0) * 0.40) and units_produced == 0 and machine_state == "running":
            alerts.append(self._build_alert(
                alert_type="PRODUCTION_ENERGY_DIVERGENCE",
                machine_id=machine_id,
                machine_name=machine_meta.get("name", machine_id),
                department=dept_meta.get("name", dept_id),
                severity="Warning",
                priority="High",
                category="Production Efficiency",
                reason="Machine drawing 40%+ rated active power while registering zero finished product throughput.",
                evidence=[
                    {"metric": "Active Power Draw", "measured": f"{current_power:.1f} kW"},
                    {"metric": "Throughput Count", "produced": "0 parts in last 15 min"},
                    {"metric": "Machine State", "reported": machine_state},
                ],
                confidence=0.88,
                suggested_action="Check for CNC spindle air-cutting, robotic feeder jam, or parts hopper starvation.",
                business_impact="Stops specific energy consumption (kWh/part) inflation and productivity loss.",
                financial_impact=3200.0,
                timestamp=now_str,
            ))

        return alerts

    def _build_alert(
        self,
        alert_type: str,
        machine_id: str,
        machine_name: str,
        department: str,
        severity: str,
        priority: str,
        category: str,
        reason: str,
        evidence: List[Dict[str, Any]],
        confidence: float,
        suggested_action: str,
        business_impact: str,
        financial_impact: float,
        timestamp: str,
    ) -> Dict[str, Any]:
        """Constructs a validated enterprise alert JSON structure."""
        alert_id = f"ALT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        return {
            "alert_id": alert_id,
            "alert_type": alert_type,
            "timestamp": timestamp,
            "machine_id": machine_id,
            "machine_name": machine_name,
            "department": department,
            "severity": severity,          # Normal, Information, Warning, Critical, Emergency
            "priority": priority,          # Information, Low, Medium, High, Critical
            "category": category,
            "reason": reason,
            "evidence": evidence,
            "confidence": confidence,
            "suggested_action": suggested_action,
            "estimated_business_impact": business_impact,
            "estimated_financial_impact_inr": round(float(financial_impact), 2),
        }
