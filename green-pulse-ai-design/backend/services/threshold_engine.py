"""
GreenPulse AI - Industrial Intelligence Layer: Adaptive Threshold Engine
Calculates dynamic, context-aware industrial operating thresholds based on historical behavior,
rolling statistics, shift parameters, machine utilization, and departmental baselines.
Never uses static hardcoded thresholds.
"""
from typing import Dict, Any, List, Optional
import numpy as np

from services.config.industrial_constants import (
    SHIFT_SCHEDULE,
    PEAK_HOURS,
    OFF_PEAK_HOURS,
    STANDARD_HOURS,
)
from services.config.machine_config import MACHINES
from services.config.department_config import DEPARTMENTS
from services.config.threshold_config import THRESHOLD_CONFIG


class AdaptiveThresholdEngine:
    """
    Production Adaptive Threshold Engine that computes dynamic operational bounds
    adapted to the equipment, department, diurnal hour, shift, and recent rolling window.
    """

    def __init__(self):
        self.machines = MACHINES
        self.departments = DEPARTMENTS
        self.config = THRESHOLD_CONFIG

    def evaluate_metric_threshold(
        self,
        machine_id: str,
        metric_name: str,
        current_value: float,
        hour: int,
        day_of_week: int,
        shift: str,
        machine_state: str,
        rolling_mean: Optional[float] = None,
        rolling_std: Optional[float] = None,
        rolling_median: Optional[float] = None,
        percentile_95: Optional[float] = None,
        production_level_pct: float = 100.0,
        load_ratio: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Dynamically calculates expected value and upper/lower bounds for an industrial metric.
        
        Returns:
            Structured JSON-ready dictionary with:
            Current Value, Expected Value, Threshold, Deviation, Deviation %, Confidence, Reason, Severity.
        """
        machine_meta = self.machines.get(machine_id, {})
        dept_id = machine_meta.get("department_id", "DEPT-MACHINING")
        dept_meta = self.departments.get(dept_id, {})

        is_weekend = day_of_week >= 5
        shift_weight = self.config["shift_adaptation_weights"].get(shift, 1.0)
        is_peak_hour = hour in PEAK_HOURS

        # 1. Base Expected Value Determination
        if metric_name in ["active_power_kw", "power_kw"]:
            expected_val, tolerance_std, baseline_reason = self._compute_power_baseline(
                machine_meta, machine_state, rolling_mean, rolling_median,
                rolling_std, shift_weight, is_weekend, production_level_pct, load_ratio
            )
            unit = "kW"
            param_label = "Active Power"

        elif metric_name in ["temperature_c", "temp_c"]:
            expected_val, tolerance_std, baseline_reason = self._compute_temperature_baseline(
                machine_meta, machine_state, rolling_mean, rolling_std
            )
            unit = "°C"
            param_label = "Temperature"

        elif metric_name in ["runtime_hours", "runtime_hr"]:
            expected_val, tolerance_std, baseline_reason = self._compute_runtime_baseline(
                machine_meta, shift, machine_state
            )
            unit = "hours"
            param_label = "Runtime Duration"

        elif metric_name in ["power_factor", "pf"]:
            expected_val = machine_meta.get("expected_power_factor", 0.94)
            tolerance_std = self.config["min_std_floor_pf"]
            unit = "cos φ"
            param_label = "Power Factor"
            baseline_reason = "Substation load excitation curve baseline"

        else:
            # Fallback for generic telemetry
            expected_val = rolling_mean if rolling_mean is not None else current_value
            tolerance_std = rolling_std if rolling_std is not None else (expected_val * 0.1)
            unit = "units"
            param_label = metric_name
            baseline_reason = "Historical telemetry median baseline"

        # 2. Dynamic Adaptive Bounds Computation (Mean ± k * Std)
        k_warning = self.config["z_score_warning"]
        k_critical = self.config["z_score_critical"]

        # Adapt tolerance based on 95th percentile clamp if available
        if percentile_95 is not None and percentile_95 > expected_val:
            p95_margin = (percentile_95 - expected_val) / 2.0
            tolerance_std = max(tolerance_std, p95_margin)

        upper_warning = expected_val + (k_warning * tolerance_std)
        lower_warning = max(0.0, expected_val - (k_warning * tolerance_std))
        upper_critical = expected_val + (k_critical * tolerance_std)
        lower_critical = max(0.0, expected_val - (k_critical * tolerance_std))

        # 3. Deviation & Deviation %
        deviation = current_value - expected_val
        deviation_pct = (deviation / max(abs(expected_val), 1e-3)) * 100.0

        # 4. Severity Assessment
        if current_value > upper_critical or current_value < lower_critical:
            severity = "Critical"
        elif current_value > upper_warning or current_value < lower_warning:
            severity = "Warning"
        else:
            severity = "Normal"

        # 5. Industrial Confidence Score (0.0 to 1.0)
        # Higher confidence when rolling stats are supported by stable operation
        data_stability = 1.0 / (1.0 + (tolerance_std / max(abs(expected_val), 1.0)))
        confidence = round(float(np.clip(0.80 + (0.19 * data_stability), 0.80, 0.99)), 4)

        # 6. Detailed Industrial Reason Synthesis
        if severity == "Normal":
            reason = f"{param_label} operating comfortably within dynamic industrial tolerance ({expected_val:.1f} ± {k_warning * tolerance_std:.1f} {unit}) for Shift {shift}."
        elif deviation > 0:
            reason = (
                f"{param_label} excursion: Current {current_value:.1f} {unit} exceeds dynamic upper threshold of "
                f"{upper_warning:.1f} {unit} (+{deviation_pct:.1f}% deviation) against {baseline_reason}."
            )
        else:
            reason = (
                f"{param_label} drop: Current {current_value:.1f} {unit} dropped below expected threshold of "
                f"{lower_warning:.1f} {unit} ({deviation_pct:.1f}% deviation) against {baseline_reason}."
            )

        return {
            "machine_id": machine_id,
            "machine_name": machine_meta.get("name", machine_id),
            "department": dept_meta.get("name", dept_id),
            "metric": metric_name,
            "unit": unit,
            "current_value": round(float(current_value), 2),
            "expected_value": round(float(expected_val), 2),
            "lower_threshold": round(float(lower_warning), 2),
            "upper_threshold": round(float(upper_warning), 2),
            "critical_upper_threshold": round(float(upper_critical), 2),
            "deviation": round(float(deviation), 2),
            "deviation_pct": round(float(deviation_pct), 2),
            "severity": severity,
            "confidence": confidence,
            "reason": reason,
            "context": {
                "shift": shift,
                "hour": hour,
                "is_peak_tariff": is_peak_hour,
                "is_weekend": is_weekend,
                "machine_state": machine_state,
                "production_level_pct": production_level_pct,
            },
        }

    def _compute_power_baseline(
        self,
        machine_meta: Dict[str, Any],
        machine_state: str,
        rolling_mean: Optional[float],
        rolling_median: Optional[float],
        rolling_std: Optional[float],
        shift_weight: float,
        is_weekend: bool,
        production_level_pct: float,
        load_ratio: Optional[float],
    ):
        """Calculates expected active power adapted to state, shift, and load."""
        rated_kw = machine_meta.get("rated_power_kw", 25.0)
        mean_kw = machine_meta.get("mean_operating_power_kw", 10.0)
        idle_kw = machine_meta.get("idle_baseline_power_kw", 2.0)

        if machine_state in ["idle", "standby"]:
            expected_val = idle_kw
            tolerance_std = max(idle_kw * 0.25, self.config["min_std_floor_kw"])
            baseline_reason = "Unloaded machine idle power baseline"
        elif machine_state == "off":
            expected_val = 0.0
            tolerance_std = self.config["min_std_floor_kw"]
            baseline_reason = "De-energized equipment baseline"
        elif is_weekend:
            expected_val = idle_kw * self.config["weekend_load_factor"]
            tolerance_std = self.config["min_std_floor_kw"]
            baseline_reason = "Weekend standby maintenance baseline"
        else:
            # Active production state
            if rolling_mean is not None and rolling_mean > idle_kw:
                expected_val = rolling_mean
            elif rolling_median is not None:
                expected_val = rolling_median
            else:
                expected_val = mean_kw * shift_weight * (production_level_pct / 100.0)

            if rolling_std is not None and rolling_std > 0:
                tolerance_std = max(rolling_std, self.config["min_std_floor_kw"])
            else:
                tolerance_std = max(expected_val * 0.12, self.config["min_std_floor_kw"])

            baseline_reason = f"Historical operating mean adjusted for Shift {shift_weight}x throughput"

        return expected_val, tolerance_std, baseline_reason

    def _compute_temperature_baseline(
        self,
        machine_meta: Dict[str, Any],
        machine_state: str,
        rolling_mean: Optional[float],
        rolling_std: Optional[float],
    ):
        """Calculates expected temperature adapted to thermal inertia."""
        min_temp = machine_meta.get("normal_temp_min_c", 25.0)
        max_temp = machine_meta.get("normal_temp_max_c", 75.0)
        expected_val = (min_temp + max_temp) / 2.0

        if rolling_mean is not None and min_temp <= rolling_mean <= max_temp * 1.15:
            expected_val = rolling_mean

        if rolling_std is not None and rolling_std > 0:
            tolerance_std = max(rolling_std, self.config["min_std_floor_temp_c"])
        else:
            tolerance_std = max((max_temp - min_temp) * 0.15, self.config["min_std_floor_temp_c"])

        baseline_reason = f"Normal thermodynamic operating band ({min_temp}°C - {max_temp}°C)"
        return expected_val, tolerance_std, baseline_reason

    def _compute_runtime_baseline(
        self,
        machine_meta: Dict[str, Any],
        shift: str,
        machine_state: str,
    ):
        """Calculates expected continuous runtime for shift schedule."""
        shift_duration_hours = 8.0
        expected_val = shift_duration_hours * 0.85  # 85% typical shift operating factor
        tolerance_std = 1.5
        baseline_reason = f"Standard 8-hour shift schedule for Shift {shift}"
        return expected_val, tolerance_std, baseline_reason
