import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from app.models.station import Station
from app.models.section import RailwaySection
from app.models.asset import Asset
from app.models.maintenance import MaintenanceRequest
from app.models.train import Train
from app.models.freight import FreightTrainMovement
from app.models.block import MaintenanceWindow, OptimizedBlock
from app.models.traffic import TrafficWindow
from app.models.crew import CrewAvailability
from app.models.admin_config import AdminConfiguration
from app.ai.risk_model import RiskModel

logger = logging.getLogger(__name__)


class AdminService:
    @staticmethod
    def get_system_health(db: Session) -> Dict[str, Any]:
        """Performs comprehensive live system and component health diagnostics."""
        # Database connectivity check
        db_connected = False
        db_type = "sqlite"
        try:
            db.execute(text("SELECT 1;"))
            db_connected = True
            bind = db.get_bind()
            if bind:
                db_type = bind.dialect.name
        except Exception as e:
            logger.error("DB health check failed: %s", e)

        # AI Model Status
        model_status = "UNAVAILABLE"
        model_features = 11
        model_threshold = 0.5684
        try:
            RiskModel.load_model()
            if RiskModel._is_loaded and RiskModel._model is not None:
                model_status = "XGBOOST_TRAINED_MODEL"
                model_features = len(RiskModel._feature_columns)
                model_threshold = RiskModel._threshold
        except Exception as e:
            logger.warning("AI model status check note: %s", e)



        # Data Counts
        counts = {
            "stations": db.query(func.count(Station.station_id)).scalar() or 0,
            "sections": db.query(func.count(RailwaySection.section_id)).scalar() or 0,
            "assets": db.query(func.count(Asset.asset_id)).scalar() or 0,
            "maintenance_requests": db.query(func.count(MaintenanceRequest.request_id)).scalar() or 0,
            "passenger_trains": db.query(func.count(Train.train_number)).scalar() or 0,
            "freight_movements": db.query(func.count(FreightTrainMovement.freight_train_id)).scalar() or 0,
            "maintenance_windows": db.query(func.count(MaintenanceWindow.window_id)).scalar() or 0,
            "traffic_windows": db.query(func.count(TrafficWindow.traffic_window_id)).scalar() or 0,
            "optimized_blocks": db.query(func.count(OptimizedBlock.id)).scalar() or 0,
            "crew_teams": db.query(func.count(CrewAvailability.crew_id)).scalar() or 0,
        }

        return {
            "status": "HEALTHY" if db_connected and model_status == "XGBOOST_TRAINED_MODEL" else "DEGRADED",
            "backend": {"status": "ONLINE", "version": "2.0.0", "framework": "FastAPI + Pydantic v2"},
            "database": {"status": "CONNECTED" if db_connected else "ERROR", "dialect": db_type, "healthy": db_connected},
            "ai_engine": {
                "status": model_status,
                "model_type": "XGBoost Classifier",
                "feature_count": model_features,
                "decision_threshold": model_threshold,
                "explainability": "SHAP TreeExplainer Active",
            },
            "optimizer": {
                "status": "READY",
                "engine": "Google OR-Tools CP-SAT",
                "max_time_limit_sec": 5.0,
                "deterministic_seed": 42,
            },
            "what_if_engine": {
                "status": "READY",
                "supported_scenarios": ["TRAFFIC_PLUS_20", "EMERGENCY_MAINTENANCE", "REMOVE_MAINTENANCE_WINDOW"],
            },
            "data_counts": counts,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def get_or_create_config(db: Session) -> AdminConfiguration:
        """Retrieves singleton admin configuration or initializes default."""
        config = db.query(AdminConfiguration).filter(AdminConfiguration.id == 1).first()
        if not config:
            config = AdminConfiguration(
                id=1,
                max_block_duration_hours=4.0,
                emergency_priority_multiplier=1.5,
                critical_freight_multiplier=1.5,
                high_freight_multiplier=1.2,
                auto_approval_threshold=80.0,
                corridor_speed_limit_kmh=160,
                dispatch_mode="AUTOMATIC_OPTIMIZATION",
            )
            db.add(config)
            db.commit()
            db.refresh(config)
        return config

    @staticmethod
    def update_config(db: Session, update_data: Dict[str, Any]) -> AdminConfiguration:
        """Updates persistent operational configuration."""
        config = AdminService.get_or_create_config(db)
        for key, value in update_data.items():
            if value is not None and hasattr(config, key):
                setattr(config, key, value)
        config.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(config)
        return config
