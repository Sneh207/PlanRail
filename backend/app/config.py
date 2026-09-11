from pathlib import Path
import json
from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_default_sqlite_url() -> str:
    """Safely resolve the absolute path to the local demo SQLite database."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    sqlite_file = base_dir / "_dataset_inspect" / "PlanRail_Delhi_Agra_Dataset" / "planrail_demo.sqlite"
    return f"sqlite:///{sqlite_file.as_posix()}"


class Settings(BaseSettings):
    PROJECT_NAME: str = "PlanRail Backend API"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def set_default_database_url(cls, v: Optional[str]) -> str:
        if v and str(v).strip():
            return str(v).strip()
        return get_default_sqlite_url()

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("["):
                return json.loads(v)
            return [i.strip() for i in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

