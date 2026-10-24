"""
GreenPulse AI - Forecast API Route
Provides multi-horizon AI energy, financial expenditure, and carbon forecasting.
Clean Architecture: Delegates all domain logic to ForecastService.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permissions
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.forecast import ForecastResponse
from app.services.forecast_service import ForecastService

router = APIRouter(prefix="/forecast", tags=["Forecast"])


@router.get(
    "",
    response_model=ApiResponse[ForecastResponse],
    summary="Get Multi-Horizon AI Demand & Carbon Forecast",
    description="""
Retrieves multi-horizon hourly energy demand, peak electrical load, financial expenditure, and carbon footprint forecasts.

### Enterprise Features:
- **XGBoost Inference**: Real-time multi-target regression over a 34-feature industrial vector.
- **SHAP Explainability**: Returns local feature attributions, positive/negative drivers, and plant-engineer-readable narratives.
- **Uncertainty Quantification**: Upper (95%) and lower (80%) confidence intervals for grid scheduling.
- **Industrial Thresholds**: Evaluates predicted peak load against contracted maximum demand (CMD).
""",
    responses={
        200: {
            "description": "Successfully generated multi-horizon forecast with SHAP explainability.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "forecast_range": "Next 24 Hours",
                            "projected_day_energy_kwh": 3840.5,
                            "projected_cost": 28803.75,
                            "projected_carbon_tons": 3.15,
                            "model_version": "1.2.0-prod",
                            "confidence_score": 0.94,
                            "shap_explanation": {
                                "base_value": 3120.0,
                                "prediction_value": 3840.5,
                                "top_contributing_features": [
                                    {"feature_name": "Shift Runtime (Hours)", "shap_value": 320.5, "feature_value": 18.0, "impact_type": "INCREASING"},
                                    {"feature_name": "Production Load (%)", "shap_value": 240.2, "feature_value": 115.0, "impact_type": "INCREASING"}
                                ],
                                "natural_language_explanation": "Predicted demand increased because: Shift Runtime (Hours) increased by 320.50 kWh; Production Load (%) increased by 240.20 kWh."
                            }
                        },
                        "message": "Forecast trajectory generated successfully",
                        "errors": []
                    }
                }
            }
        },
        400: {"description": "Bad Request: Malformed query parameters or unsupported scenario."},
        422: {"description": "Validation Error: Horizon out of bounds (1 to 168 hours allowed)."},
        500: {"description": "Internal Inference Error: Model failed to process telemetry vector."}
    }
)
async def get_forecast(
    horizon: int = Query(24, ge=1, le=168, description="Forecast horizon in hours (1 to 168)"),
    scenario: str = Query("standard", description="Forecasting scenario: standard, aggressive_ramp, solar_curtailment"),
    machine_id: Optional[str] = Query(None, description="Optional specific machine filter (e.g., COMP-01, FURN-01)"),
    current_user: User = Depends(require_permissions("VIEW_FORECAST")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[ForecastResponse]:
    service = ForecastService(db)
    data = await service.get_forecast(horizon_hours=horizon, scenario=scenario, machine_id=machine_id)
    return ApiResponse.ok(data=data, message="Forecast trajectory generated successfully")
