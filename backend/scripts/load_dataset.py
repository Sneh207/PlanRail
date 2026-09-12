"""
load_dataset.py — PlanRail prototype dataset loader
====================================================

Loads the Delhi–Agra prototype dataset CSVs into the shared Supabase
PostgreSQL database using deterministic upsert (ON CONFLICT DO UPDATE).

Usage (from backend/ directory):
    python -m scripts.load_dataset --dataset-dir "C:\\path\\to\\dataset"

The loader is idempotent: running it twice against the same dataset will
not create duplicates or increase row counts.

Import order (dependency-safe):
    1.  stations
    2.  railway_sections
    3.  trains
    4.  train_schedules
    5.  assets
    6.  maintenance_requests
    7.  maintenance_history
    8.  crew_availability
    9.  task_compatibility  → maintenance_compatibility table
    10. traffic_windows
    11. maintenance_windows
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------------------
# Bootstrap: make sure app package is importable when running as a module
# from the backend/ directory.
# ---------------------------------------------------------------------------
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.config import settings  # noqa: E402  (import after sys.path fix)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
EXPECTED_COUNTS = {
    "stations": 18,
    "railway_sections": 17,
    "trains": 24,
    "train_schedules": 432,
    "assets": 85,
    "maintenance_requests": 150,
    "maintenance_history": 300,
    "crew_availability": 30,
    "maintenance_compatibility": 12,
    "traffic_windows": 408,
    "maintenance_windows": 408,
    "freight_train_movements": 36,
}

VALID_COMPATIBILITY_VALUES = {"COMPATIBLE", "CONDITIONAL", "INCOMPATIBLE"}


# ===========================================================================
# Utility helpers
# ===========================================================================

def parse_bool(value: str) -> bool:
    """Convert a CSV boolean string ('True'/'False') to a Python bool."""
    v = value.strip().lower()
    if v in ("true", "1", "yes"):
        return True
    if v in ("false", "0", "no"):
        return False
    raise ValueError(f"Cannot parse boolean from: {value!r}")


def parse_date_utc(value: str) -> datetime:
    """Parse a YYYY-MM-DD date string and return a UTC-aware datetime (midnight)."""
    d = date.fromisoformat(value.strip())
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)


def parse_float_or_none(value: str) -> float | None:
    """Parse float, return None if blank."""
    v = value.strip()
    return float(v) if v else None


def parse_int_or_none(value: str) -> int | None:
    """Parse int, return None if blank."""
    v = value.strip()
    return int(v) if v else None


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a CSV file and return a list of row dicts (all string values)."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def require_columns(rows: list[dict], required: list[str], filename: str) -> None:
    """Assert all required columns are present in the CSV header."""
    if not rows:
        raise ValueError(f"{filename}: file is empty")
    actual = set(rows[0].keys())
    missing = [c for c in required if c not in actual]
    if missing:
        raise ValueError(f"{filename}: missing columns: {missing}")


def check_unique(rows: list[dict], key: str, filename: str) -> None:
    """Assert no duplicate values for the given key column."""
    seen: set = set()
    dupes: list = []
    for row in rows:
        val = row[key]
        if val in seen:
            dupes.append(val)
        seen.add(val)
    if dupes:
        raise ValueError(f"{filename}: duplicate {key} values: {dupes[:5]}")


def check_fk(
    rows: list[dict],
    fk_col: str,
    ref_set: set,
    filename: str,
    ref_name: str,
) -> None:
    """Assert all fk_col values in rows exist in ref_set."""
    bad = [r[fk_col] for r in rows if r[fk_col] not in ref_set]
    if bad:
        raise ValueError(
            f"{filename}: {fk_col} references non-existent {ref_name}: "
            f"{bad[:5]}"
        )


def log_table(
    table: str,
    attempted: int,
    inserted: int,
    updated: int,
    skipped: int = 0,
) -> None:
    print(f"\nTable: {table}")
    print(f"  attempted : {attempted}")
    print(f"  inserted  : {inserted}")
    print(f"  updated   : {updated}")
    print(f"  skipped   : {skipped}")


def get_engine(database_url: str):
    url = database_url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return create_engine(url, pool_pre_ping=True, pool_recycle=300)


# ===========================================================================
# Phase 1: Pre-import validation
# ===========================================================================

def validate_all(dataset_dir: Path) -> dict[str, list[dict]]:
    """
    Read and validate all CSV files.  Returns a dict keyed by CSV filename
    (without extension) containing the validated rows.
    Raises ValueError on any validation failure — no DB writes occur.
    """
    print("\n-- Pre-import validation -----------------------------------------")

    def csv_path(name: str) -> Path:
        p = dataset_dir / name
        if not p.exists():
            raise FileNotFoundError(f"Required CSV not found: {p}")
        return p

    # -- stations --
    stations_rows = read_csv(csv_path("stations.csv"))
    require_columns(
        stations_rows,
        ["station_id", "station_code", "station_name", "latitude", "longitude", "km_from_ndls"],
        "stations.csv",
    )
    check_unique(stations_rows, "station_id", "stations.csv")
    check_unique(stations_rows, "station_code", "stations.csv")
    for r in stations_rows:
        float(r["latitude"])
        float(r["longitude"])
    station_codes = {r["station_code"] for r in stations_rows}
    print(f"  stations.csv          OK  ({len(stations_rows)} rows)")

    # -- railway_sections --
    sections_rows = read_csv(csv_path("railway_sections.csv"))
    require_columns(
        sections_rows,
        ["section_id", "from_station_code", "to_station_code", "distance_km"],
        "railway_sections.csv",
    )
    check_unique(sections_rows, "section_id", "railway_sections.csv")
    check_fk(sections_rows, "from_station_code", station_codes, "railway_sections.csv", "stations.station_code")
    check_fk(sections_rows, "to_station_code", station_codes, "railway_sections.csv", "stations.station_code")
    for r in sections_rows:
        float(r["distance_km"])
    section_ids = {r["section_id"] for r in sections_rows}
    print(f"  railway_sections.csv  OK  ({len(sections_rows)} rows)")

    # -- trains --
    trains_rows = read_csv(csv_path("trains.csv"))
    require_columns(
        trains_rows,
        ["train_number", "train_name", "train_type", "is_synthetic_schedule"],
        "trains.csv",
    )
    check_unique(trains_rows, "train_number", "trains.csv")
    for r in trains_rows:
        parse_bool(r["is_synthetic_schedule"])
    train_numbers = {r["train_number"] for r in trains_rows}
    print(f"  trains.csv            OK  ({len(trains_rows)} rows)")

    # -- train_schedules --
    schedules_rows = read_csv(csv_path("train_schedules.csv"))
    require_columns(
        schedules_rows,
        ["schedule_id", "train_number", "station_code", "sequence", "day"],
        "train_schedules.csv",
    )
    check_unique(schedules_rows, "schedule_id", "train_schedules.csv")
    check_fk(schedules_rows, "train_number", train_numbers, "train_schedules.csv", "trains.train_number")
    check_fk(schedules_rows, "station_code", station_codes, "train_schedules.csv", "stations.station_code")
    print(f"  train_schedules.csv   OK  ({len(schedules_rows)} rows)")

    # -- assets --
    assets_rows = read_csv(csv_path("assets.csv"))
    require_columns(
        assets_rows,
        ["asset_id", "section_id", "asset_type", "department"],
        "assets.csv",
    )
    check_unique(assets_rows, "asset_id", "assets.csv")
    check_fk(assets_rows, "section_id", section_ids, "assets.csv", "railway_sections.section_id")
    asset_ids = {r["asset_id"] for r in assets_rows}
    print(f"  assets.csv            OK  ({len(assets_rows)} rows)")

    # -- maintenance_requests --
    mr_rows = read_csv(csv_path("maintenance_requests.csv"))
    require_columns(
        mr_rows,
        [
            "request_id", "asset_id", "section_id", "department",
            "maintenance_type", "severity", "criticality_score",
            "duration_hours", "due_date", "overdue_days", "status",
        ],
        "maintenance_requests.csv",
    )
    check_unique(mr_rows, "request_id", "maintenance_requests.csv")
    check_fk(mr_rows, "asset_id", asset_ids, "maintenance_requests.csv", "assets.asset_id")
    check_fk(mr_rows, "section_id", section_ids, "maintenance_requests.csv", "railway_sections.section_id")
    for r in mr_rows:
        float(r["severity"])
        float(r["criticality_score"])
        float(r["duration_hours"])
        parse_date_utc(r["due_date"])
        if r.get("created_date", "").strip():
            parse_date_utc(r["created_date"])
    print(f"  maintenance_requests.csv OK ({len(mr_rows)} rows)")

    # -- maintenance_history --
    hist_rows = read_csv(csv_path("maintenance_history.csv"))
    require_columns(
        hist_rows,
        ["history_id", "asset_id", "section_id", "event_date", "event_type", "severity", "downtime_hours"],
        "maintenance_history.csv",
    )
    check_unique(hist_rows, "history_id", "maintenance_history.csv")
    check_fk(hist_rows, "asset_id", asset_ids, "maintenance_history.csv", "assets.asset_id")
    check_fk(hist_rows, "section_id", section_ids, "maintenance_history.csv", "railway_sections.section_id")
    for r in hist_rows:
        float(r["severity"])
        float(r["downtime_hours"])
        parse_date_utc(r["event_date"])
    print(f"  maintenance_history.csv  OK ({len(hist_rows)} rows)")

    # -- crew_availability --
    crew_rows = read_csv(csv_path("crew_availability.csv"))
    require_columns(
        crew_rows,
        ["crew_id", "crew_name", "department", "available_from_hour", "available_to_hour", "team_size"],
        "crew_availability.csv",
    )
    check_unique(crew_rows, "crew_id", "crew_availability.csv")
    for r in crew_rows:
        int(r["available_from_hour"])
        int(r["available_to_hour"])
        int(r["team_size"])
    print(f"  crew_availability.csv    OK ({len(crew_rows)} rows)")

    # -- task_compatibility --
    compat_rows = read_csv(csv_path("task_compatibility.csv"))
    require_columns(
        compat_rows,
        ["department_a", "department_b", "compatibility"],
        "task_compatibility.csv",
    )
    for r in compat_rows:
        val = r["compatibility"].strip()
        if val not in VALID_COMPATIBILITY_VALUES:
            raise ValueError(
                f"task_compatibility.csv: invalid compatibility value {val!r}. "
                f"Must be one of {VALID_COMPATIBILITY_VALUES}"
            )
    print(f"  task_compatibility.csv   OK ({len(compat_rows)} rows)")

    # -- traffic_windows --
    tw_rows = read_csv(csv_path("traffic_windows.csv"))
    require_columns(
        tw_rows,
        ["traffic_window_id", "section_id", "hour", "train_count", "traffic_level"],
        "traffic_windows.csv",
    )
    check_unique(tw_rows, "traffic_window_id", "traffic_windows.csv")
    check_fk(tw_rows, "section_id", section_ids, "traffic_windows.csv", "railway_sections.section_id")
    print(f"  traffic_windows.csv      OK ({len(tw_rows)} rows)")

    # -- maintenance_windows --
    mw_rows = read_csv(csv_path("maintenance_windows.csv"))
    require_columns(
        mw_rows,
        ["window_id", "section_id", "start_hour", "start_time", "end_time",
         "expected_train_count", "traffic_level", "is_feasible"],
        "maintenance_windows.csv",
    )
    check_unique(mw_rows, "window_id", "maintenance_windows.csv")
    check_fk(mw_rows, "section_id", section_ids, "maintenance_windows.csv", "railway_sections.section_id")
    for r in mw_rows:
        parse_bool(r["is_feasible"])
    # -- freight_train_movements (optional / simulated) --
    freight_rows = []
    freight_csv = dataset_dir / "PlanRail_Delhi_Agra_Freight_Trains_with_References.csv"
    if not freight_csv.is_file():
        freight_csv = dataset_dir.parent / "PlanRail_Delhi_Agra_Freight_Trains_with_References.csv"
    if freight_csv.is_file():
        freight_rows = read_csv(freight_csv)
        require_columns(
            freight_rows,
            ["freight_train_id", "movement_date", "origin_station_code", "destination_station_code", "commodity", "load_tonnes"],
            "PlanRail_Delhi_Agra_Freight_Trains_with_References.csv",
        )
        check_unique(freight_rows, "freight_train_id", "PlanRail_Delhi_Agra_Freight_Trains_with_References.csv")
        print(f"  PlanRail_Delhi_Agra_Freight_Trains_with_References.csv OK ({len(freight_rows)} rows)")

    print("\n  [OK] All pre-import validations passed.\n")

    return {
        "stations": stations_rows,
        "railway_sections": sections_rows,
        "trains": trains_rows,
        "train_schedules": schedules_rows,
        "assets": assets_rows,
        "maintenance_requests": mr_rows,
        "maintenance_history": hist_rows,
        "crew_availability": crew_rows,
        "task_compatibility": compat_rows,
        "traffic_windows": tw_rows,
        "maintenance_windows": mw_rows,
        "freight_train_movements": freight_rows,
    }


# ===========================================================================
# Phase 2: Loaders (one per table)
# ===========================================================================

def _upsert_result(conn, stmt) -> tuple[int, int]:
    result = conn.execute(stmt)
    return result.rowcount


def load_stations(conn, rows: list[dict]) -> tuple[int, int, int]:
    """Load stations.csv -> stations table.  Returns (attempted, inserted, updated)."""
    pre_count = conn.execute(text("SELECT COUNT(*) FROM stations")).scalar()
    records = []
    for r in rows:
        lon = float(r["longitude"])
        lat = float(r["latitude"])
        records.append({
            "station_id": r["station_id"].strip(),
            "station_code": r["station_code"].strip(),
            "station_name": r["station_name"].strip(),
            "name": r["station_name"].strip(),
            "latitude": lat,
            "longitude": lon,
            "km_from_ndls": parse_float_or_none(r.get("km_from_ndls", "")),
            "source_type": r.get("source_type", "").strip() or None,
            "source_note": r.get("source_note", "").strip() or None,
        })
    stmt = text(
        """
        INSERT INTO stations
            (station_id, station_code, station_name, name,
             latitude, longitude, km_from_ndls,
             source_type, source_note, location)
        VALUES
            (:station_id, :station_code, :station_name, :name,
             :latitude, :longitude, :km_from_ndls,
             :source_type, :source_note,
             ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326))
        ON CONFLICT (station_code) DO UPDATE SET
            station_id     = EXCLUDED.station_id,
            station_name   = EXCLUDED.station_name,
            name           = EXCLUDED.name,
            latitude       = EXCLUDED.latitude,
            longitude      = EXCLUDED.longitude,
            km_from_ndls   = EXCLUDED.km_from_ndls,
            source_type    = EXCLUDED.source_type,
            source_note    = EXCLUDED.source_note,
            location       = EXCLUDED.location,
            updated_at     = NOW()
        """
    )
    conn.execute(stmt, records)
    post_count = conn.execute(text("SELECT COUNT(*) FROM stations")).scalar()
    attempted = len(records)
    inserted = post_count - pre_count
    updated = attempted - inserted
    return attempted, inserted, updated


def load_railway_sections(conn, rows: list[dict]) -> tuple[int, int, int]:
    """Load railway_sections.csv -> railway_sections table."""
    pre_count = conn.execute(text("SELECT COUNT(*) FROM railway_sections")).scalar()
    records = []
    for r in rows:
        records.append({
            "section_id": r["section_id"].strip(),
            "section_code": r["section_id"].strip(),
            "from_station_code": r["from_station_code"].strip(),
            "to_station_code": r["to_station_code"].strip(),
            "from_station_name": r.get("from_station_name", "").strip() or None,
            "to_station_name": r.get("to_station_name", "").strip() or None,
            "distance_km": float(r["distance_km"]),
            "track_configuration": r.get("track_configuration", "").strip() or None,
            "electrification": r.get("electrification", "").strip() or None,
            "traffic_class": r.get("traffic_class", "").strip() or None,
        })
    stmt = text(
        """
        INSERT INTO railway_sections
            (section_id, section_code, from_station_code, to_station_code,
             from_station_name, to_station_name, distance_km,
             track_configuration, electrification, traffic_class,
             geometry)
        VALUES
            (:section_id, :section_code, :from_station_code, :to_station_code,
             :from_station_name, :to_station_name, :distance_km,
             :track_configuration, :electrification, :traffic_class,
             NULL)
        ON CONFLICT (section_id) DO UPDATE SET
            section_code       = EXCLUDED.section_code,
            from_station_code  = EXCLUDED.from_station_code,
            to_station_code    = EXCLUDED.to_station_code,
            from_station_name  = EXCLUDED.from_station_name,
            to_station_name    = EXCLUDED.to_station_name,
            distance_km        = EXCLUDED.distance_km,
            track_configuration = EXCLUDED.track_configuration,
            electrification    = EXCLUDED.electrification,
            traffic_class      = EXCLUDED.traffic_class,
            updated_at         = NOW()
        """
    )
    conn.execute(stmt, records)
    post_count = conn.execute(text("SELECT COUNT(*) FROM railway_sections")).scalar()
    attempted = len(records)
    inserted = post_count - pre_count
    updated = attempted - inserted
    return attempted, inserted, updated


def load_trains(conn, rows: list[dict]) -> tuple[int, int, int]:
    """Load trains.csv -> trains table."""
    pre_count = conn.execute(text("SELECT COUNT(*) FROM trains")).scalar()
    records = []
    for r in rows:
        records.append({
            "train_number": r["train_number"].strip(),
            "train_name": r["train_name"].strip(),
            "train_type": r["train_type"].strip(),
            "origin_code": r.get("origin_code", "").strip() or None,
            "destination_code": r.get("destination_code", "").strip() or None,
            "service_pattern": r.get("service_pattern", "").strip() or None,
            "is_synthetic_schedule": parse_bool(r["is_synthetic_schedule"]),
            "priority": 1,
        })
    stmt = text(
        """
        INSERT INTO trains
            (train_number, train_name, train_type,
             origin_code, destination_code, service_pattern,
             is_synthetic_schedule, priority)
        VALUES
            (:train_number, :train_name, :train_type,
             :origin_code, :destination_code, :service_pattern,
             :is_synthetic_schedule, :priority)
        ON CONFLICT (train_number) DO UPDATE SET
            train_name           = EXCLUDED.train_name,
            train_type           = EXCLUDED.train_type,
            origin_code          = EXCLUDED.origin_code,
            destination_code     = EXCLUDED.destination_code,
            service_pattern      = EXCLUDED.service_pattern,
            is_synthetic_schedule = EXCLUDED.is_synthetic_schedule,
            updated_at           = NOW()
        """
    )
    conn.execute(stmt, records)
    post_count = conn.execute(text("SELECT COUNT(*) FROM trains")).scalar()
    attempted = len(records)
    inserted = post_count - pre_count
    updated = attempted - inserted
    return attempted, inserted, updated


def load_train_schedules(conn, rows: list[dict]) -> tuple[int, int, int]:
    """Load train_schedules.csv -> train_schedules table."""
    pre_count = conn.execute(text("SELECT COUNT(*) FROM train_schedules")).scalar()
    records = []
    for r in rows:
        records.append({
            "schedule_id": r["schedule_id"].strip(),
            "train_number": r["train_number"].strip(),
            "station_code": r["station_code"].strip(),
            "station_name": r.get("station_name", "").strip() or None,
            "sequence": int(r["sequence"]),
            "arrival_time": r.get("arrival_time", "").strip() or None,
            "departure_time": r.get("departure_time", "").strip() or None,
            "day": int(r.get("day", "1") or "1"),
            "km_from_origin": parse_float_or_none(r.get("km_from_origin", "")),
        })
    stmt = text(
        """
        INSERT INTO train_schedules
            (schedule_id, train_number, station_code, station_name,
             sequence, arrival_time, departure_time, day, km_from_origin)
        VALUES
            (:schedule_id, :train_number, :station_code, :station_name,
             :sequence, :arrival_time, :departure_time, :day, :km_from_origin)
        ON CONFLICT (schedule_id) DO UPDATE SET
            train_number   = EXCLUDED.train_number,
            station_code   = EXCLUDED.station_code,
            station_name   = EXCLUDED.station_name,
            sequence       = EXCLUDED.sequence,
            arrival_time   = EXCLUDED.arrival_time,
            departure_time = EXCLUDED.departure_time,
            day            = EXCLUDED.day,
            km_from_origin = EXCLUDED.km_from_origin
        """
    )
    conn.execute(stmt, records)
    post_count = conn.execute(text("SELECT COUNT(*) FROM train_schedules")).scalar()
    attempted = len(records)
    inserted = post_count - pre_count
    updated = attempted - inserted
    return attempted, inserted, updated


def load_assets(conn, rows: list[dict]) -> tuple[int, int, int]:
    """Load assets.csv -> assets table."""
    pre_count = conn.execute(text("SELECT COUNT(*) FROM assets")).scalar()
    records = []
    for r in rows:
        lmd = r.get("last_maintenance_date", "").strip()
        records.append({
            "asset_id": r["asset_id"].strip(),
            "section_id": r["section_id"].strip(),
            "asset_type": r["asset_type"].strip(),
            "department": r["department"].strip(),
            "installation_year": parse_int_or_none(r.get("installation_year", "")),
            "condition_score": parse_float_or_none(r.get("condition_score", "")),
            "criticality": r.get("criticality", "").strip() or None,
            "last_maintenance_date": parse_date_utc(lmd) if lmd else None,
        })
    stmt = text(
        """
        INSERT INTO assets
            (asset_id, section_id, asset_type, department,
             installation_year, condition_score, criticality,
             last_maintenance_date)
        VALUES
            (:asset_id, :section_id, :asset_type, :department,
             :installation_year, :condition_score, :criticality,
             :last_maintenance_date)
        ON CONFLICT (asset_id) DO UPDATE SET
            section_id             = EXCLUDED.section_id,
            asset_type             = EXCLUDED.asset_type,
            department             = EXCLUDED.department,
            installation_year      = EXCLUDED.installation_year,
            condition_score        = EXCLUDED.condition_score,
            criticality            = EXCLUDED.criticality,
            last_maintenance_date  = EXCLUDED.last_maintenance_date,
            updated_at             = NOW()
        """
    )
    conn.execute(stmt, records)
    post_count = conn.execute(text("SELECT COUNT(*) FROM assets")).scalar()
    attempted = len(records)
    inserted = post_count - pre_count
    updated = attempted - inserted
    return attempted, inserted, updated


def load_maintenance_requests(conn, rows: list[dict]) -> tuple[int, int, int]:
    """Load maintenance_requests.csv -> maintenance_requests table."""
    pre_count = conn.execute(text("SELECT COUNT(*) FROM maintenance_requests")).scalar()
    records = []
    for r in rows:
        created_raw = r.get("created_date", "").strip()
        records.append({
            "request_id": r["request_id"].strip(),
            "asset_id": r["asset_id"].strip(),
            "section_id": r["section_id"].strip(),
            "department": r["department"].strip(),
            "asset_type": r.get("asset_type", "").strip() or None,
            "maintenance_type": r["maintenance_type"].strip(),
            "severity": float(r["severity"]),
            "criticality_score": float(r["criticality_score"]),
            "duration_hours": float(r["duration_hours"]),
            "created_date": parse_date_utc(created_raw) if created_raw else None,
            "due_date": parse_date_utc(r["due_date"]),
            "overdue_days": int(r.get("overdue_days", "0") or "0"),
            "baseline_risk_score": parse_float_or_none(r.get("baseline_risk_score", "")),
            "status": r.get("status", "PENDING").strip(),
            "crew_required": 1,
        })
    stmt = text(
        """
        INSERT INTO maintenance_requests
            (request_id, asset_id, section_id, department, asset_type,
             maintenance_type, severity, criticality_score, duration_hours,
             created_date, due_date, overdue_days, baseline_risk_score, status,
             crew_required)
        VALUES
            (:request_id, :asset_id, :section_id, :department, :asset_type,
             :maintenance_type, :severity, :criticality_score, :duration_hours,
             :created_date, :due_date, :overdue_days, :baseline_risk_score, :status,
             :crew_required)
        ON CONFLICT (request_id) DO UPDATE SET
            asset_id            = EXCLUDED.asset_id,
            section_id          = EXCLUDED.section_id,
            department          = EXCLUDED.department,
            asset_type          = EXCLUDED.asset_type,
            maintenance_type    = EXCLUDED.maintenance_type,
            severity            = EXCLUDED.severity,
            criticality_score   = EXCLUDED.criticality_score,
            duration_hours      = EXCLUDED.duration_hours,
            created_date        = EXCLUDED.created_date,
            due_date            = EXCLUDED.due_date,
            overdue_days        = EXCLUDED.overdue_days,
            baseline_risk_score = EXCLUDED.baseline_risk_score,
            status              = EXCLUDED.status,
            updated_at          = NOW()
        """
    )
    conn.execute(stmt, records)
    post_count = conn.execute(text("SELECT COUNT(*) FROM maintenance_requests")).scalar()
    attempted = len(records)
    inserted = post_count - pre_count
    updated = attempted - inserted
    return attempted, inserted, updated


def load_maintenance_history(conn, rows: list[dict]) -> tuple[int, int, int]:
    """Load maintenance_history.csv -> maintenance_history table."""
    pre_count = conn.execute(text("SELECT COUNT(*) FROM maintenance_history")).scalar()
    records = []
    for r in rows:
        records.append({
            "history_id": r["history_id"].strip(),
            "asset_id": r["asset_id"].strip(),
            "section_id": r["section_id"].strip(),
            "event_date": parse_date_utc(r["event_date"]),
            "event_type": r["event_type"].strip(),
            "severity": float(r["severity"]),
            "downtime_hours": float(r["downtime_hours"]),
        })
    stmt = text(
        """
        INSERT INTO maintenance_history
            (history_id, asset_id, section_id, event_date,
             event_type, severity, downtime_hours)
        VALUES
            (:history_id, :asset_id, :section_id, :event_date,
             :event_type, :severity, :downtime_hours)
        ON CONFLICT (history_id) DO UPDATE SET
            asset_id      = EXCLUDED.asset_id,
            section_id    = EXCLUDED.section_id,
            event_date    = EXCLUDED.event_date,
            event_type    = EXCLUDED.event_type,
            severity      = EXCLUDED.severity,
            downtime_hours = EXCLUDED.downtime_hours
        """
    )
    conn.execute(stmt, records)
    post_count = conn.execute(text("SELECT COUNT(*) FROM maintenance_history")).scalar()
    attempted = len(records)
    inserted = post_count - pre_count
    updated = attempted - inserted
    return attempted, inserted, updated


def load_crew_availability(conn, rows: list[dict]) -> tuple[int, int, int]:
    """Load crew_availability.csv -> crew_availability table."""
    pre_count = conn.execute(text("SELECT COUNT(*) FROM crew_availability")).scalar()
    records = []
    for r in rows:
        records.append({
            "crew_id": r["crew_id"].strip(),
            "crew_name": r["crew_name"].strip(),
            "department": r["department"].strip(),
            "available_from_hour": int(r["available_from_hour"]),
            "available_to_hour": int(r["available_to_hour"]),
            "team_size": int(r["team_size"]),
        })
    stmt = text(
        """
        INSERT INTO crew_availability
            (crew_id, crew_name, department,
             available_from_hour, available_to_hour, team_size)
        VALUES
            (:crew_id, :crew_name, :department,
             :available_from_hour, :available_to_hour, :team_size)
        ON CONFLICT (crew_id) DO UPDATE SET
            crew_name          = EXCLUDED.crew_name,
            department         = EXCLUDED.department,
            available_from_hour = EXCLUDED.available_from_hour,
            available_to_hour  = EXCLUDED.available_to_hour,
            team_size          = EXCLUDED.team_size
        """
    )
    conn.execute(stmt, records)
    post_count = conn.execute(text("SELECT COUNT(*) FROM crew_availability")).scalar()
    attempted = len(records)
    inserted = post_count - pre_count
    updated = attempted - inserted
    return attempted, inserted, updated


def load_task_compatibility(conn, rows: list[dict]) -> tuple[int, int, int]:
    """Load task_compatibility.csv -> maintenance_compatibility table.
    compatibility is VARCHAR(50); preserve COMPATIBLE/CONDITIONAL as-is.
    Sets legacy compatible column to True to satisfy NOT NULL constraint.
    """
    pre_count = conn.execute(text("SELECT COUNT(*) FROM maintenance_compatibility")).scalar()
    records = []
    for r in rows:
        records.append({
            "department_a": r["department_a"].strip(),
            "department_b": r["department_b"].strip(),
            "compatibility": r["compatibility"].strip(),
            "compatible": True,
            "reason": r.get("reason", "").strip() or None,
        })
    stmt = text(
        """
        INSERT INTO maintenance_compatibility
            (department_a, department_b, compatibility, compatible, reason)
        VALUES
            (:department_a, :department_b, :compatibility, :compatible, :reason)
        ON CONFLICT ON CONSTRAINT uq_department_pair DO UPDATE SET
            compatibility = EXCLUDED.compatibility,
            compatible    = EXCLUDED.compatible,
            reason        = EXCLUDED.reason
        """
    )
    conn.execute(stmt, records)
    post_count = conn.execute(text("SELECT COUNT(*) FROM maintenance_compatibility")).scalar()
    attempted = len(records)
    inserted = post_count - pre_count
    updated = attempted - inserted
    return attempted, inserted, updated


def load_traffic_windows(conn, rows: list[dict]) -> tuple[int, int, int]:
    """Load traffic_windows.csv -> traffic_windows table."""
    pre_count = conn.execute(text("SELECT COUNT(*) FROM traffic_windows")).scalar()
    records = []
    for r in rows:
        records.append({
            "traffic_window_id": r["traffic_window_id"].strip(),
            "section_id": r["section_id"].strip(),
            "hour": int(r["hour"]),
            "train_count": int(r["train_count"]),
            "traffic_level": r["traffic_level"].strip(),
        })
    stmt = text(
        """
        INSERT INTO traffic_windows
            (traffic_window_id, section_id, hour, train_count, traffic_level)
        VALUES
            (:traffic_window_id, :section_id, :hour, :train_count, :traffic_level)
        ON CONFLICT (traffic_window_id) DO UPDATE SET
            section_id    = EXCLUDED.section_id,
            hour          = EXCLUDED.hour,
            train_count   = EXCLUDED.train_count,
            traffic_level = EXCLUDED.traffic_level
        """
    )
    conn.execute(stmt, records)
    post_count = conn.execute(text("SELECT COUNT(*) FROM traffic_windows")).scalar()
    attempted = len(records)
    inserted = post_count - pre_count
    updated = attempted - inserted
    return attempted, inserted, updated


def load_maintenance_windows(conn, rows: list[dict]) -> tuple[int, int, int]:
    """Load maintenance_windows.csv -> maintenance_windows table."""
    pre_count = conn.execute(text("SELECT COUNT(*) FROM maintenance_windows")).scalar()
    records = []
    for r in rows:
        records.append({
            "window_id": r["window_id"].strip(),
            "section_id": r["section_id"].strip(),
            "start_hour": int(r["start_hour"]),
            "start_time": r["start_time"].strip(),
            "end_time": r["end_time"].strip(),
            "expected_train_count": int(r["expected_train_count"]),
            "traffic_level": r["traffic_level"].strip(),
            "is_feasible": parse_bool(r["is_feasible"]),
            "window_reason": r.get("window_reason", "").strip() or None,
        })
    stmt = text(
        """
        INSERT INTO maintenance_windows
            (window_id, section_id, start_hour, start_time, end_time,
             expected_train_count, traffic_level, is_feasible, window_reason)
        VALUES
            (:window_id, :section_id, :start_hour, :start_time, :end_time,
             :expected_train_count, :traffic_level, :is_feasible, :window_reason)
        ON CONFLICT (window_id) DO UPDATE SET
            section_id           = EXCLUDED.section_id,
            start_hour           = EXCLUDED.start_hour,
            start_time           = EXCLUDED.start_time,
            end_time             = EXCLUDED.end_time,
            expected_train_count = EXCLUDED.expected_train_count,
            traffic_level        = EXCLUDED.traffic_level,
            is_feasible          = EXCLUDED.is_feasible,
            window_reason        = EXCLUDED.window_reason,
            updated_at           = NOW()
        """
    )
    conn.execute(stmt, records)
    post_count = conn.execute(text("SELECT COUNT(*) FROM maintenance_windows")).scalar()
    attempted = len(records)
    inserted = post_count - pre_count
    updated = attempted - inserted
    return attempted, inserted, updated


def load_freight_train_movements(conn, rows: list[dict]) -> tuple[int, int, int]:
    """Load simulated freight trains CSV -> freight_train_movements table."""
    if not rows:
        return 0, 0, 0
    # Ensure table exists
    conn.execute(text(
        """
        CREATE TABLE IF NOT EXISTS freight_train_movements (
            freight_train_id TEXT PRIMARY KEY,
            movement_date DATE NOT NULL,
            origin_station_code TEXT NOT NULL,
            destination_station_code TEXT NOT NULL,
            commodity TEXT NOT NULL,
            load_tonnes DOUBLE PRECISION NOT NULL,
            planned_entry_time TEXT NOT NULL,
            planned_exit_time TEXT NOT NULL,
            traffic_priority TEXT NOT NULL,
            corridor TEXT NOT NULL DEFAULT 'Delhi-Agra',
            data_status TEXT NOT NULL DEFAULT 'SIMULATED_BY_PLANRAIL',
            source_basis TEXT NOT NULL,
            planning_use TEXT NOT NULL,
            simulation_note TEXT NOT NULL,
            reference_1 TEXT,
            reference_1_url TEXT,
            reference_2 TEXT,
            reference_2_url TEXT,
            reference_3 TEXT,
            reference_3_url TEXT,
            reference_4 TEXT,
            reference_4_url TEXT
        )
        """
    ))
    pre_count = conn.execute(text("SELECT COUNT(*) FROM freight_train_movements")).scalar()
    records = []
    for r in rows:
        raw_date = r.get("movement_date", "").strip()
        parsed_date = date.fromisoformat(raw_date) if raw_date else date.today()
        records.append({
            "freight_train_id": r["freight_train_id"].strip(),
            "movement_date": parsed_date,
            "origin_station_code": r["origin_station_code"].strip(),
            "destination_station_code": r["destination_station_code"].strip(),
            "commodity": r.get("commodity", "General").strip(),
            "load_tonnes": float(r.get("load_tonnes", 0.0) or 0.0),
            "planned_entry_time": r.get("planned_entry_time", "00:00").strip(),
            "planned_exit_time": r.get("planned_exit_time", "04:00").strip(),
            "traffic_priority": r.get("traffic_priority", "Medium").strip(),
            "corridor": r.get("corridor", "Delhi-Agra").strip(),
            "data_status": r.get("data_status", "SIMULATED_BY_PLANRAIL").strip(),
            "source_basis": r.get("source_basis", "PlanRail synthetic freight dataset").strip(),
            "planning_use": r.get("planning_use", "Traffic conflict and maintenance-block optimization").strip(),
            "simulation_note": r.get("simulation_note", "Synthetic planning scenario; not real FOIS record.").strip(),
            "reference_1": r.get("reference_1"),
            "reference_1_url": r.get("reference_1_url"),
            "reference_2": r.get("reference_2"),
            "reference_2_url": r.get("reference_2_url"),
            "reference_3": r.get("reference_3"),
            "reference_3_url": r.get("reference_3_url"),
            "reference_4": r.get("reference_4"),
            "reference_4_url": r.get("reference_4_url"),
        })
    stmt = text(
        """
        INSERT INTO freight_train_movements
            (freight_train_id, movement_date, origin_station_code, destination_station_code,
             commodity, load_tonnes, planned_entry_time, planned_exit_time, traffic_priority,
             corridor, data_status, source_basis, planning_use, simulation_note,
             reference_1, reference_1_url, reference_2, reference_2_url,
             reference_3, reference_3_url, reference_4, reference_4_url)
        VALUES
            (:freight_train_id, :movement_date, :origin_station_code, :destination_station_code,
             :commodity, :load_tonnes, :planned_entry_time, :planned_exit_time, :traffic_priority,
             :corridor, :data_status, :source_basis, :planning_use, :simulation_note,
             :reference_1, :reference_1_url, :reference_2, :reference_2_url,
             :reference_3, :reference_3_url, :reference_4, :reference_4_url)
        ON CONFLICT (freight_train_id) DO UPDATE SET
            movement_date            = EXCLUDED.movement_date,
            origin_station_code      = EXCLUDED.origin_station_code,
            destination_station_code = EXCLUDED.destination_station_code,
            commodity                = EXCLUDED.commodity,
            load_tonnes              = EXCLUDED.load_tonnes,
            planned_entry_time       = EXCLUDED.planned_entry_time,
            planned_exit_time        = EXCLUDED.planned_exit_time,
            traffic_priority         = EXCLUDED.traffic_priority,
            corridor                 = EXCLUDED.corridor,
            data_status              = EXCLUDED.data_status,
            source_basis             = EXCLUDED.source_basis,
            planning_use             = EXCLUDED.planning_use,
            simulation_note          = EXCLUDED.simulation_note,
            reference_1              = EXCLUDED.reference_1,
            reference_1_url          = EXCLUDED.reference_1_url,
            reference_2              = EXCLUDED.reference_2,
            reference_2_url          = EXCLUDED.reference_2_url,
            reference_3              = EXCLUDED.reference_3,
            reference_3_url          = EXCLUDED.reference_3_url,
            reference_4              = EXCLUDED.reference_4,
            reference_4_url          = EXCLUDED.reference_4_url
        """
    )
    conn.execute(stmt, records)
    post_count = conn.execute(text("SELECT COUNT(*) FROM freight_train_movements")).scalar()
    attempted = len(records)
    inserted = post_count - pre_count
    updated = attempted - inserted
    return attempted, inserted, updated



# ===========================================================================
# Phase 3: Post-import validation
# ===========================================================================

def validate_post_import(conn) -> bool:
    """
    Verify row counts and important FK relationships after import.
    Returns True if all checks pass.
    """
    print("\n-- Post-import validation ----------------------------------------")
    all_ok = True

    # 1. Row counts
    print("\n  Row counts:")
    for table, expected in EXPECTED_COUNTS.items():
        actual = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        ok = actual == expected
        mark = "[OK]" if ok else "[FAIL]"
        print(f"  {mark}  {table:<30} expected={expected}  actual={actual}")
        if not ok:
            all_ok = False

    # 2. FK: railway_sections -> stations
    print("\n  FK: railway_sections.from/to_station_code -> stations.station_code")
    bad = conn.execute(text(
        """
        SELECT COUNT(*) FROM railway_sections rs
        WHERE NOT EXISTS (
            SELECT 1 FROM stations s WHERE s.station_code = rs.from_station_code
        ) OR NOT EXISTS (
            SELECT 1 FROM stations s WHERE s.station_code = rs.to_station_code
        )
        """
    )).scalar()
    _fk_check("railway_sections -> stations", bad, all_ok)
    if bad:
        all_ok = False

    # 3. FK: assets -> railway_sections
    bad = conn.execute(text(
        """
        SELECT COUNT(*) FROM assets a
        WHERE NOT EXISTS (
            SELECT 1 FROM railway_sections rs WHERE rs.section_id = a.section_id
        )
        """
    )).scalar()
    _fk_check("assets -> railway_sections", bad, all_ok)
    if bad:
        all_ok = False

    # 4. FK: maintenance_requests -> assets, sections
    bad = conn.execute(text(
        """
        SELECT COUNT(*) FROM maintenance_requests mr
        WHERE NOT EXISTS (SELECT 1 FROM assets a WHERE a.asset_id = mr.asset_id)
           OR NOT EXISTS (SELECT 1 FROM railway_sections rs WHERE rs.section_id = mr.section_id)
        """
    )).scalar()
    _fk_check("maintenance_requests -> assets/sections", bad, all_ok)
    if bad:
        all_ok = False

    # 5. FK: maintenance_history -> assets, sections
    bad = conn.execute(text(
        """
        SELECT COUNT(*) FROM maintenance_history mh
        WHERE NOT EXISTS (SELECT 1 FROM assets a WHERE a.asset_id = mh.asset_id)
           OR NOT EXISTS (SELECT 1 FROM railway_sections rs WHERE rs.section_id = mh.section_id)
        """
    )).scalar()
    _fk_check("maintenance_history -> assets/sections", bad, all_ok)
    if bad:
        all_ok = False

    # 6. FK: train_schedules -> trains, stations
    bad = conn.execute(text(
        """
        SELECT COUNT(*) FROM train_schedules ts
        WHERE NOT EXISTS (SELECT 1 FROM trains t WHERE t.train_number = ts.train_number)
           OR NOT EXISTS (SELECT 1 FROM stations s WHERE s.station_code = ts.station_code)
        """
    )).scalar()
    _fk_check("train_schedules -> trains/stations", bad, all_ok)
    if bad:
        all_ok = False

    # 7. FK: traffic_windows -> railway_sections
    bad = conn.execute(text(
        """
        SELECT COUNT(*) FROM traffic_windows tw
        WHERE NOT EXISTS (SELECT 1 FROM railway_sections rs WHERE rs.section_id = tw.section_id)
        """
    )).scalar()
    _fk_check("traffic_windows -> railway_sections", bad, all_ok)
    if bad:
        all_ok = False

    # 8. FK: maintenance_windows -> railway_sections
    bad = conn.execute(text(
        """
        SELECT COUNT(*) FROM maintenance_windows mw
        WHERE NOT EXISTS (SELECT 1 FROM railway_sections rs WHERE rs.section_id = mw.section_id)
        """
    )).scalar()
    _fk_check("maintenance_windows -> railway_sections", bad, all_ok)
    if bad:
        all_ok = False

    # 9. PostGIS: station locations
    print("\n  PostGIS station locations:")
    total = conn.execute(text("SELECT COUNT(*) FROM stations")).scalar()
    with_geom = conn.execute(text(
        "SELECT COUNT(*) FROM stations WHERE location IS NOT NULL"
    )).scalar()
    srid_ok = conn.execute(text(
        "SELECT COUNT(*) FROM stations WHERE ST_SRID(location) = 4326"
    )).scalar()
    mark = "[OK]" if (with_geom == total and srid_ok == total) else "[FAIL]"
    print(f"  {mark}  stations with geometry: {with_geom}/{total}  SRID=4326: {srid_ok}/{total}")
    if with_geom != total or srid_ok != total:
        all_ok = False

    # 10. Railway section geometry -- must remain NULL
    print("\n  Railway section geometry (must remain NULL):")
    with_geom = conn.execute(text(
        "SELECT COUNT(*) FROM railway_sections WHERE geometry IS NOT NULL"
    )).scalar()
    mark = "[OK]" if with_geom == 0 else "[FAIL]"
    print(f"  {mark}  sections with geometry: {with_geom} (expected 0)")
    if with_geom != 0:
        all_ok = False

    # 11. Verify ai_training_features not imported
    print("\n  ai_training_features.csv: NOT imported (no target table exists) [OK]")

    return all_ok


def _fk_check(label: str, bad_count: int, _all_ok: bool) -> None:
    mark = "[OK]" if bad_count == 0 else "[FAIL]"
    print(f"  {mark}  {label}: {bad_count} broken FK rows")


# ===========================================================================
# Main entry point
# ===========================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load PlanRail prototype dataset into Supabase PostgreSQL."
    )
    parser.add_argument(
        "--dataset-dir",
        required=True,
        help="Path to the directory containing the CSV files.",
    )
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir).resolve()
    if not dataset_dir.is_dir():
        print(f"ERROR: dataset-dir does not exist or is not a directory: {dataset_dir}")
        sys.exit(1)

    if not settings.DATABASE_URL:
        print("ERROR: DATABASE_URL is not set. Check backend/.env")
        sys.exit(1)

    print(f"\n{'=' * 65}")
    print("  PlanRail Dataset Loader")
    print(f"{'=' * 65}")
    print(f"  Dataset dir : {dataset_dir}")
    print(f"  Database    : {settings.DATABASE_URL[:40]}...")
    print(f"{'=' * 65}")

    # Phase 1: validate -- no DB writes yet
    try:
        all_data = validate_all(dataset_dir)
    except (ValueError, FileNotFoundError) as exc:
        print(f"\nVALIDATION ERROR: {exc}")
        print("No data was written to the database.")
        sys.exit(1)

    # Phase 2: import inside a single connection (per-table transactions)
    engine = get_engine(settings.DATABASE_URL)

    print("-- Importing tables ----------------------------------------------")

    load_steps = [
        ("stations",              load_stations,              all_data["stations"]),
        ("railway_sections",      load_railway_sections,      all_data["railway_sections"]),
        ("trains",                load_trains,                all_data["trains"]),
        ("train_schedules",       load_train_schedules,       all_data["train_schedules"]),
        ("assets",                load_assets,                all_data["assets"]),
        ("maintenance_requests",  load_maintenance_requests,  all_data["maintenance_requests"]),
        ("maintenance_history",   load_maintenance_history,   all_data["maintenance_history"]),
        ("crew_availability",     load_crew_availability,     all_data["crew_availability"]),
        ("maintenance_compatibility", load_task_compatibility, all_data["task_compatibility"]),
        ("traffic_windows",       load_traffic_windows,       all_data["traffic_windows"]),
        ("maintenance_windows",   load_maintenance_windows,   all_data["maintenance_windows"]),
        ("freight_train_movements", load_freight_train_movements, all_data["freight_train_movements"]),
    ]

    total_attempted = total_inserted = total_updated = 0

    for table_name, loader_fn, rows in load_steps:
        try:
            with engine.begin() as conn:  # auto-commits or rolls back per table
                attempted, inserted, updated = loader_fn(conn, rows)
            log_table(table_name, attempted, inserted, updated)
            total_attempted += attempted
            total_inserted += inserted
            total_updated += updated
        except Exception as exc:
            print(f"\n  [FAILED] loading {table_name}: {exc}")
            print("  The transaction for this table has been rolled back.")
            print("  Previously completed tables are committed.")
            sys.exit(1)

    print(f"\n-- Import totals -------------------------------------------------")
    print(f"  attempted : {total_attempted}")
    print(f"  inserted  : {total_inserted}")
    print(f"  updated   : {total_updated}")

    # Phase 3: post-import validation
    with engine.connect() as conn:
        ok = validate_post_import(conn)

    if ok:
        print(f"\n{'=' * 65}")
        print("  [OK] Dataset import SUCCESSFUL -- all validation checks passed.")
        print(f"{'=' * 65}\n")
    else:
        print(f"\n{'=' * 65}")
        print("  [FAIL] Import completed but some validation checks FAILED.")
        print("    Review the output above for details.")
        print(f"{'=' * 65}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
