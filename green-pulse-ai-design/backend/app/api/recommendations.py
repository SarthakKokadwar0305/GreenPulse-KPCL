"""
GreenPulse AI - Recommendations API Route
Provides prescriptive Energy Conservation Measures (ECMs), estimated savings, ROI, and execution status.
Clean Architecture: Delegates all domain logic to RecommendationService.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permissions
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.recommendation import (
    RecommendationSchema,
    ApplyRecommendationRequest,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get(
    "",
    response_model=ApiResponse[List[RecommendationSchema]],
    summary="List Energy Conservation Measures (ECMs)",
    description="""
Retrieves ranked prescriptive energy conservation measures and equipment tuning strategies.

### Prescriptive Capabilities:
- **Multi-Criteria Priority Ranking**: Weighs financial payback, energy magnitude, carbon abatement, and risk.
- **Quantified Business Impact**: Delivers monthly OPEX savings (INR), carbon emissions reduction (tCO2e), and payback period.
- **Industrial Reasoning**: Links recommendations directly to triggered business rules and machine health indices.
""",
    responses={
        200: {
            "description": "Successfully retrieved ranked energy conservation recommendations.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": [
                            {
                                "id": "rec-01",
                                "title": "Shift Annealing Furnace Cycle to Off-Peak Window",
                                "category": "Load Shifting",
                                "priority": "high",
                                "estimated_savings_currency_per_month": 42500.0,
                                "estimated_carbon_reduction_tons_per_month": 3.8,
                                "roi_percent": 185.0,
                                "payback_period_months": 2.5,
                                "business_explanation": "Executing the 3-hour heat treatment cycle after 22:00 IST avoids the Rs 9.50/kWh peak tariff penalty.",
                                "technical_explanation": "Reduces plant peak load by 140 kW during the 18:00-22:00 grid constraint window.",
                                "supporting_rule_ids": ["RULE-TO-001", "RULE-DM-002"],
                                "status": "active"
                            }
                        ],
                        "message": "Fetched 1 energy conservation recommendations",
                        "errors": []
                    }
                }
            }
        },
        400: {"description": "Bad Request: Invalid category filter."},
        500: {"description": "Internal Server Error: Failed to rank recommendations."}
    }
)
async def list_recommendations(
    category: Optional[str] = Query(None, description="Filter by category: Load Shifting, Asset Tuning, Setpoint Optimization"),
    current_user: User = Depends(require_permissions("VIEW_RECOMMENDATIONS")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[List[RecommendationSchema]]:
    service = RecommendationService(db)
    recs = await service.get_recommendations(category=category)
    return ApiResponse.ok(data=recs, message=f"Fetched {len(recs)} energy conservation recommendations")


@router.post(
    "/{recommendation_id}/apply",
    response_model=ApiResponse[RecommendationSchema],
    summary="Apply Prescriptive Recommendation",
    description="Triggers adoption of an ECM, dispatching automated setpoints or notifying plant operations."
)
async def apply_recommendation(
    recommendation_id: str,
    request: ApplyRecommendationRequest,
    current_user: User = Depends(require_permissions("APPROVE_RECOMMENDATIONS")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[RecommendationSchema]:
    service = RecommendationService(db)
    updated = await service.apply_recommendation(recommendation_id, request)
    return ApiResponse.ok(data=updated, message=f"Recommendation '{recommendation_id}' applied successfully")
