"""
GreenPulse AI - Report Pydantic Schemas
Contracts for generated compliance documents and standing automated pipelines.
"""
from typing import List, Optional
from pydantic import BaseModel


class ReportSummaryStat(BaseModel):
    label: str
    value: str


class IndustrialReportSchema(BaseModel):
    id: str
    title: str
    category: str
    period: str
    generated_at: str
    author: str
    file_size: str
    status: str
    download_url: Optional[str] = None
    summary_stats: List[ReportSummaryStat]


class ScheduledReportSchema(BaseModel):
    id: str
    name: str
    frequency: str
    send_time: str
    recipients: List[str]
    format: str
    category: str
    active: bool
    last_sent: str


class GenerateReportRequest(BaseModel):
    category: str  # energy, carbon, forecast, anomaly
    title: Optional[str] = None
    period_start: str
    period_end: str
    format: str = "PDF"


class ReportsListResponse(BaseModel):
    recent_reports: List[IndustrialReportSchema]
    scheduled_reports: List[ScheduledReportSchema]
