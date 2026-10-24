"""
GreenPulse AI - Industrial Intelligence Layer: Recommendation Priority Engine
Ranks and prioritizes recommendations using Multi-Criteria Decision Analysis (MCDA).
Considers safety, financial savings, energy, carbon, ROI, machine criticality, and confidence.
"""
from typing import Dict, Any, List


class RecommendationPriorityEngine:
    """
    Ranks industrial recommendations through multi-attribute objective optimization:
    Score = w_safety * S + w_finance * F + w_energy * E + w_carbon * C + w_roi * R + w_crit * K + w_conf * P
    """

    def __init__(self):
        # Industrial weighting matrix (sum = 1.0)
        self.weights = {
            "safety": 0.25,             # Safety and equipment catastrophic risk prevention
            "financial": 0.20,          # Monetary savings (OPEX)
            "energy": 0.15,             # Active electrical reduction
            "carbon": 0.10,             # ESG decarbonization impact
            "roi": 0.10,                # Return on investment / payback speed
            "criticality": 0.10,        # Criticality of machine to continuous production line
            "confidence": 0.10,         # AI / Rule confidence level
        }

    def rank_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculates priority score for each recommendation and sorts descending.
        
        Returns:
            Sorted list of recommendations with computed priority scores and ranking tags.
        """
        if not recommendations:
            return []

        scored_recs = []
        for rec in recommendations:
            score = self._compute_score(rec)
            rec_copy = dict(rec)
            rec_copy["priority_score"] = round(float(score), 2)
            
            # Priority badge assignment
            if score >= 80.0:
                rec_copy["priority_rank"] = "CRITICAL_IMMEDIATE"
            elif score >= 65.0:
                rec_copy["priority_rank"] = "HIGH_PRIORITY"
            elif score >= 45.0:
                rec_copy["priority_rank"] = "MEDIUM_PRIORITY"
            else:
                rec_copy["priority_rank"] = "OPPORTUNITY"

            scored_recs.append(rec_copy)

        # Sort descending by priority score
        scored_recs.sort(key=lambda x: x["priority_score"], reverse=True)

        # Assign ordinal sequence numbers
        for idx, item in enumerate(scored_recs, start=1):
            item["sequence_rank"] = idx

        return scored_recs

    def _compute_score(self, rec: Dict[str, Any]) -> float:
        """Calculates normalized composite score (0 to 100)."""
        # 1. Safety & Risk Score (0 - 100)
        prio_str = str(rec.get("priority", "Medium")).lower()
        if "critical" in prio_str or "emergency" in prio_str:
            s_score = 100.0
        elif "high" in prio_str:
            s_score = 75.0
        elif "medium" in prio_str:
            s_score = 45.0
        else:
            s_score = 20.0

        # 2. Financial Impact Score (Normalized against ₹50,000/month benchmark)
        impact = rec.get("business_impact", {})
        fin = impact.get("financial_savings", {})
        monthly_inr = fin.get("monthly_total_savings_inr", rec.get("estimated_cost_savings_inr", 1000.0))
        f_score = min(100.0, (monthly_inr / 50000.0) * 100.0)

        # 3. Energy Savings Score (Normalized against 5,000 kWh/month)
        energy = impact.get("energy_savings", {})
        monthly_kwh = energy.get("monthly_kwh", rec.get("estimated_energy_savings_kwh", 100.0))
        e_score = min(100.0, (monthly_kwh / 5000.0) * 100.0)

        # 4. Carbon Savings Score (Normalized against 4,000 kg CO2/month)
        carbon = impact.get("carbon_reduction", {})
        monthly_carbon = carbon.get("monthly_carbon_kg_co2e", rec.get("estimated_carbon_reduction_kg", 50.0))
        c_score = min(100.0, (monthly_carbon / 4000.0) * 100.0)

        # 5. ROI & Implementation Ease Score
        diff_str = str(rec.get("implementation_difficulty", "Low")).lower()
        if "low" in diff_str or "immediate" in diff_str:
            r_score = 95.0
        elif "medium" in diff_str:
            r_score = 65.0
        else:
            r_score = 35.0

        # 6. Machine Criticality (1 to 5 scale -> 20 to 100)
        crit_val = rec.get("machine_criticality", 4)
        k_score = crit_val * 20.0

        # 7. Confidence Score (0.0 to 1.0 -> 0 to 100)
        conf_val = rec.get("confidence", 0.90)
        p_score = conf_val * 100.0

        # Weighted combination
        composite = (
            (self.weights["safety"] * s_score)
            + (self.weights["financial"] * f_score)
            + (self.weights["energy"] * e_score)
            + (self.weights["carbon"] * c_score)
            + (self.weights["roi"] * r_score)
            + (self.weights["criticality"] * k_score)
            + (self.weights["confidence"] * p_score)
        )

        return float(composite)
