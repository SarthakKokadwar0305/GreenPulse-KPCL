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
    MachineSimulationRequest,
    MachineSimulationResponse,
    SimulationTimelineEntry,
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


@router.post(
    "/machine",
    response_model=ApiResponse[MachineSimulationResponse],
    summary="Run Interactive Machine Digital Twin Simulation",
    description="Evaluates machine parametric variations (State, Runtime, Load, Motor Speed, Temp, Voltage, Current, Power Factor, Renewable %, Condition) and outputs real-time predictions, explanations, and prescriptive insights."
)
@router.post(
    "/machine/simulate",
    response_model=ApiResponse[MachineSimulationResponse],
    include_in_schema=False,
)
async def simulate_machine(
    request: MachineSimulationRequest,
    current_user: User = Depends(require_permissions("VIEW_MACHINE", "VIEW_SIMULATOR")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[MachineSimulationResponse]:
    service = SimulatorService(db)
    result = await service.simulate_machine(request)
    return ApiResponse.ok(data=result, message=f"Digital twin simulation for {request.machine_id} completed")


@router.post(
    "/machine/history",
    response_model=ApiResponse[SimulationTimelineEntry],
    summary="Append Digital Twin Simulation Run to Timeline Audit",
)
async def record_simulation_history(
    entry: SimulationTimelineEntry,
    current_user: User = Depends(require_permissions("VIEW_SIMULATOR")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[SimulationTimelineEntry]:
    service = SimulatorService(db)
    saved = await service.record_simulation_timeline(entry)
    return ApiResponse.ok(data=saved, message="Simulation run logged to audit timeline")


@router.get(
    "/machine/history",
    response_model=ApiResponse[List[SimulationTimelineEntry]],
    summary="Get Digital Twin Simulation Timeline Audit",
)
async def get_simulation_history(
    limit: int = 25,
    current_user: User = Depends(require_permissions("VIEW_SIMULATOR")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[List[SimulationTimelineEntry]]:
    service = SimulatorService(db)
    entries = await service.get_simulation_timeline(limit=limit)
    return ApiResponse.ok(data=entries, message=f"Retrieved {len(entries)} timeline events")

