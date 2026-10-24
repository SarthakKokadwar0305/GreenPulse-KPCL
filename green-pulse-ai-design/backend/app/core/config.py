"""
GreenPulse AI - Core Application Configuration
Enterprise settings powered by Pydantic Settings.
"""
from pathlib import Path
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # Application Information
    APP_NAME: str = "GreenPulse AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str = "greenpulse-enterprise-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    # Default to SQLite for seamless local development, supports asyncpg PostgreSQL
    DATABASE_URL: str = "sqlite+aiosqlite:///./greenpulse.db"
    DB_ECHO: bool = False

    # Datasets and ML Models
    DATASET_DIR: str = "./datasets"
    TRAINED_MODELS_DIR: str = "./trained_models"

    # Plant Constants
    PLANT_CODE: str = "FAC-IND-PUN-004"
    PLANT_NAME: str = "GreenPulse Heavy Machinery Plant #4"
    CONTRACTED_PEAK_DEMAND_KW: float = 2500.0
    BASE_TARIFF_INR: float = 7.20
    PEAK_TARIFF_MULTIPLIER: float = 1.44
    GRID_EMISSION_FACTOR_KG_KWH: float = 0.82

    # AI Copilot & RAG Pipeline
    QDRANT_PATH: str = "./qdrant_storage"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma3:4b"
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-m3"
    DOCUMENTS_DIR: str = "./knowledge_documents"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]

    @property
    def PROJECT_NAME(self) -> str:
        return self.APP_NAME

    @property
    def ENVIRONMENT(self) -> str:
        return self.APP_ENV

    @property
    def cors_origins_list(self) -> List[str]:
        return self.CORS_ORIGINS

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
