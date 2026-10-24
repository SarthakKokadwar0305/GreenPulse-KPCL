"""
GreenPulse AI - Common Pydantic Schemas
Generic response envelopes and industrial telemetry primitives.
"""
from datetime import datetime, timezone
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standardized API envelope for consistent enterprise JSON responses."""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def ok(cls, data: Optional[T] = None, message: str = "Operation completed successfully") -> "ApiResponse[T]":
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(cls, message: str = "An error occurred", data: Optional[T] = None) -> "ApiResponse[T]":
        return cls(success=False, message=message, data=data)


def api_success(data: Any = None, message: str = "Operation completed successfully") -> ApiResponse[Any]:
    return ApiResponse(success=True, message=message, data=data)


def api_error(message: str = "An error occurred", data: Any = None) -> ApiResponse[Any]:
    return ApiResponse(success=False, message=message, data=data)


class TrendIndicator(BaseModel):
    value: float
    direction: str  # 'up', 'down', 'flat'
    sentiment: str  # 'positive', 'negative', 'neutral'
    period: str  # e.g., 'vs baseline', 'vs last shift'


class StatusBadge(BaseModel):
    label: str
    tone: str  # 'success', 'warning', 'danger', 'info', 'neutral'
