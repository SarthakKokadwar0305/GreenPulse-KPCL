"""
GreenPulse AI - Anomaly API Route
Provides real-time incident detection, evidence metrics, and maintenance ticket dispatch.
Clean Architecture: Delegates all domain logic to AnomalyService.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permissions
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.anomaly import (
    AnomalyIncidentSchema,
    AcknowledgeAnomalyRequest,
    CreateWorkOrderRequest,
)
from app.services.anomaly_service import AnomalyService

router = APIRouter(tags=["Anomalies"])


@router.get(
    "/anomalies",
    response_model=ApiResponse[List[AnomalyIncidentSchema]],
    summary="List Detected Equipment Anomalies (Plural Alias)",
    include_in_schema=False,
)
@router.get(
    "/anomaly",
    response_model=ApiResponse[List[AnomalyIncidentSchema]],
    summary="List Detected Equipment Anomalies",
    description="""
Retrieves active and historical plant anomaly incidents detected via unsupervised machine learning and industrial rule triggers.

### Diagnostic Capabilities:
- **Isolation Forest Scoring**: Quantifies operational deviation from normal subspace (-1.0 to +1.0).
- **Industrial Threshold Breaches**: Evaluates current telemetry against adaptive bounds.
- **Root Cause & Triggered Rules**: Identifies contributing equipment subsystems (e.g., thermal excursion, phase imbalance).
- **Prescriptive Actions**: Recommends immediate operational mitigations.
""",
    responses={
        200: {
            "description": "Successfully retrieved detected anomalies with root cause attributions.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": [
                            {
                                "id": "anom-01",
                                "machine_id": "COMP-01",
                                "machine_name": "Main Air Compressor",
                                "anomaly_type": "Unscheduled Pressure Drop & Power Spike",
                                "severity": "critical",
                                "anomaly_score": 0.88,
                                "confidence_percent": 94.5,
                                "root_cause": "Intake valve leakage causing compressor motor over-amperage",
                                "threshold_violated": "Active Power (410 kW > 380 kW limit)",
                                "triggered_rules": ["RULE-EQ-001: Excessive Compressor Cycle Power"],
                                "suggested_action": "Isolate secondary compressor manifold and inspect inlet seal.",
                                "model_version": "1.2.0-prod"
                            }
                        ],
                        "message": "Fetched 1 anomaly incidents",
                        "errors": []
                    }
                }
            }
        },
        400: {"description": "Bad Request: Invalid severity or status filter value."},
        500: {"description": "Internal Server Error: Telemetry anomaly evaluation failed."}
    }
)
@router.get(
    "/anomalies",
    response_model=ApiResponse[List[AnomalyIncidentSchema]],
    summary="List Detected Equipment Anomalies (Alias)",
    description="Alias for /anomaly providing enterprise RESTful compatibility.",
    include_in_schema=True,
    responses={
        200: {"description": "Successfully retrieved detected anomalies."},
        400: {"description": "Bad Request: Invalid query parameter."},
        500: {"description": "Internal Server Error."}
    }
)
async def list_anomalies(
    severity: Optional[str] = Query(None, description="Filter by severity: critical, warning, info"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: open, investigating, acknowledged, resolved"),
    current_user: User = Depends(require_permissions("VIEW_ALERTS")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[List[AnomalyIncidentSchema]]:
    service = AnomalyService(db)
    anomalies = await service.get_anomalies(severity=severity, status=status_filter)

    # Filter for Operator: restricted strictly to assigned machines
    if current_user.role == "OPERATOR":
        assigned_ids = {m.lower() for m in current_user.assigned_machine_ids}
        assigned_codes = {m.upper() for m in current_user.assigned_machine_codes}
        anomalies = [
            a for a in anomalies
            if a.machine_id.lower() in assigned_ids or a.machine_id.upper() in assigned_codes
        ]

    return ApiResponse.ok(data=anomalies, message=f"Fetched {len(anomalies)} anomaly incidents")


@router.post(
    "/anomaly/{incident_id}/acknowledge",
    response_model=ApiResponse[AnomalyIncidentSchema],
    summary="Acknowledge Anomaly Incident",
    description="Marks an active anomaly as acknowledged by a plant engineer."
)
async def acknowledge_anomaly(
    incident_id: str,
    request: AcknowledgeAnomalyRequest,
    current_user: User = Depends(require_permissions("ACKNOWLEDGE_ALERT")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[AnomalyIncidentSchema]:
    service = AnomalyService(db)
    updated = await service.acknowledge_anomaly(incident_id, request)
    return ApiResponse.ok(data=updated, message=f"Incident '{incident_id}' acknowledged by {request.engineer_name}")


@router.post(
    "/anomaly/{incident_id}/work-order",
    response_model=ApiResponse[Dict[str, Any]],
    status_code=status.HTTP_201_CREATED,
    summary="Generate Maintenance Work Order for Anomaly",
    description="Dispatches a work order to technicians with priority and inspection guidelines."
)
async def create_work_order(
    incident_id: str,
    request: CreateWorkOrderRequest,
    current_user: User = Depends(require_permissions("SCHEDULE_MAINTENANCE")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[Dict[str, Any]]:
    service = AnomalyService(db)
    result = await service.create_work_order(incident_id, request)
    return ApiResponse.ok(data=result, message=f"Work order {result.get('work_order_id')} generated successfully")
