"""
GreenPulse AI - Machines API Route
Provides asset-level telemetry, three-phase electrical diagnostics, thermal status, and maintenance logs.
Enforces Role-Based Access Control and strict Operator machine filtering.
Clean Architecture: Delegates all domain logic to MachineService.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_machine_authorization
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.machine import MachineDetailSchema
from app.services.machine_service import MachineService

router = APIRouter(prefix="/machines", tags=["Machines"])


@router.get(
    "",
    response_model=ApiResponse[List[MachineDetailSchema]],
    summary="List Factory Machines (Role-Filtered)",
    description="Returns telemetry, health index, runtime, power consumption, and status for monitored industrial assets. Operators see assigned machines only."
)
async def list_machines(
    zone: Optional[str] = Query(None, description="Filter by factory zone/bay"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by operational status (running, warning, critical, idle)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[List[MachineDetailSchema]]:
    if not current_user.has_permission("VIEW_MACHINE") and not current_user.has_permission("VIEW_ASSIGNED_MACHINE"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Lacks permission to view machine fleet.",
        )

    service = MachineService(db)
    machines = await service.get_machines(zone=zone, status=status_filter)

    # Operator filtering: restrict strictly to assigned machinery
    if current_user.role == "OPERATOR":
        assigned_ids = {m.lower() for m in current_user.assigned_machine_ids}
        assigned_codes = {m.upper() for m in current_user.assigned_machine_codes}
        machines = [
            m for m in machines
            if m.id.lower() in assigned_ids or m.code.upper() in assigned_codes
        ]

    return ApiResponse.ok(data=machines, message=f"Fetched {len(machines)} machine assets")


@router.get(
    "/machine/{machine_id}",
    response_model=ApiResponse[MachineDetailSchema],
    summary="Get Machine Telemetry & Digital Twin by ID (Alias)",
    include_in_schema=False,
)
@router.get(
    "/{machine_id}",
    response_model=ApiResponse[MachineDetailSchema],
    summary="Get Machine Telemetry & Digital Twin by ID",
    description="Returns detailed engineering telemetry: 3-phase currents, voltages, harmonics, thermal profile, and maintenance logs."
)
async def get_machine(
    machine_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[MachineDetailSchema]:
    if not current_user.has_permission("VIEW_MACHINE") and not current_user.has_permission("VIEW_ASSIGNED_MACHINE"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Lacks permission to view machine telemetry.",
        )

    # Enforce assigned machine isolation for Operators
    verify_machine_authorization(machine_id, current_user)

    service = MachineService(db)
    machine = await service.get_machine_by_id(machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with ID '{machine_id}' was not found in plant registry."
        )
    return ApiResponse.ok(data=machine, message=f"Machine '{machine_id}' telemetry fetched")
