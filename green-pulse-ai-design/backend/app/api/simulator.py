"""
GreenPulse AI - Simulator API Route
Provides parametric what-if energy modeling, shift scheduling simulations, and ROI comparisons.
Clean Architecture: Delegates all domain logic to SimulatorService.
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permissions
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.simulation import (
    SimulationRequest,
    SimulationResponse,
)
from app.services.simulator_service import SimulatorService

router = APIRouter(prefix="/simulator", tags=["Simulator"])


@router.post(
    "",
    response_model=ApiResponse[SimulationResponse],
    summary="Run Operational What-If Energy Simulation",
    include_in_schema=False,
)
@router.post(
    "/simulate",
    response_model=ApiResponse[SimulationResponse],
    summary="Run Operational What-If Energy Simulation",
    description="""
Executes counterfactual what-if scenarios modeling plant production loading, equipment runtime hours, shift schedule reconfiguration, tariff rate variations, and renewable power integration.

### Simulation Engine Features:
- **XGBoost Inference**: Evaluates energy, cost, and carbon across perturbed operating points.
- **Tariff & Carbon Accounting**: Re-computes Time-of-Day (ToD) tariff curves and Scope 2 GHG emissions.
- **Prescriptive Guidance**: Generates an automated executive recommendation summary highlighting trade-offs.
""",
    responses={
        200: {
            "description": "Simulation completed successfully with delta comparisons.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "predicted_energy_kwh": 4120.0,
                            "predicted_cost_inr": 31250.0,
                            "predicted_carbon_tons": 3.38,
                            "savings_inr": 4500.0,
                            "recommendation_summary": "Increasing renewable share to 25% offsets the 10% load increase, yielding net savings of Rs 4,500/day.",
                            "hourly_comparison": [],
                            "model_version": "1.2.0-prod"
                        },
                        "message": "What-if simulation completed successfully",
                        "errors": []
                    }
                }
            }
        },
        400: {"description": "Bad Request: Incompatible simulation parameter combinations."},
        422: {"description": "Validation Error: Out-of-range parameter (e.g. negative runtime or load > 200%)."},
        500: {"description": "Internal Server Error: Simulation execution failed."}
    }
)
async def run_simulation(
    request: SimulationRequest,
    current_user: User = Depends(require_permissions("VIEW_SIMULATOR", "RUN_SIMULATION")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[SimulationResponse]:
    service = SimulatorService(db)
    result = await service.run_simulation(request)
    return ApiResponse.ok(data=result, message="What-if simulation completed successfully")


@router.post(
    "/compare",
    response_model=ApiResponse[List[SimulationResponse]],
    summary="Compare Multiple What-If Operational Scenarios",
    description="Runs side-by-side simulations across different parameter sets for capital planning and executive decisions."
)
async def compare_scenarios(
    scenarios: List[SimulationRequest],
    current_user: User = Depends(require_permissions("VIEW_SIMULATOR", "RUN_SIMULATION")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[List[SimulationResponse]]:
    service = SimulatorService(db)
    results = await service.compare_multiple(scenarios)
    return ApiResponse.ok(data=results, message=f"Simulated {len(results)} scenario permutations")
