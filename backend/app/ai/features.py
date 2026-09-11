"""
PlanRail Feature Engineering Pipeline
=====================================

Extracts, normalizes, and computes domain-specific features from
MaintenanceRequest, Asset, and MaintenanceHistory database entities.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.history import MaintenanceHistory
from app.models.maintenance import MaintenanceRequest

logger = logging.getLogger(__name__)


def clip_scale(val: float, low: float, high: float) -> float:
    """Clips and normalizes a value to [0.0, 100.0] scale."""
    if high <= low:
        return 0.0
    normalized = ((val - low) / (high - low)) * 100.0
    return max(0.0, min(100.0, normalized))


def extract_features(db: Session, request: MaintenanceRequest) -> Dict[str, Any]:
    """
    Extracts raw and normalized features for a single MaintenanceRequest.

    Returns a feature dictionary containing:
      - Raw database fields
      - Normalized [0, 100] features
      - Derived domain indicators (condition_risk, failure_rate, overdue_ratio)
    """
    # 1. Severity normalization
    raw_severity = float(request.severity) if request.severity is not None else 50.0
    # In DB, severity can be 1-10 or 0-100. If <= 10, scale to 0-100
    if raw_severity <= 10.0:
        severity_norm = clip_scale(raw_severity, 1.0, 10.0)
    else:
        severity_norm = clip_scale(raw_severity, 0.0, 100.0)

    # 2. Criticality normalization
    raw_criticality = (
        float(request.criticality_score)
        if request.criticality_score is not None
        else 50.0
    )
    if raw_criticality <= 10.0:
        criticality_norm = clip_scale(raw_criticality, 1.0, 10.0)
    else:
        criticality_norm = clip_scale(raw_criticality, 0.0, 100.0)

    # 3. Overdue days normalization
    raw_overdue_days = int(request.overdue_days) if request.overdue_days is not None else 0
    # 0 to 60 days standard normalization
    overdue_norm = clip_scale(float(raw_overdue_days), 0.0, 60.0)

    # 4. Fetch associated Asset
    asset: Optional[Asset] = None
    if request.asset_id:
        asset = db.query(Asset).filter(Asset.asset_id == request.asset_id).first()

    current_year = 2026  # PlanRail planning epoch
    if asset and asset.installation_year:
        asset_age_years = max(1, current_year - asset.installation_year)
    else:
        asset_age_years = 10  # Domain default

    if asset and asset.condition_score is not None:
        raw_condition_score = float(asset.condition_score)
    else:
        raw_condition_score = 75.0  # Domain default moderate health

    condition_risk = max(0.0, min(100.0, 100.0 - raw_condition_score))
    asset_age_norm = clip_scale(float(asset_age_years), 0.0, 30.0)

    # 5. Fetch associated Historical Events
    historical_failures_count = 0
    total_past_downtime = 0.0
    if request.asset_id:
        history_records = (
            db.query(MaintenanceHistory)
            .filter(MaintenanceHistory.asset_id == request.asset_id)
            .all()
        )
        historical_failures_count = len(history_records)
        total_past_downtime = sum(float(h.downtime_hours) for h in history_records)

    # failure_rate = min((historical_failures / max(asset_age, 1)) * 20, 100)
    failure_rate = min(
        (float(historical_failures_count) / max(float(asset_age_years), 1.0)) * 20.0,
        100.0,
    )

    # overdue_ratio = min((overdue_days / (maintenance_frequency * 30)) * 100, 100)
    # Default monthly frequency (1.0)
    overdue_ratio = min((float(raw_overdue_days) / 30.0) * 100.0, 100.0)

    # Duration
    duration_hours = float(request.duration_hours) if request.duration_hours is not None else 2.0
    duration_norm = clip_scale(duration_hours, 0.5, 8.0)

    return {
        "request_id": request.request_id,
        "asset_id": request.asset_id,
        "section_id": request.section_id,
        "department": request.department,
        "asset_type": request.asset_type or (asset.asset_type if asset else "UNKNOWN"),
        # Raw features
        "raw_severity": raw_severity,
        "raw_criticality": raw_criticality,
        "raw_overdue_days": raw_overdue_days,
        "raw_condition_score": raw_condition_score,
        "asset_age_years": asset_age_years,
        "historical_event_count": historical_failures_count,
        "total_past_downtime": total_past_downtime,
        "duration_hours": duration_hours,
        # Normalized features [0, 100]
        "severity_norm": round(severity_norm, 2),
        "criticality_norm": round(criticality_norm, 2),
        "overdue_norm": round(overdue_norm, 2),
        "condition_risk": round(condition_risk, 2),
        "asset_age_norm": round(asset_age_norm, 2),
        "failure_rate": round(failure_rate, 2),
        "overdue_ratio": round(overdue_ratio, 2),
        "duration_norm": round(duration_norm, 2),
    }
