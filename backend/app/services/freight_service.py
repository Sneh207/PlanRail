"""
PlanRail Freight Train Service
==============================

Provides domain querying and traffic calculation routines for synthetic freight planning train records.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Dict, List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.freight import FreightTrainMovement

logger = logging.getLogger(__name__)


class FreightService:
    @staticmethod
    def get_freight_movements(
        db: Session,
        movement_date: Optional[date] = None,
        traffic_priority: Optional[str] = None,
        commodity: Optional[str] = None,
        origin_station_code: Optional[str] = None,
        destination_station_code: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[FreightTrainMovement], int]:
        """
        Retrieves paginated freight train planning movements with optional filtering.
        """
        query = db.query(FreightTrainMovement)

        if movement_date:
            query = query.filter(FreightTrainMovement.movement_date == movement_date)
        if traffic_priority:
            query = query.filter(
                func.lower(FreightTrainMovement.traffic_priority) == traffic_priority.strip().lower()
            )
        if commodity:
            query = query.filter(
                func.lower(FreightTrainMovement.commodity) == commodity.strip().lower()
            )
        if origin_station_code:
            query = query.filter(
                func.upper(FreightTrainMovement.origin_station_code) == origin_station_code.strip().upper()
            )
        if destination_station_code:
            query = query.filter(
                func.upper(FreightTrainMovement.destination_station_code) == destination_station_code.strip().upper()
            )

        total = query.count()
        items = (
            query.order_by(
                FreightTrainMovement.movement_date.asc(),
                FreightTrainMovement.planned_entry_time.asc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    @staticmethod
    def get_freight_movement_by_id(
        db: Session,
        freight_train_id: str,
    ) -> Optional[FreightTrainMovement]:
        """Fetches a single freight movement by its unique ID."""
        return (
            db.query(FreightTrainMovement)
            .filter(FreightTrainMovement.freight_train_id == freight_train_id.strip())
            .first()
        )

    @staticmethod
    def get_hourly_freight_traffic(
        db: Session,
        target_date: date,
    ) -> Dict[int, float]:
        """
        Calculates hourly traffic pressure for a given date from synthetic freight planning movements.
        
        Priority Weight Multipliers:
          - Critical: 1.5
          - High: 1.2
          - Medium / other: 1.0

        Returns:
            Dictionary mapping hour (0-23) -> cumulative weighted freight traffic count.
        """
        hourly_traffic: Dict[int, float] = {h: 0.0 for h in range(24)}
        try:
            movements = (
                db.query(FreightTrainMovement)
                .filter(FreightTrainMovement.movement_date == target_date)
                .all()
            )
        except Exception:
            db.rollback()
            return hourly_traffic

        if not movements:
            return hourly_traffic

        for m in movements:
            try:
                entry_parts = [int(p) for p in m.planned_entry_time.split(":")]
                exit_parts = [int(p) for p in m.planned_exit_time.split(":")]
                entry_hour = entry_parts[0]
                exit_hour = exit_parts[0]
            except Exception:
                continue

            priority_lower = m.traffic_priority.lower()
            if "critical" in priority_lower:
                weight = 1.5
            elif "high" in priority_lower:
                weight = 1.2
            else:
                weight = 1.0

            # Mark all active hours in the movement interval
            if exit_hour >= entry_hour:
                for h in range(entry_hour, min(24, exit_hour + 1)):
                    hourly_traffic[h] += weight
            else:
                # Spans across midnight
                for h in range(entry_hour, 24):
                    hourly_traffic[h] += weight
                for h in range(0, exit_hour + 1):
                    hourly_traffic[h] += weight

        return hourly_traffic
