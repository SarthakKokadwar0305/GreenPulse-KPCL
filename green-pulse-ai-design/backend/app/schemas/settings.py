"""
GreenPulse AI - Settings Pydantic Schemas
Contracts for industrial plant parameters, SCADA integration, and security controls.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class PlantSettingsSchema(BaseModel):
    facility_name: str = "GreenPulse Central Hub - Unit 4"
    facility_code: str = "FAC-MH-PUN-04"
    location: str = "MIDC Industrial Area, Pune, Maharashtra, India"
    contracted_demand_kw: float = Field(default=2500.0, ge=100.0, le=50000.0)
    utility_account: str = "MSEDCL-HT-99214482"
    substation_feeder: str = "33kV Express Feeder Line #2"
    operating_shifts: str = "3-Shift Continuous (24x7)"
    electricity_tariff: float = Field(default=7.20, ge=1.0, le=30.0)
    carbon_target_tons: float = Field(default=4.8, ge=0.0)
    renewable_share_percent: float = Field(default=22.0, ge=0.0, le=100.0)


class NotificationSettingsSchema(BaseModel):
    warning_threshold_kw: float = Field(default=2200.0, ge=50.0, le=50000.0)
    power_factor_minimum: float = Field(default=0.92, ge=0.5, le=1.0)
    webhook_url: str = "https://scada-relay.internal.greenpulse.ai/v1/alerts"
    email_recipients: List[str] = [
        "plant.director@greenpulse.ai",
        "energy.manager@greenpulse.ai"
    ]


class ApiGatewaySettingsSchema(BaseModel):
    scada_host: str = "192.168.10.45"
    scada_port: int = Field(default=502, ge=1, le=65535)
    opc_ua_endpoint: str = "opc.tcp://192.168.10.12:4840/GreenPulse/Server"
    mqtt_broker_url: str = "mqtts://edge-broker.internal.greenpulse.ai:8883"
    api_key_masked: str = "gp_live_99f8a32b**********************"


class SystemSettingsResponse(BaseModel):
    plant: PlantSettingsSchema
    notifications: NotificationSettingsSchema
    api: ApiGatewaySettingsSchema
    last_updated: Optional[str] = None


class UpdateSystemSettingsRequest(BaseModel):
    plant: Optional[PlantSettingsSchema] = None
    notifications: Optional[NotificationSettingsSchema] = None
    api: Optional[ApiGatewaySettingsSchema] = None
