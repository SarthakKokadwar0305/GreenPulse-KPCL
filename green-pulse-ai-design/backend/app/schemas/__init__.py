"""
GreenPulse AI - Schemas Package
Exports all Pydantic request and response models.
"""
from app.schemas.common import ApiResponse, TrendIndicator, StatusBadge
from app.schemas.dashboard import (
    KpiMetricSchema,
    PlantStatusMetricSchema,
    SystemStatusSchema,
    DashboardOverviewResponse,
)
from app.schemas.plant import (
    ProductionSummarySchema,
    DepartmentOverviewSchema,
    UtilityConsumptionSchema,
    ActiveUtilityAssetSchema,
    ShiftInformationSchema,
    FactoryTimelineEventSchema,
    PlantOverviewResponse,
)
from app.schemas.machine import (
    VoltageBalance,
    PhaseCurrent,
    MaintenanceRecordSchema,
    MachineInsightSchema,
    MachineTimelineState,
    MachineDetailSchema,
)
from app.schemas.energy import (
    HourlyUsagePoint,
    DailyUsagePoint,
    WeeklyUsagePoint,
    MonthlyUsagePoint,
    MachineComparisonPoint,
    DepartmentComparisonPoint,
    PeakDemandAnalyticsSchema,
    HeatmapDayRow,
    EnergyAnalyticsResponse,
)
from app.schemas.carbon import (
    Scope1Breakdown,
    Scope2Breakdown,
    CarbonTrendPoint,
    CarbonByMachinePoint,
    CarbonByDepartmentPoint,
    EsgOverviewSchema,
    CarbonAccountingResponse,
)
from app.schemas.forecast import (
    HourlyForecastPoint,
    PrimaryDriverSchema,
    AiExplanationSchema,
    ForecastTimelineMilestoneSchema,
    ForecastResponse,
)
from app.schemas.anomaly import (
    AnomalyEvidenceItem,
    AnomalyIncidentSchema,
    AcknowledgeAnomalyRequest,
    CreateWorkOrderRequest,
)
from app.schemas.recommendation import (
    RecommendationSchema,
    ApplyRecommendationRequest,
)
from app.schemas.simulation import (
    SimulationRequest,
    HourlySimulationPoint,
    SimulationResponse,
)
from app.schemas.report import (
    IndustrialReportSchema,
    ScheduledReportSchema,
    GenerateReportRequest,
    ReportsListResponse,
)

__all__ = [
    "ApiResponse",
    "TrendIndicator",
    "StatusBadge",
    "KpiMetricSchema",
    "PlantStatusMetricSchema",
    "SystemStatusSchema",
    "DashboardOverviewResponse",
    "ProductionSummarySchema",
    "DepartmentOverviewSchema",
    "UtilityConsumptionSchema",
    "ActiveUtilityAssetSchema",
    "ShiftInformationSchema",
    "FactoryTimelineEventSchema",
    "PlantOverviewResponse",
    "VoltageBalance",
    "PhaseCurrent",
    "MaintenanceRecordSchema",
    "MachineInsightSchema",
    "MachineTimelineState",
    "MachineDetailSchema",
    "HourlyUsagePoint",
    "DailyUsagePoint",
    "WeeklyUsagePoint",
    "MonthlyUsagePoint",
    "MachineComparisonPoint",
    "DepartmentComparisonPoint",
    "PeakDemandAnalyticsSchema",
    "HeatmapDayRow",
    "EnergyAnalyticsResponse",
    "Scope1Breakdown",
    "Scope2Breakdown",
    "CarbonTrendPoint",
    "CarbonByMachinePoint",
    "CarbonByDepartmentPoint",
    "EsgOverviewSchema",
    "CarbonAccountingResponse",
    "HourlyForecastPoint",
    "PrimaryDriverSchema",
    "AiExplanationSchema",
    "ForecastTimelineMilestoneSchema",
    "ForecastResponse",
    "AnomalyEvidenceItem",
    "AnomalyIncidentSchema",
    "AcknowledgeAnomalyRequest",
    "CreateWorkOrderRequest",
    "RecommendationSchema",
    "ApplyRecommendationRequest",
    "SimulationRequest",
    "HourlySimulationPoint",
    "SimulationResponse",
    "IndustrialReportSchema",
    "ScheduledReportSchema",
    "GenerateReportRequest",
    "ReportsListResponse",
]
