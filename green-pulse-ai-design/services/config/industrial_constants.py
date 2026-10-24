"""
GreenPulse AI - Industrial Intelligence Layer: Industrial Constants
Standard manufacturing tariffs, emission factors, shifts, and contractual limits.
"""

# Tariff Schedules (Time-of-Day / ToD Structure)
BASE_TARIFF_INR_PER_KWH = 7.20
PEAK_TARIFF_INR_PER_KWH = 10.368    # 1.44x surcharge during peak stress hours
OFF_PEAK_TARIFF_INR_PER_KWH = 5.20  # Night hours discounted incentive

# Peak and Off-Peak Hour Windows
PEAK_HOURS = [10, 11, 18, 19, 20, 21]       # Morning & evening industrial peak demand
OFF_PEAK_HOURS = [22, 23, 0, 1, 2, 3, 4, 5] # Night valley off-peak
STANDARD_HOURS = [6, 7, 8, 9, 12, 13, 14, 15, 16, 17]

# Sustainability & Emissions (Scope 2 Grid Emission Factor - CEA India)
GRID_EMISSION_FACTOR_KG_PER_KWH = 0.82
SOLAR_EMISSION_FACTOR_KG_PER_KWH = 0.045 # Life cycle embodied carbon

# Contracted Demand & Electrical Boundaries
CONTRACTED_MAX_DEMAND_KW = 250.0       # Plant total sanctioned demand
DEMAND_WARNING_THRESHOLD_KW = 212.5     # 85% of contract limit
DEMAND_CRITICAL_THRESHOLD_KW = 237.5    # 95% of contract limit (penalty imminent)
MDI_PENALTY_RATE_INR_PER_KVA = 450.0    # Surcharge per kVA exceeding contracted demand

# Power Factor Thresholds
TARGET_POWER_FACTOR = 0.98
MINIMUM_ACCEPTABLE_POWER_FACTOR = 0.92
POWER_FACTOR_PENALTY_THRESHOLD = 0.90   # Discom penalty kicks in below 0.90

# Plant Shift Schedules
SHIFT_SCHEDULE = {
    "A": {"name": "Morning Shift", "start_hour": 6, "end_hour": 14, "target_production_rate": 1.0},
    "B": {"name": "Afternoon Shift", "start_hour": 14, "end_hour": 22, "target_production_rate": 0.95},
    "C": {"name": "Night Shift", "start_hour": 22, "end_hour": 6, "target_production_rate": 0.80},
}

# Operating Day Types
WEEKDAY_HOURS_PER_YEAR = 24.0 * 260.0
WEEKEND_HOURS_PER_YEAR = 24.0 * 105.0

# Telemetry Sampling Interval
INTERVAL_MINUTES = 5.0
INTERVAL_HOURS = INTERVAL_MINUTES / 60.0
INTERVALS_PER_HOUR = 12
INTERVALS_PER_DAY = 288
