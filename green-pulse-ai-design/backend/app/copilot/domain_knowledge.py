"""
GreenPulse AI Copilot - Industrial Domain Knowledge Base
Provides deep domain definitions, mathematical formulations, industrial benchmarks,
regulatory compliance references, and mitigation protocols for energy and manufacturing concepts.
"""
from typing import Dict, Optional, List

INDUSTRIAL_KNOWLEDGE_BASE: Dict[str, Dict[str, any]] = {
    "peak_demand": {
        "title": "Peak Demand (Maximum Demand - kW / kVA)",
        "definition": (
            "Peak Demand is the highest instantaneous or sliding-window average electrical load "
            "(typically integrated over 15 or 30-minute integration periods) registered by the utility "
            "tri-vector TOD (Time-of-Day) meter during a billing cycle."
        ),
        "formula": "Peak Demand (kVA) = Peak Real Power (kW) / Power Factor (cos φ)",
        "industrial_benchmarks": "Typically budgeted not to exceed 85% of Contracted Maximum Demand (CMD).",
        "financial_implications": (
            "Exceeding Contracted Demand incurs two-part tariff penalties: 150% to 200% penalty tariff "
            "on the excess kVA, plus potential demand ratchet penalties from DISCOMs (e.g. MSEDCL, BESCOM)."
        ),
        "mitigation_protocols": [
            "Stagger high-inertia equipment startups (Compressors, Furnaces).",
            "Shed non-critical thermal and auxiliary loads via automated PLC load-shedding relays.",
            "Utilize Battery Energy Storage Systems (BESS) or rooftop solar during peak tariff slots.",
            "Reschedule high-load batch annealing or melting to off-peak / night valley hours."
        ],
        "keywords": ["peak demand", "maximum demand", "kw spike", "kva spike", "demand surge", "demand penalty", "peak load"]
    },
    "contract_demand": {
        "title": "Contracted Maximum Demand (CMD - kVA / kW)",
        "definition": (
            "The maximum electrical power sanctioned and contracted between the industrial manufacturing "
            "facility and the electric distribution utility (DISCOM) for a dedicated HT (High Tension) consumer connection."
        ),
        "formula": "Billing Demand = Max(Actual Recorded MD, 75% or 85% of Contract Demand)",
        "industrial_benchmarks": "GreenPulse Plant #4 CMD is rated at 2,500 kW (approx 2,778 kVA at 0.90 PF).",
        "financial_implications": (
            "Demand charges are levied monthly on Billing Demand regardless of actual consumption. "
            "Under-utilizing below 75% results in paying for unused capacity; exceeding triggers severe penalties."
        ),
        "mitigation_protocols": [
            "Right-size contract demand through trailing 12-month load duration curve audits.",
            "Implement automatic demand controller with audible siren at 90% CMD threshold."
        ],
        "keywords": ["contract demand", "contracted demand", "cmd", "sanctioned load", "ht connection", "demand charge"]
    },
    "power_factor": {
        "title": "Power Factor (cos φ / True PF)",
        "definition": (
            "The ratio of Real Working Power (kW) to Apparent Power (kVA) drawn from the AC supply grid. "
            "In modern nonlinear industrial plants (VFDs, rectifiers, arc furnaces), True PF accounts for both "
            "Displacement PF and Harmonic Distortion (THD-I)."
        ),
        "formula": "True PF = (kW / kVA) = Displacement PF × (1 / √(1 + THD_i²))",
        "industrial_benchmarks": (
            "Target: 0.98 to 1.00 (Unity). Indian utilities mandate PF ≥ 0.90. Utilities offer 0.5% to 7% bill incentives "
            "for maintaining PF > 0.95, and penalize heavily for PF < 0.90."
        ),
        "financial_implications": (
            "A drop from 0.98 to 0.85 increases kVA apparent demand by 15.3%, triggering kVA demand penalties "
            "and active line loss heating (I²R losses) in factory transformers and busbars."
        ),
        "mitigation_protocols": [
            "Automatic Power Factor Correction (APFC) capacitor banks with microprocessor thyristor switching.",
            "Active Harmonic Filters (AHF) to eliminate harmonic reactive currents drawn by CNCs and VFDs.",
            "Synchronous condensers or localized compensation at terminal induction motor terminals."
        ],
        "keywords": ["power factor", "pf", "lagging", "leading", "kvar", "apfc", "reactive power", "thd", "true pf"]
    },
    "load_factor": {
        "title": "Plant Electrical Load Factor (LF)",
        "definition": (
            "The measure of plant energy utilization efficiency, defined as the ratio of average energy consumed "
            "over a designated timeframe to the peak demand observed over that same timeframe."
        ),
        "formula": "Load Factor (%) = (Total kWh Consumed in Period) / (Peak Demand kW × Total Hours in Period) × 100",
        "industrial_benchmarks": "World-class continuous manufacturing plants achieve 75% - 85% Load Factor.",
        "financial_implications": (
            "Higher load factor spreads fixed demand charges across more units of production, lowering the blended cost per kWh."
        ),
        "mitigation_protocols": [
            "Levelize batch production scheduling across 3 operating shifts.",
            "Interlock compressor unload cycles and pre-cool chiller storage."
        ],
        "keywords": ["load factor", "lf", "load duration", "load flattening", "utilization factor"]
    },
    "carbon_intensity": {
        "title": "Carbon Intensity (Specific GHG Emissions)",
        "definition": (
            "The emission rate of greenhouse gases relative to production output or electrical energy consumed, "
            "expressed in kg CO₂ equivalent per unit of production (e.g. kg CO₂e / finished part or kg CO₂e / kWh)."
        ),
        "formula": "Carbon Intensity = Total Emissions (Scope 1 + Scope 2 in kg CO₂e) / Production Output Units",
        "industrial_benchmarks": "GreenPulse Plant benchmark: Grid emission factor is 0.82 kg CO₂/kWh (CEA Central Electricity Authority baseline).",
        "financial_implications": (
            "Direct impact on BRSR (Business Responsibility and Sustainability Reporting) compliance for SEBI listed entities, "
            "EU CBAM (Carbon Border Adjustment Mechanism) export tariffs, and carbon credit monetization under BEE CCTS."
        ),
        "mitigation_protocols": [
            "Increase on-site rooftop solar and group captive renewable open access wheeling.",
            "Eliminate compressed air system leaks and down-throttle idle furnace induction loops."
        ],
        "keywords": ["carbon intensity", "ghg", "emission factor", "scope 1", "scope 2", "brsr", "cbam", "co2e", "carbon footprint"]
    },
    "machine_health": {
        "title": "Machine Health Index (MHI / Asset Reliability)",
        "definition": (
            "A composite multi-parameter score (0 - 100%) that quantifies the structural, electrical, and thermal "
            "degradation of an industrial machine, synthesizing vibration RMS, winding temperature, bearing acoustics, "
            "harmonics, and power draw stability."
        ),
        "formula": "MHI = 100 - [w₁·(Vib_Norm) + w₂·(Temp_Norm) + w₃·(Harmonic_Norm) + w₄·(Current_Unbalance)]",
        "industrial_benchmarks": "Healthy > 80%, Warning: 60% - 80%, Critical < 60% (Immediate intervention required).",
        "financial_implications": (
            "Preventing unplanned line breakdown on critical assets (like Air Compressors or Induction Furnaces) "
            "avoids direct production loss averaging ₹1,50,000 to ₹4,00,000 per hour of downtime."
        ),
        "mitigation_protocols": [
            "Condition-based predictive vibration monitoring adhering to ISO 10816 vibration severity standards.",
            "Infrared thermography scan of contactors and motor drive end (DE) bearings.",
            "Dynamic lubrication replenishment based on high-frequency ultrasound acoustic metrics."
        ],
        "keywords": ["machine health", "mhi", "asset health", "equipment condition", "iso 10816", "vibration", "bearing", "health index"]
    },
    "shap": {
        "title": "SHAP (SHapley Additive exPlanations) for Industrial AI",
        "definition": (
            "A game-theoretic framework based on Shapley values that computes the exact marginal contribution "
            "of each sensor feature (ambient temperature, motor RPM, pressure, shift type) toward an XGBoost energy "
            "prediction or an Isolation Forest anomaly flag."
        ),
        "formula": "f(x) = φ₀ + ∑ [φᵢ · xᵢ], where φᵢ is the Shapley value of feature i",
        "industrial_benchmarks": "Provides deterministic feature attribution and auditability for plant engineers.",
        "financial_implications": (
            "Translates abstract AI predictions into actionable physical root causes (e.g. 'Pressure drop contributed +42 kW')."
        ),
        "mitigation_protocols": [
            "Direct maintenance technicians toward the top 2 highest positive SHAP contributing physical attributes."
        ],
        "keywords": ["shap", "shapley", "explainability", "feature importance", "root cause", "xai"]
    },
    "forecast_confidence": {
        "title": "Forecast Confidence & Prediction Intervals",
        "definition": (
            "The statistical certainty boundary (typically 90% or 95% confidence interval) generated around "
            "the 24-hour machine energy demand curve, accounting for production scheduling variance, weather humidity, "
            "and historical heteroscedastic noise."
        ),
        "formula": "Interval = ŷ ± (z_{α/2} · σ_residual)",
        "industrial_benchmarks": "GreenPulse XGBoost forecasting engine achieves MAPE (Mean Absolute Percentage Error) < 4.2%.",
        "financial_implications": (
            "Enables Day-Ahead Market (DAM) power scheduling and avoids DISCOM deviation settlement penalties (DSM)."
        ),
        "mitigation_protocols": [
            "Update exogenous shift schedules and production batch plans to tighten prediction intervals."
        ],
        "keywords": ["forecast confidence", "prediction interval", "mape", "uncertainty", "confidence band"]
    },
    "isolation_forest": {
        "title": "Isolation Forest Unsupervised Anomaly Detection",
        "definition": (
            "An unsupervised tree-ensemble anomaly detection algorithm that isolates multi-dimensional sensor outliers "
            "by randomly partitioning feature values. Outliers require fewer splits to isolate than normal operating points."
        ),
        "formula": "Anomaly Score s(x, n) = 2^(-E(h(x)) / c(n))",
        "industrial_benchmarks": "Threshold calibrated at contamination rate c = 0.03 (top 3% abnormal operational events).",
        "financial_implications": (
            "Detects micro-frictional bearing seizing, phase unbalance, and pressure leaks hours before catastrophic failure."
        ),
        "mitigation_protocols": [
            "Trigger automatic supervisory SCADA telemetry snapshots when anomaly score exceeds 0.65."
        ],
        "keywords": ["isolation forest", "anomaly detection", "outlier", "contamination", "unsupervised ml", "anomaly score"]
    },
    "xgboost": {
        "title": "XGBoost (Extreme Gradient Boosting) Energy Modeling",
        "definition": (
            "A highly optimized distributed gradient boosted decision tree algorithm used by GreenPulse AI to model "
            "nonlinear relationships between machine operational states, ambient conditions, and energy consumption."
        ),
        "formula": "Obj(θ) = ∑ L(yᵢ, ŷᵢ) + ∑ Ω(f_k), where Ω penalizes tree depth and leaf weights",
        "industrial_benchmarks": "Produces calibrated hourly energy forecasts across all 9 factory machinery assets.",
        "financial_implications": "Provides reliable baseline modeling for ISO 50001 Energy Performance Indicators (EnPI).",
        "mitigation_protocols": [
            "Retrain models bi-weekly with new SCADA telemetry to prevent concept drift across seasonal ambient shifts."
        ],
        "keywords": ["xgboost", "gradient boosting", "energy forecasting", "ml model", "regression"]
    },
    "digital_twin": {
        "title": "Industrial Digital Twin & Modbus Telemetry",
        "definition": (
            "A high-fidelity digital virtual representation of physical manufacturing machines continuously synchronized "
            "with real-time PLC/SCADA Modbus TCP and OPC-UA sensor telemetry (current, voltage, vibration, temperature, pressure)."
        ),
        "formula": "State Synchronization: S_twin(t) = f(S_physical(t), Modbus_Tags(t))",
        "industrial_benchmarks": "GreenPulse telemetry updates at 0.4s to 1.0s polling cycles across 21 registers per machine.",
        "financial_implications": (
            "Enables real-time virtual stress testing, thermal modeling, and simulation without interrupting factory floor operations."
        ),
        "mitigation_protocols": [
            "Monitor communication packet loss on Modbus TCP port 502 and verify gateway keep-alives."
        ],
        "keywords": ["digital twin", "scada", "modbus", "opc ua", "telemetry", "virtual asset", "plc"]
    },
    "predictive_maintenance": {
        "title": "Predictive Maintenance (PdM) & CBM",
        "definition": (
            "Condition-Based Maintenance that leverages machine learning anomaly scores, vibration spectrum analysis, "
            "and thermal imaging to execute service actions precisely before mechanical failure occurs."
        ),
        "formula": "Remaining Useful Life (RUL) estimation based on degradation trajectory curves",
        "industrial_benchmarks": "Reduces maintenance expenditure by 25-30% and eliminates up to 70% of unplanned downtime.",
        "financial_implications": (
            "Saves major repair costs, avoids secondary component destruction, and preserves motor efficiency standards."
        ),
        "mitigation_protocols": [
            "Schedule maintenance during scheduled changeovers or low-tariff night shifts."
        ],
        "keywords": ["predictive maintenance", "pdm", "condition based maintenance", "cbm", "rul", "maintenance schedule"]
    },
    "equipment_utilization": {
        "title": "Overall Equipment Effectiveness (OEE) & Asset Utilization",
        "definition": (
            "The gold-standard manufacturing productivity metric measuring the percentage of manufacturing time "
            "that is truly productive. Composed of Availability, Performance, and Quality."
        ),
        "formula": "OEE = Availability (%) × Performance Rate (%) × Quality Rate (%)",
        "industrial_benchmarks": "World-Class OEE benchmark: > 85% (Availability: 90%, Performance: 95%, Quality: 99.9%).",
        "financial_implications": (
            "A 1% increase in plant OEE typically unlocks ₹15,00,000 - ₹35,00,000 in annual capacity without capital expenditure."
        ),
        "mitigation_protocols": [
            "Reduce changeover times using SMED (Single-Minute Exchange of Die) methodology.",
            "Eliminate micro-stoppages caused by machine feeder misalignment."
        ],
        "keywords": ["oee", "equipment utilization", "availability", "performance rate", "quality rate", "utilization"]
    },
    "production_efficiency": {
        "title": "Specific Energy Consumption (SEC / Production Efficiency)",
        "definition": (
            "The electrical energy required to produce a single unit of finished manufacturing output (kWh per kg, per part, or per heat)."
        ),
        "formula": "SEC = Total Energy Consumed (kWh) / Total Standard Output Units Produced",
        "industrial_benchmarks": "Targeted under Bureau of Energy Efficiency (BEE) Perform, Achieve and Trade (PAT) mandatory norms.",
        "financial_implications": (
            "SEC reduction directly reduces unit cost of goods sold (COGS) and yields tradable Energy Saving Certificates (ESCerts)."
        ),
        "mitigation_protocols": [
            "Ensure machines operate within their rated sweet-spot loading curve (70% - 85% full load).",
            "Eliminate unneeded machine idling through automated sleep modes."
        ],
        "keywords": ["production efficiency", "sec", "specific energy consumption", "kwh per unit", "energy intensity"]
    }
}


def lookup_domain_concept(query: str) -> Optional[Dict[str, any]]:
    """Finds the most relevant domain concept based on keyword matching."""
    q = query.lower()
    for key, data in INDUSTRIAL_KNOWLEDGE_BASE.items():
        for kw in data["keywords"]:
            if kw in q:
                return data
    return None


def get_all_concepts() -> List[str]:
    """Returns list of all available industrial concept keys."""
    return list(INDUSTRIAL_KNOWLEDGE_BASE.keys())
