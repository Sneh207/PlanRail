"""
PlanRail Traffic Disruption & Operational Impact Engine
======================================================

Quantifies operational disruption to track sections from passenger and freight traffic.
Integrates timetable windows with FreightService synthetic freight planning movements.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.traffic import TrafficWindow
from app.models.block import MaintenanceWindow
from app.services.freight_service import FreightService

logger = logging.getLogger(__name__)


class TrafficImpactModel:
    """
    Traffic Disruption Engine combining passenger schedules and synthetic freight planning movements.
    """

    # Analytical weights from BACKEND_README.md
    WEIGHT_TRAINS = 0.30
    WEIGHT_HEADWAY = 0.25
    WEIGHT_PEAK = 0.20
    WEIGHT_UTIL = 0.15
    WEIGHT_DELAY = 0.10

    @classmethod
    def calculate_traffic_impact(
        cls,
        db: Session,
        section_id: str,
        duration_hours: float = 2.0,
        target_date: Optional[date] = None,
        preferred_start_hour: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Calculates operational traffic impact for a maintenance task on a given section.
        """
        if target_date is None:
            target_date = date(2026, 9, 15)  # Corridor default planning date
        elif isinstance(target_date, str):
            try:
                target_date = date.fromisoformat(target_date)
            except Exception:
                target_date = date(2026, 9, 15)

        # 1. Query passenger traffic windows for this section
        traffic_windows = (
            db.query(TrafficWindow)
            .filter(TrafficWindow.section_id == section_id)
            .all()
        )

        avg_hourly_passenger_trains = 0.0
        max_hourly_passenger_trains = 0
        if traffic_windows:
            counts = [w.train_count for w in traffic_windows]
            avg_hourly_passenger_trains = sum(counts) / len(counts)
            max_hourly_passenger_trains = max(counts)

        # 2. Query freight traffic pressure from FreightService
        freight_hourly = FreightService.get_hourly_freight_traffic(db, target_date)
        avg_freight_hourly = (
            sum(freight_hourly.values()) / 24.0 if freight_hourly else 0.0
        )

        # 3. Determine hour window to evaluate
        if preferred_start_hour is not None:
            eval_hour = preferred_start_hour
        else:
            # Default to midday or morning operational block window
            eval_hour = 11

        passenger_trains_in_window = 0
        for w in traffic_windows:
            if w.hour == eval_hour:
                passenger_trains_in_window = w.train_count
                break
        if passenger_trains_in_window == 0 and traffic_windows:
            passenger_trains_in_window = round(avg_hourly_passenger_trains)

        freight_trains_in_window = freight_hourly.get(eval_hour, 0.0)
        total_trains_in_window = float(passenger_trains_in_window) + freight_trains_in_window

        # 4. Compute 5 analytical components (all 0-100 scale)
        # W_trains: Train count factor
        w_trains = min(100.0, (total_trains_in_window / 4.0) * 100.0)

        # W_headway: Headway disruption ratio (duration / avg_headway)
        # Typical Delhi-Agra headway ~15-20 min (0.33 hours)
        avg_headway_hours = 0.33
        headway_ratio = duration_hours / avg_headway_hours
        w_headway = min(100.0, (headway_ratio / 6.0) * 100.0)

        # W_peak: Peak penalty (Morning 06-10, Evening 17-21)
        is_peak = (6 <= eval_hour <= 10) or (17 <= eval_hour <= 21)
        w_peak = 100.0 if is_peak else 15.0

        # W_util: Section utilization factor
        w_util = min(100.0, (max_hourly_passenger_trains / 5.0) * 100.0)

        # W_delay: Delay cascade penalty = trains * (duration * 0.5) * 1.3
        expected_cascade_delay_minutes = total_trains_in_window * (duration_hours * 30.0) * 1.3
        w_delay = min(100.0, (expected_cascade_delay_minutes / 120.0) * 100.0)

        # Combined analytical traffic impact score
        impact_score = (
            cls.WEIGHT_TRAINS * w_trains
            + cls.WEIGHT_HEADWAY * w_headway
            + cls.WEIGHT_PEAK * w_peak
            + cls.WEIGHT_UTIL * w_util
            + cls.WEIGHT_DELAY * w_delay
        )
        impact_score = round(max(0.0, min(100.0, impact_score)), 2)

        # Traffic category
        if impact_score >= 75.0:
            category = "CRITICAL"
        elif impact_score >= 50.0:
            category = "HIGH"
        elif impact_score >= 25.0:
            category = "MEDIUM"
        else:
            category = "LOW"

        # Explain factors
        factors = []
        if is_peak:
            factors.append(f"Window falls in peak operational hours ({eval_hour:02d}:00 hrs)")
        else:
            factors.append(f"Off-peak operational window ({eval_hour:02d}:00 hrs)")

        if passenger_trains_in_window > 0:
            factors.append(f"{passenger_trains_in_window} scheduled passenger train path{'s' if passenger_trains_in_window > 1 else ''} in window")

        if freight_trains_in_window > 0:
            factors.append(f"{freight_trains_in_window:.1f} synthetic freight planning movement paths in sector")

        if duration_hours > 3.0:
            factors.append(f"Extended block possession duration ({duration_hours:.1f} hrs) elevates cascade delay")

        return {
            "traffic_impact_score": impact_score,
            "traffic_impact_category": category,
            "passenger_train_pressure": round(float(passenger_trains_in_window), 1),
            "freight_train_pressure": round(float(freight_trains_in_window), 1),
            "total_train_pressure": round(total_trains_in_window, 1),
            "is_peak_window": is_peak,
            "expected_cascade_delay_minutes": round(expected_cascade_delay_minutes, 1),
            "traffic_components": {
                "train_density": round(w_trains, 1),
                "headway_severance": round(w_headway, 1),
                "peak_penalty": round(w_peak, 1),
                "section_utilization": round(w_util, 1),
                "delay_cascade": round(w_delay, 1),
            },
            "traffic_factors": factors,
        }
