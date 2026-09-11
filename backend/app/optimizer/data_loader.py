"""
PlanRail Optimizer Data Loader
==============================

Extracts, validates, and transforms database records into pure data structures
suitable for the CP-SAT MaintenanceBlockSolver.
Works seamlessly across PostgreSQL (with PostGIS/Alembic) and SQLite.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy import select, text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.models.block import MaintenanceWindow
from app.models.compatibility import MaintenanceCompatibility
from app.models.maintenance import MaintenanceRequest
from app.models.section import RailwaySection
from app.models.traffic import TrafficWindow
from app.optimizer.solver import (
    MaintenanceRequestInput,
    MaintenanceWindowInput,
    TrafficWindowInput,
)


def parse_time_to_minutes(time_val: Optional[Any], default_hour: int = 0) -> Tuple[int, int]:
    """
    Parses a time string ("HH:MM", "HH:MM:SS") or returns (default_hour, 0).
    Returns (hour, minute).
    """
    if not time_val:
        return default_hour, 0
    try:
        parts = str(time_val).strip().split(":")
        if len(parts) >= 2:
            return int(parts[0]), int(parts[1])
        if len(parts) == 1 and parts[0].isdigit():
            return int(parts[0]), 0
    except (ValueError, TypeError):
        pass
    return default_hour, 0


def parse_datetime_flexible(val: Any) -> Optional[datetime]:
    """Parses datetime strings (ISO format) or datetime objects and ensures UTC awareness."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val if val.tzinfo is not None else val.replace(tzinfo=timezone.utc)
    if isinstance(val, date):
        return datetime(val.year, val.month, val.day, tzinfo=timezone.utc)
    try:
        clean_str = str(val).strip()
        if "T" in clean_str or " " in clean_str:
            clean_str = clean_str.replace(" ", "T")
            if clean_str.endswith("Z"):
                clean_str = clean_str[:-1] + "+00:00"
            dt = datetime.fromisoformat(clean_str)
            return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)
        d = date.fromisoformat(clean_str)
        return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
    except Exception:
        return None


class OptimizerDataLoader:
    """Loads and converts PlanRail domain entities for solver consumption."""

    def __init__(self, db: Session):
        self.db = db

    def load_section_mappings(self) -> Tuple[Dict[str, int], Dict[str, str]]:
        """
        Loads all railway sections.
        Returns:
            code_to_id: mapping from section_code/section_id to database integer PK id (or synthetic index)
            section_codes: dictionary of available section codes
        """
        code_to_id: Dict[str, int] = {}
        section_codes: Dict[str, str] = {}

        try:
            # First try ORM query (PostgreSQL schema)
            sections = self.db.execute(select(RailwaySection.id, RailwaySection.section_id)).all()
            for row in sections:
                sec_db_id, sec_code = row[0], row[1]
                code_to_id[sec_code] = sec_db_id
                section_codes[sec_code] = sec_code
        except Exception:
            # Fallback for raw SQL / SQLite schema without 'id' column
            self.db.rollback()
            rows = self.db.execute(text("SELECT section_id FROM railway_sections")).fetchall()
            for idx, r in enumerate(rows, start=1):
                sec_code = str(r[0]).strip()
                code_to_id[sec_code] = idx
                section_codes[sec_code] = sec_code

        return code_to_id, section_codes

    def load_compatibility_rules(self) -> Dict[Tuple[str, str], str]:
        """
        Loads cross-department compatibility pairs.
        Returns mapping from (dept_a, dept_b) -> "COMPATIBLE" | "CONDITIONAL" | "INCOMPATIBLE".
        """
        rules: Dict[Tuple[str, str], str] = {}
        rows = []

        try:
            rows = self.db.execute(
                text("SELECT department_a, department_b, compatibility FROM maintenance_compatibility")
            ).fetchall()
        except Exception:
            self.db.rollback()
            try:
                rows = self.db.execute(
                    text("SELECT department_a, department_b, compatibility FROM task_compatibility")
                ).fetchall()
            except Exception:
                self.db.rollback()

        for r in rows:
            dept_a = str(r[0]).strip()
            dept_b = str(r[1]).strip()
            status = str(r[2]).strip().upper()
            rules[(dept_a, dept_b)] = status
            rules[(dept_b, dept_a)] = status

        return rules

    def load_eligible_requests(
        self,
        target_date: Optional[date] = None,
        selected_request_ids: Optional[List[str]] = None,
    ) -> List[MaintenanceRequestInput]:
        """
        Loads eligible candidate maintenance requests.
        """
        candidate_inputs: List[MaintenanceRequestInput] = []

        # Execute parameterized SQL query for maximum compatibility
        query_sql = "SELECT request_id, section_id, department, duration_hours, due_date, severity, criticality_score, overdue_days, status, maintenance_type FROM maintenance_requests"
        params: Dict[str, Any] = {}

        where_clauses = ["status = 'PENDING'"]
        if selected_request_ids:
            clean_ids = [rid.strip() for rid in selected_request_ids if rid.strip()]
            if clean_ids:
                placeholders = ", ".join(f":rid_{i}" for i in range(len(clean_ids)))
                where_clauses = [f"request_id IN ({placeholders})"]
                for i, cid in enumerate(clean_ids):
                    params[f"rid_{i}"] = cid

        query_sql += " WHERE " + " AND ".join(where_clauses)

        try:
            rows = self.db.execute(text(query_sql), params).fetchall()
        except Exception:
            self.db.rollback()
            rows = []

        horizon_end = None
        if target_date and not selected_request_ids:
            horizon_end = datetime(
                target_date.year, target_date.month, target_date.day, 23, 59, 59, tzinfo=timezone.utc
            ) + timedelta(days=7)

        for idx, r in enumerate(rows, start=1):
            req_id = str(r[0]).strip()
            sec_id = str(r[1]).strip()
            dept = str(r[2]).strip()
            dur_hours = float(r[3]) if r[3] is not None else 0.0
            due_dt = parse_datetime_flexible(r[4])
            sev = float(r[5]) if r[5] is not None else 2.5
            crit = float(r[6]) if r[6] is not None else 2.5
            overdue = int(r[7]) if r[7] is not None else 0
            status = str(r[8]).strip() if r[8] else "PENDING"
            maint_type = str(r[9]).strip() if r[9] else ""

            if dur_hours <= 0 or status in ("COMPLETED", "CANCELLED", "REJECTED"):
                continue

            if horizon_end and due_dt and due_dt > horizon_end:
                continue

            # Heuristic / AI priority score
            p_score = min(100.0, (sev * 10.0) + (crit * 8.0) + (overdue * 2.0))

            req_input = MaintenanceRequestInput(
                id=idx,
                request_id=req_id,
                section_id=sec_id,
                department=dept,
                duration_hours=dur_hours,
                due_date=due_dt,
                severity=sev,
                criticality_score=crit,
                overdue_days=overdue,
                priority_score=p_score,
                risk_score=None,
                maintenance_type=maint_type,
                status=status,
            )
            candidate_inputs.append(req_input)

        return candidate_inputs

    def load_maintenance_windows(
        self,
        candidate_section_ids: Optional[Set[str]] = None,
        target_date: Optional[date] = None,
    ) -> List[MaintenanceWindowInput]:
        """
        Loads feasible maintenance windows for candidate sections, incorporating
        combined passenger and synthetic freight planning traffic for the target date.
        """
        window_inputs: List[MaintenanceWindowInput] = []
        sql = "SELECT window_id, section_id, start_hour, start_time, end_time, expected_train_count, traffic_level, is_feasible, window_reason FROM maintenance_windows"
        
        # Load freight traffic pressure if target_date is supplied
        freight_hourly_traffic: Dict[int, float] = {}
        if target_date:
            try:
                from app.services.freight_service import FreightService
                freight_hourly_traffic = FreightService.get_hourly_freight_traffic(self.db, target_date)
            except Exception as e:
                self.db.rollback()
                logger.debug("Freight traffic pressure calculation note: %s", e)

        try:
            rows = self.db.execute(text(sql)).fetchall()
        except Exception:
            self.db.rollback()
            rows = []

        for idx, r in enumerate(rows, start=1):
            win_id = str(r[0]).strip()
            sec_id = str(r[1]).strip()
            start_h = int(r[2]) if r[2] is not None else 0
            start_t = r[3]
            end_t = r[4]
            train_cnt = int(r[5]) if r[5] is not None else 0
            traffic_lvl = str(r[6]).strip().upper() if r[6] else "LOW"
            is_feas = bool(r[7]) if r[7] is not None else True
            reason = str(r[8]).strip() if r[8] else None

            # Skip if section not in candidate set (if filtering is active)
            if candidate_section_ids and sec_id not in candidate_section_ids:
                continue
            # Skip infeasible windows
            if not is_feas:
                continue

            start_h_parsed, start_m = parse_time_to_minutes(start_t, default_hour=start_h)
            end_h_parsed, end_m = parse_time_to_minutes(end_t, default_hour=start_h + 4)

            start_min = start_h_parsed * 60 + start_m
            end_min = end_h_parsed * 60 + end_m
            if end_min <= start_min:
                end_min += 1440  # Crosses midnight

            dur_min = max(60, end_min - start_min)

            # Factor in freight planning traffic if active for target date
            freight_pressure = freight_hourly_traffic.get(start_h_parsed, 0.0)
            if freight_pressure > 0:
                combined_train_count = train_cnt + int(round(freight_pressure))
                if combined_train_count >= 4:
                    traffic_lvl = "HIGH"
                elif combined_train_count >= 2 and traffic_lvl == "LOW":
                    traffic_lvl = "MEDIUM"
                train_cnt = combined_train_count

            win_input = MaintenanceWindowInput(
                id=idx,
                window_id=win_id,
                section_id=sec_id,
                start_hour=start_h_parsed,
                start_minute=start_m,
                duration_minutes=dur_min,
                expected_train_count=train_cnt,
                traffic_level=traffic_lvl,
                is_feasible=is_feas,
                window_reason=reason,
            )
            window_inputs.append(win_input)

        return window_inputs

    def load_traffic_windows(
        self,
        candidate_section_ids: Optional[Set[str]] = None,
    ) -> List[TrafficWindowInput]:
        """
        Loads hourly traffic windows.
        """
        traffic_inputs: List[TrafficWindowInput] = []
        sql = "SELECT section_id, hour, train_count, traffic_level FROM traffic_windows"
        try:
            rows = self.db.execute(text(sql)).fetchall()
            for r in rows:
                sec_id = str(r[0]).strip()
                if candidate_section_ids and sec_id not in candidate_section_ids:
                    continue
                traffic_inputs.append(
                    TrafficWindowInput(
                        section_id=sec_id,
                        hour=int(r[1]),
                        train_count=int(r[2]),
                        traffic_level=str(r[3]).strip(),
                    )
                )
        except Exception:
            self.db.rollback()

        return traffic_inputs

    def prepare_solver_inputs(
        self,
        target_date: Optional[date] = None,
        selected_request_ids: Optional[List[str]] = None,
    ) -> Tuple[
        List[MaintenanceRequestInput],
        List[MaintenanceWindowInput],
        Dict[Tuple[str, str], str],
        Dict[str, int],
    ]:
        """
        Orchestrates full loading and validation pipeline.
        Returns:
            (requests, windows, compatibility_rules, section_id_map)
        """
        section_id_map, _ = self.load_section_mappings()
        compatibility_rules = self.load_compatibility_rules()
        requests = self.load_eligible_requests(
            target_date=target_date,
            selected_request_ids=selected_request_ids,
        )

        candidate_sections = {r.section_id for r in requests}
        windows = self.load_maintenance_windows(
            candidate_section_ids=candidate_sections,
            target_date=target_date,
        )

        return requests, windows, compatibility_rules, section_id_map

