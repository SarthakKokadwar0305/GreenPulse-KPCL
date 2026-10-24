"""
GreenPulse AI - Industrial Intelligence Layer: Threshold Configuration
Adaptive statistical parameters, rolling windows, z-score boundaries, and shift weighting.
"""
from typing import Dict, Any

THRESHOLD_CONFIG: Dict[str, Any] = {
    # Rolling Statistical Windows
    "short_term_window_intervals": 12,    # 1 hour (12 x 5-minute readings)
    "medium_term_window_intervals": 72,   # 6 hours
    "long_term_window_intervals": 288,    # 24 hours (full diurnal baseline)

    # Multiplier k for Adaptive Confidence Interval: Expected = Mean ± k * Std
    "z_score_warning": 2.0,               # ~95.45% confidence boundary
    "z_score_critical": 3.0,              # ~99.73% confidence boundary
    "z_score_emergency": 4.0,             # Extreme industrial excursion

    # Percentile-based clipping
    "percentile_lower": 5.0,
    "percentile_upper": 95.0,

    # Minimum standard deviation floor to prevent division-by-zero on flatlined idle signals
    "min_std_floor_kw": 0.35,
    "min_std_floor_temp_c": 1.20,
    "min_std_floor_pf": 0.015,

    # Shift adaptation coefficients (accounting for varying production cadence per shift)
    "shift_adaptation_weights": {
        "A": 1.00,    # Morning full shift baseline
        "B": 0.95,    # Afternoon shift slight throughput variation
        "C": 0.80,    # Night maintenance & batch processing
    },

    # Weekend reduction coefficient
    "weekend_load_factor": 0.30,          # Plant runs in standby/maintenance on weekends

    # Maximum Allowable Continuous Idle Runtime Before Alerting (Minutes)
    "idle_timeout_rules_minutes": {
        "CNC-01": 20,
        "CNC-02": 20,
        "COMP-01": 15,
        "COMP-02": 15,
        "FURN-01": 30,
        "HVAC-01": 45,
        "PAINT-01": 15,
        "PUMP-01": 20,
    },
}
