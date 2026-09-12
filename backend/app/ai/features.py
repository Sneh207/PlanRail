"""
PlanRail Feature Engineering Pipeline
=====================================

Extracts, normalizes, and computes domain-specific features from
MaintenanceRequest, Asset, Section, Freight, and MaintenanceHistory database entities.
Produces the exact 11-feature contract required by the trained XGBoost model.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.freight import FreightTrainMovement
from app.models.history import MaintenanceHistory
from app.models.maintenance import MaintenanceRequest
from app.models.section import RailwaySection as Section
from app.models.traffic import TrafficWindow

logger = logging.getLogger(__name__)


def clip_scale(val: float, low: float, high: float) -> float:
    """Clips and normalizes a value to [0.0, 100.0] scale."""
    if high <= low:
        return 0.0
    normalized = ((val - low) / (high - low)) * 100.0
    return max(0.0, min(100.0, normalized))


def extract_features(db: Session, request: MaintenanceRequest) -> Dict[str, Any]:
    """
    Extracts raw, normalized, and model-input features for a single MaintenanceRequest.

    Returns a comprehensive feature dictionary including:
      - Raw database fields
      - 11 features matching the XGBoost trained model contract
      - Normalized [0, 100] decision-support indicators
      - Derived domain risk ratios
    """
    # 1. Severity extraction & normalization
    raw_severity = float(request.severity) if request.severity is not None else 5.0
    # For model (1-10 scale):
    model_severity = raw_severity if raw_severity <= 10.0 else raw_severity / 10.0
    model_severity = max(1.0, min(10.0, model_severity))
    # Normalized [0, 100]
    severity_norm = clip_scale(model_severity, 1.0, 10.0)

    # 2. Criticality extraction & normalization
    raw_criticality = (
        float(request.criticality_score)
        if request.criticality_score is not None
        else 5.0
    )
    model_criticality = raw_criticality if raw_criticality <= 10.0 else raw_criticality / 10.0
    model_criticality = max(1.0, min(10.0, model_criticality))
    criticality_norm = clip_scale(model_criticality, 1.0, 10.0)

    # 3. Overdue days extraction & normalization
    raw_overdue_days = int(request.overdue_days) if request.overdue_days is not None else 0
    model_overdue_days = max(0.0, float(raw_overdue_days))
    overdue_norm = clip_scale(model_overdue_days, 0.0, 60.0)

    # 4. Fetch associated Asset
    asset: Optional[Asset] = None
    if request.asset_id:
        asset = db.query(Asset).filter(Asset.asset_id == request.asset_id).first()

    current_year = 2026  # PlanRail epoch
    if asset and asset.installation_year:
        asset_age_years = max(1.0, float(current_year - asset.installation_year))
    else:
        asset_age_years = 10.0

    if asset and asset.condition_score is not None:
        raw_condition_score = float(asset.condition_score)
    else:
        raw_condition_score = 75.0

    model_condition_score = max(10.0, min(100.0, raw_condition_score))
    condition_risk = max(0.0, min(100.0, 100.0 - model_condition_score))
    asset_age_norm = clip_scale(asset_age_years, 0.0, 30.0)

    # 5. Fetch associated Historical Events & defects
    historical_failures_count = 0
    total_past_downtime = 0.0
    if request.asset_id:
        history_records = (
            db.query(MaintenanceHistory)
            .filter(MaintenanceHistory.asset_id == request.asset_id)
            .all()
        )
        historical_failures_count = len(history_records)
        total_past_downtime = sum(float(h.downtime_hours or 0.0) for h in history_records)

    model_historical_failures = min(float(historical_failures_count), 10.0)
    model_previous_defects = min(float(historical_failures_count + (1 if raw_severity >= 7.0 else 0)), 10.0)

    # 6. Fetch Corridor Traffic & Freight Density
    section_id = request.section_id or ""
    # Query traffic windows for section or use domain baseline for Delhi–Agra
    traffic_windows = (
        db.query(TrafficWindow)
        .filter(TrafficWindow.section_id == section_id)
        .all()
        if section_id
        else []
    )
    if traffic_windows:
        avg_trains = sum(float(tw.train_count or 0.0) for tw in traffic_windows) / len(traffic_windows)
        train_density = max(15.0, min(115.0, avg_trains * 8.0))
    else:
        train_density = 55.0  # Delhi–Agra corridor mean passenger density

    # Query Freight movements
    freight_count = (
        db.query(FreightTrainMovement)
        .filter(
            (FreightTrainMovement.origin_station_code.isnot(None))
        )
        .count()
    )
    freight_density = max(15.0, min(110.0, float(freight_count) * 1.5))
    total_density = train_density + freight_density
    freight_share = (freight_density / total_density * 100.0) if total_density > 0 else 48.0

    # Maintenance cycle frequency (standard months or weeks)
    maintenance_frequency = 6.0

    # Derived domain indicators
    failure_rate = min(
        (model_historical_failures / max(asset_age_years, 1.0)) * 20.0,
        100.0,
    )
    overdue_ratio = min((model_overdue_days / (maintenance_frequency * 30.0)) * 100.0, 100.0)
    duration_hours = float(request.duration_hours) if request.duration_hours is not None else 2.0
    duration_norm = clip_scale(duration_hours, 0.5, 8.0)

    return {
        "request_id": request.request_id,
        "asset_id": request.asset_id,
        "section_id": request.section_id,
        "department": request.department,
        "asset_type": request.asset_type or (asset.asset_type if asset else "UNKNOWN"),

        # ── 11 Canonical XGBoost Model Feature Vector ──
        "condition_score": model_condition_score,
        "severity": model_severity,
        "criticality": model_criticality,
        "overdue_days": model_overdue_days,
        "historical_failures": model_historical_failures,
        "train_density": train_density,
        "freight_train_density": freight_density,
        "freight_share_percent": freight_share,
        "asset_age": asset_age_years,
        "maintenance_frequency": maintenance_frequency,
        "previous_defects": model_previous_defects,

        # ── Raw Reference Values ──
        "raw_severity": raw_severity,
        "raw_criticality": raw_criticality,
        "raw_overdue_days": raw_overdue_days,
        "raw_condition_score": raw_condition_score,
        "asset_age_years": asset_age_years,
        "historical_event_count": historical_failures_count,
        "total_past_downtime": total_past_downtime,
        "duration_hours": duration_hours,

        # ── Normalized Values [0, 100] ──
        "severity_norm": round(severity_norm, 2),
        "criticality_norm": round(criticality_norm, 2),
        "overdue_norm": round(overdue_norm, 2),
        "condition_risk": round(condition_risk, 2),
        "asset_age_norm": round(asset_age_norm, 2),
        "failure_rate": round(failure_rate, 2),
        "overdue_ratio": round(overdue_ratio, 2),
        "duration_norm": round(duration_norm, 2),
    }
