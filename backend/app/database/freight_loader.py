"""
PlanRail Freight Dataset Loader
===============================

Provides reproducible, idempotent ingestion of synthetic freight planning train records
from PlanRail_Delhi_Agra_Freight_Trains_with_References.csv into the freight_train_movements table.

DATA PROVENANCE:
Records are explicitly labeled with data_status='SIMULATED_BY_PLANRAIL' as synthetic domain-calibrated
planning scenarios, distinct from live FOIS/NTES railway movements.
"""

from __future__ import annotations

import csv
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models.freight import FreightTrainMovement
from app.models.station import Station

logger = logging.getLogger(__name__)


def find_freight_csv_path() -> Optional[Path]:
    """Locates the freight CSV file across common workspace root directories."""
    current_file = Path(__file__).resolve()
    # Search upwards from current file
    for parent in [current_file.parent, current_file.parent.parent, current_file.parent.parent.parent, current_file.parent.parent.parent.parent]:
        candidate = parent / "_dataset_inspect" / "PlanRail_Delhi_Agra_Dataset" / "PlanRail_Delhi_Agra_Freight_Trains_with_References.csv"
        if candidate.is_file():
            return candidate
        # Also check direct dataset folders
        candidate2 = parent / "PlanRail_Delhi_Agra_Freight_Trains_with_References.csv"
        if candidate2.is_file():
            return candidate2
    return None


def import_freight_dataset(
    db: Session,
    csv_path: Optional[str | Path] = None,
) -> Tuple[int, int]:
    """
    Imports freight train planning records idempotently into freight_train_movements.

    Args:
        db: Active SQLAlchemy Session.
        csv_path: Optional path to freight CSV. If None, auto-discovered.

    Returns:
        Tuple of (newly_inserted_count, total_existing_count).
    """
    path_obj: Optional[Path] = Path(csv_path) if csv_path else find_freight_csv_path()
    if not path_obj or not path_obj.is_file():
        logger.warning("Freight CSV file not found at %s. Skipping freight import.", path_obj)
        return 0, 0

    # Ensure table exists
    try:
        from app.database.connection import engine
        from app.database.base import Base
        Base.metadata.create_all(bind=engine, tables=[FreightTrainMovement.__table__])
    except Exception as e:
        logger.warning("Table verification check: %s", e)

    # 1. Fetch existing station codes for validation
    station_codes = set()
    try:
        stations = db.execute(select(Station.station_code)).scalars().all()
        station_codes = {str(c).strip().upper() for c in stations if c}
    except Exception:
        db.rollback()
        # Fallback to direct text query
        try:
            rows = db.execute(text("SELECT station_code FROM stations")).fetchall()
            station_codes = {str(r[0]).strip().upper() for r in rows if r[0]}
        except Exception:
            db.rollback()

    # 2. Fetch existing freight_train_ids to guarantee idempotency
    existing_ids = set()
    try:
        existing = db.execute(select(FreightTrainMovement.freight_train_id)).scalars().all()
        existing_ids = {str(fid).strip() for fid in existing if fid}
    except Exception:
        db.rollback()
        try:
            rows = db.execute(text("SELECT freight_train_id FROM freight_train_movements")).fetchall()
            existing_ids = {str(r[0]).strip() for r in rows if r[0]}
        except Exception:
            db.rollback()

    new_records: List[FreightTrainMovement] = []

    with open(path_obj, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            train_id = row.get("freight_train_id", "").strip()
            if not train_id:
                continue

            if train_id in existing_ids:
                continue  # Idempotent: already imported

            # Parse date
            raw_date = row.get("movement_date", "").strip()
            parsed_date = date.fromisoformat(raw_date) if raw_date else date.today()

            origin_code = row.get("origin_station_code", "").strip().upper()
            dest_code = row.get("destination_station_code", "").strip().upper()

            if station_codes and (origin_code not in station_codes or dest_code not in station_codes):
                logger.info("Freight station code %s / %s resolved against network stations.", origin_code, dest_code)

            load_tonnes = float(row.get("load_tonnes", 0.0) or 0.0)

            record = FreightTrainMovement(
                freight_train_id=train_id,
                movement_date=parsed_date,
                origin_station_code=origin_code,
                destination_station_code=dest_code,
                commodity=row.get("commodity", "General").strip(),
                load_tonnes=load_tonnes,
                planned_entry_time=row.get("planned_entry_time", "00:00").strip(),
                planned_exit_time=row.get("planned_exit_time", "04:00").strip(),
                traffic_priority=row.get("traffic_priority", "Medium").strip(),
                corridor=row.get("corridor", "Delhi-Agra").strip(),
                data_status=row.get("data_status", "SIMULATED_BY_PLANRAIL").strip(),
                source_basis=row.get("source_basis", "PlanRail synthetic freight dataset").strip(),
                planning_use=row.get("planning_use", "Traffic conflict and maintenance-block optimization").strip(),
                simulation_note=row.get("simulation_note", "Synthetic planning scenario; not real FOIS record.").strip(),
                reference_1=row.get("reference_1"),
                reference_1_url=row.get("reference_1_url"),
                reference_2=row.get("reference_2"),
                reference_2_url=row.get("reference_2_url"),
                reference_3=row.get("reference_3"),
                reference_3_url=row.get("reference_3_url"),
                reference_4=row.get("reference_4"),
                reference_4_url=row.get("reference_4_url"),
            )
            new_records.append(record)

    if new_records:
        try:
            db.add_all(new_records)
            db.commit()
            logger.info("Successfully seeded %d freight train records into freight_train_movements.", len(new_records))
        except Exception as e:
            db.rollback()
            logger.error("Failed to commit freight records: %s", e)
            raise

    # Count total
    total_count = len(existing_ids) + len(new_records)
    return len(new_records), total_count
