"""
GreenPulse AI - Reports API Route
Provides access to compliance audits (Energy, Carbon, Anomaly, Forecast) and report generation.
Enforces Role-Based Access Control: Plant Head and Energy Manager only.
Clean Architecture: Delegates all domain logic to ReportService.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permissions
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.report import (
    ReportsListResponse,
    IndustrialReportSchema,
    GenerateReportRequest,
)
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "",
    response_model=ApiResponse[ReportsListResponse],
    summary="List Compliance & Operational Reports",
    description="Returns recent compliance audits across Energy, Carbon, Forecast, and Anomaly categories alongside scheduled reporting jobs."
)
async def list_reports(
    category: Optional[str] = Query(None, description="Filter reports by category: energy, carbon, anomaly, forecast"),
    current_user: User = Depends(require_permissions("VIEW_REPORTS")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[ReportsListResponse]:
    service = ReportService(db)
    data = await service.get_reports(category=category)
    return ApiResponse.ok(data=data, message="Reports list fetched successfully")


@router.post(
    "/generate",
    response_model=ApiResponse[IndustrialReportSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Generate On-Demand Industrial Audit Report",
    description="Compiles compliance telemetry and analytics into an exportable document (PDF, CSV, Excel)."
)
async def generate_report(
    request: GenerateReportRequest,
    current_user: User = Depends(require_permissions("EXPORT_REPORTS")),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[IndustrialReportSchema]:
    service = ReportService(db)
    report = await service.generate_report(request)
    return ApiResponse.ok(data=report, message=f"Report '{report.title}' generated successfully")


@router.get(
    "/download/{report_id}",
    summary="Download Audit Report Artifact",
    description="Streams actual compiled audit document (CSV, PDF, HTML) with verified attachment headers."
)
async def download_report_artifact(
    report_id: str,
    format: str = Query("csv", description="Format: csv, pdf, html, excel"),
    current_user: User = Depends(require_permissions("VIEW_REPORTS")),
    db: AsyncSession = Depends(get_db)
):
    from fastapi.responses import Response
    service = ReportService(db)
    content, filename, media_type = await service.download_report_file(report_id, format)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

