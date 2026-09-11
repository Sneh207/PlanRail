"""
PlanRail What-If Simulation Service
===================================

Provides a read-only scenario evaluation engine comparing simulated maintenance
plans against the baseline schedule using the Google OR-Tools CP-SAT optimizer.
Ensures ZERO mutations/writes to production optimization tables.
"""

from __future__ import annotations

import copy
import logging
import math
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Set, Tuple

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.optimizer.data_loader import OptimizerDataLoader
from app.optimizer.solver import (
    MaintenanceBlockSolver,
    MaintenanceRequestInput,
    MaintenanceWindowInput,
    OptimizedBlockPlan,
    OptimizationResult,
)
from app.schemas.domain import (
    BlockTaskResponse,
    OptimizedBlockResponse,
    SimulationDifference,
    SimulationMetrics,
    SimulationRunRequest,
    SimulationRunResponse,
)

logger = logging.getLogger(__name__)


def build_in_memory_block_responses(
    blocks: List[OptimizedBlockPlan],
    target_date: date,
    run_tag: str,
) -> List[OptimizedBlockResponse]:
    """Converts solver OptimizedBlockPlan objects to API schemas in-memory without DB persistence."""
    responses: List[OptimizedBlockResponse] = []
    midnight_utc = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0, tzinfo=timezone.utc)

    for idx, b in enumerate(blocks, start=1):
        start_dt = midnight_utc + timedelta(minutes=b.start_time_minutes)
        end_dt = midnight_utc + timedelta(minutes=b.end_time_minutes)

        task_resps = [
            BlockTaskResponse(
                block_task_id=f"SIM_BT_{idx}_{t.sequence_order}",
                block_id=b.block_code,
                request_id=t.request_id,
                sequence=t.sequence_order,
            )
            for t in b.tasks
        ]

        responses.append(
            OptimizedBlockResponse(
                block_id=b.block_code,
                run_id=f"SIM_{run_tag}",
                section_id=b.section_id,
                start_time=start_dt,
                end_time=end_dt,
                duration_hours=b.duration_hours,
                status="SIMULATED",
                tasks=task_resps,
            )
        )
    return responses


def generate_explanation(
    scenario_type: str,
    request_id: Optional[str],
    window_id: Optional[str],
    difference: SimulationDifference,
    newly_scheduled: List[str],
    unscheduled: List[str],
    moved: List[str],
    emergency_scheduled: bool,
    baseline_emergency_scheduled: bool,
) -> str:
    """Generates a short, factual explanation strictly reflecting solver outcomes."""
    if scenario_type == "TRAFFIC_PLUS_20":
        if difference.train_exposure_delta != 0 or moved or newly_scheduled or unscheduled:
            return (
                "Traffic was increased by 20%, increasing operational exposure in affected windows. "
                "The optimizer reallocated maintenance toward lower-traffic windows where feasible."
            )
        return (
            "Traffic was increased by 20% across candidate windows. "
            "The optimal maintenance plan remained unchanged as alternative lower-traffic windows were either unavailable or already optimal."
        )

    elif scenario_type == "EMERGENCY_MAINTENANCE":
        req_code = request_id or "UNKNOWN"
        if emergency_scheduled:
            if not baseline_emergency_scheduled:
                return (
                    f"Emergency request {req_code} was given elevated scheduling priority and successfully "
                    "scheduled into an available window while all operational constraints remained enforced."
                )
            return (
                f"Emergency request {req_code} was given elevated scheduling priority. "
                "It was successfully retained in the schedule under strict operational constraints."
            )
        return (
            f"Emergency request {req_code} could not be scheduled due to strict operational constraints "
            "(window capacity, section match, or department compatibility)."
        )

    elif scenario_type == "REMOVE_MAINTENANCE_WINDOW":
        win_code = window_id or "UNKNOWN"
        if moved and unscheduled:
            return (
                f"Maintenance window {win_code} was removed from the simulation. "
                f"The optimizer reassigned {len(moved)} feasible tasks to alternative windows, "
                f"while {len(unscheduled)} tasks could not be accommodated due to capacity constraints."
            )
        elif moved:
            return (
                f"Maintenance window {win_code} was removed from the simulation. "
                f"The optimizer reassigned {len(moved)} feasible tasks to alternative windows where capacity allowed."
            )
        elif unscheduled:
            return (
                f"Maintenance window {win_code} was removed from the simulation. "
                f"{len(unscheduled)} tasks previously scheduled in this window could not be reassigned to alternative windows."
            )
        return (
            f"Maintenance window {win_code} was removed from the simulation. "
            "The scenario did not change the optimal plan as this window was not utilized in the baseline schedule."
        )

    return "Simulation completed successfully."


class SimulationService:
    """Service handling read-only What-If simulation runs and comparative metrics."""

    @staticmethod
    def run_simulation(
        db: Session,
        request: SimulationRunRequest,
    ) -> SimulationRunResponse:
        """
        Executes baseline and scenario CP-SAT optimization in-memory,
        calculates comparative deltas, and returns structured comparison.
        """
        target_date: date = request.target_date

        if not isinstance(target_date, date):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_TARGET_DATE", "message": "A valid target_date is required."},
            )

        # ---------------------------------------------------------------------
        # 1. Parameter Validation against DB
        # ---------------------------------------------------------------------
        if request.scenario_type == "EMERGENCY_MAINTENANCE":
            req_id = (request.request_id or "").strip()
            if not req_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"code": "MISSING_REQUEST_ID", "message": "request_id is required for EMERGENCY_MAINTENANCE."},
                )
            # Verify request exists in DB
            check_sql = text("SELECT request_id FROM maintenance_requests WHERE request_id = :rid")
            row = db.execute(check_sql, {"rid": req_id}).first()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"code": "REQUEST_NOT_FOUND", "message": f"Maintenance request '{req_id}' does not exist."},
                )

        elif request.scenario_type == "REMOVE_MAINTENANCE_WINDOW":
            win_id = (request.window_id or "").strip()
            if not win_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"code": "MISSING_WINDOW_ID", "message": "window_id is required for REMOVE_MAINTENANCE_WINDOW."},
                )
            # Verify window exists in DB
            check_sql = text("SELECT window_id FROM maintenance_windows WHERE window_id = :wid")
            row = db.execute(check_sql, {"wid": win_id}).first()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"code": "WINDOW_NOT_FOUND", "message": f"Maintenance window '{win_id}' does not exist."},
                )

        # ---------------------------------------------------------------------
        # 2. Load Baseline Optimizer Inputs
        # ---------------------------------------------------------------------
        loader = OptimizerDataLoader(db)
        try:
            baseline_requests, baseline_windows, compatibility_rules, section_id_map = loader.prepare_solver_inputs(
                target_date=target_date,
            )
        except Exception as e:
            logger.exception("Failed to load baseline optimizer inputs")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "DATA_LOAD_ERROR", "message": f"Error loading simulation baseline inputs: {str(e)}"},
            )

        # If emergency request exists in DB but was omitted (e.g. horizon filter), load it explicitly
        if request.scenario_type == "EMERGENCY_MAINTENANCE" and request.request_id:
            req_ids_in_baseline = {r.request_id for r in baseline_requests}
            if request.request_id not in req_ids_in_baseline:
                emergency_inputs = loader.load_eligible_requests(selected_request_ids=[request.request_id])
                if emergency_inputs:
                    baseline_requests.extend(emergency_inputs)

        # ---------------------------------------------------------------------
        # 3. Baseline Solve
        # ---------------------------------------------------------------------
        solver = MaintenanceBlockSolver(time_limit_seconds=5.0, random_seed=42)
        try:
            baseline_result: OptimizationResult = solver.solve(
                requests=baseline_requests,
                windows=baseline_windows,
                compatibility_rules=compatibility_rules,
                max_block_duration_hours=4.0,
                target_date=target_date,
                section_id_map=section_id_map,
            )
        except Exception as e:
            logger.exception("Baseline optimization solve failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "SOLVER_ERROR", "message": f"Baseline solver error: {str(e)}"},
            )

        # ---------------------------------------------------------------------
        # 4. In-Memory Scenario Transformation
        # ---------------------------------------------------------------------
        scenario_windows: List[MaintenanceWindowInput] = []
        scenario_requests: List[MaintenanceRequestInput] = []

        if request.scenario_type == "TRAFFIC_PLUS_20":
            # Deep copy and increase traffic by 20%
            for w in baseline_windows:
                new_traffic = int(math.ceil(w.expected_train_count * 1.20))
                scenario_windows.append(
                    MaintenanceWindowInput(
                        id=w.id,
                        window_id=w.window_id,
                        section_id=w.section_id,
                        start_hour=w.start_hour,
                        start_minute=w.start_minute,
                        duration_minutes=w.duration_minutes,
                        expected_train_count=new_traffic,
                        traffic_level=w.traffic_level,
                        is_feasible=w.is_feasible,
                        window_reason=w.window_reason,
                    )
                )
            scenario_requests = [
                MaintenanceRequestInput(
                    id=r.id,
                    request_id=r.request_id,
                    section_id=r.section_id,
                    department=r.department,
                    duration_hours=r.duration_hours,
                    due_date=r.due_date,
                    severity=r.severity,
                    criticality_score=r.criticality_score,
                    overdue_days=r.overdue_days,
                    priority_score=r.priority_score,
                    risk_score=r.risk_score,
                    maintenance_type=r.maintenance_type,
                    status=r.status,
                )
                for r in baseline_requests
            ]

        elif request.scenario_type == "EMERGENCY_MAINTENANCE":
            scenario_windows = [
                MaintenanceWindowInput(
                    id=w.id,
                    window_id=w.window_id,
                    section_id=w.section_id,
                    start_hour=w.start_hour,
                    start_minute=w.start_minute,
                    duration_minutes=w.duration_minutes,
                    expected_train_count=w.expected_train_count,
                    traffic_level=w.traffic_level,
                    is_feasible=w.is_feasible,
                    window_reason=w.window_reason,
                )
                for w in baseline_windows
            ]
            for r in baseline_requests:
                if r.request_id == request.request_id:
                    # Emergency priority boost: 1000.0 priority score
                    # Adds 15,000 points to objective, dominating standard tasks while hard constraints remain absolute
                    scenario_requests.append(
                        MaintenanceRequestInput(
                            id=r.id,
                            request_id=r.request_id,
                            section_id=r.section_id,
                            department=r.department,
                            duration_hours=r.duration_hours,
                            due_date=r.due_date,
                            severity=5.0,
                            criticality_score=5.0,
                            overdue_days=max(r.overdue_days, 14),
                            priority_score=1000.0,
                            risk_score=r.risk_score,
                            maintenance_type=r.maintenance_type,
                            status=r.status,
                        )
                    )
                else:
                    scenario_requests.append(
                        MaintenanceRequestInput(
                            id=r.id,
                            request_id=r.request_id,
                            section_id=r.section_id,
                            department=r.department,
                            duration_hours=r.duration_hours,
                            due_date=r.due_date,
                            severity=r.severity,
                            criticality_score=r.criticality_score,
                            overdue_days=r.overdue_days,
                            priority_score=r.priority_score,
                            risk_score=r.risk_score,
                            maintenance_type=r.maintenance_type,
                            status=r.status,
                        )
                    )

        elif request.scenario_type == "REMOVE_MAINTENANCE_WINDOW":
            scenario_windows = [
                MaintenanceWindowInput(
                    id=w.id,
                    window_id=w.window_id,
                    section_id=w.section_id,
                    start_hour=w.start_hour,
                    start_minute=w.start_minute,
                    duration_minutes=w.duration_minutes,
                    expected_train_count=w.expected_train_count,
                    traffic_level=w.traffic_level,
                    is_feasible=w.is_feasible,
                    window_reason=w.window_reason,
                )
                for w in baseline_windows
                if w.window_id != request.window_id
            ]
            scenario_requests = [
                MaintenanceRequestInput(
                    id=r.id,
                    request_id=r.request_id,
                    section_id=r.section_id,
                    department=r.department,
                    duration_hours=r.duration_hours,
                    due_date=r.due_date,
                    severity=r.severity,
                    criticality_score=r.criticality_score,
                    overdue_days=r.overdue_days,
                    priority_score=r.priority_score,
                    risk_score=r.risk_score,
                    maintenance_type=r.maintenance_type,
                    status=r.status,
                )
                for r in baseline_requests
            ]

        # ---------------------------------------------------------------------
        # 5. Scenario Solve
        # ---------------------------------------------------------------------
        try:
            scenario_result: OptimizationResult = solver.solve(
                requests=scenario_requests,
                windows=scenario_windows,
                compatibility_rules=compatibility_rules,
                max_block_duration_hours=4.0,
                target_date=target_date,
                section_id_map=section_id_map,
            )
        except Exception as e:
            logger.exception("Scenario optimization solve failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "SOLVER_ERROR", "message": f"Scenario solver error: {str(e)}"},
            )

        # ---------------------------------------------------------------------
        # 6. Metrics & Comparison Computation
        # ---------------------------------------------------------------------
        baseline_sched_count = len(baseline_result.scheduled_task_ids)
        baseline_unsched_count = len(baseline_result.unscheduled_task_ids)
        baseline_block_count = len(baseline_result.blocks)
        baseline_duration = round(sum(b.duration_hours for b in baseline_result.blocks), 2)
        baseline_obj = round(baseline_result.objective_value, 2)
        baseline_exposure = sum(b.expected_train_count for b in baseline_result.blocks)

        baseline_metrics = SimulationMetrics(
            scheduled_tasks=baseline_sched_count,
            unscheduled_tasks=baseline_unsched_count,
            blocks=baseline_block_count,
            total_scheduled_duration_hours=baseline_duration,
            objective_score=baseline_obj,
            total_expected_train_exposure=baseline_exposure,
        )

        scenario_sched_count = len(scenario_result.scheduled_task_ids)
        scenario_unsched_count = len(scenario_result.unscheduled_task_ids)
        scenario_block_count = len(scenario_result.blocks)
        scenario_duration = round(sum(b.duration_hours for b in scenario_result.blocks), 2)
        scenario_obj = round(scenario_result.objective_value, 2)
        scenario_exposure = sum(b.expected_train_count for b in scenario_result.blocks)

        scenario_metrics = SimulationMetrics(
            scheduled_tasks=scenario_sched_count,
            unscheduled_tasks=scenario_unsched_count,
            blocks=scenario_block_count,
            total_scheduled_duration_hours=scenario_duration,
            objective_score=scenario_obj,
            total_expected_train_exposure=scenario_exposure,
        )

        difference = SimulationDifference(
            scheduled_tasks_delta=scenario_sched_count - baseline_sched_count,
            blocks_delta=scenario_block_count - baseline_block_count,
            scheduled_duration_delta_hours=round(scenario_duration - baseline_duration, 2),
            objective_delta=round(scenario_obj - baseline_obj, 2),
            train_exposure_delta=scenario_exposure - baseline_exposure,
        )

        # Task delta tracking
        baseline_scheduled_set: Set[str] = set(baseline_result.scheduled_task_ids)
        scenario_scheduled_set: Set[str] = set(scenario_result.scheduled_task_ids)

        baseline_task_window = {
            t.request_id: b.window_code for b in baseline_result.blocks for t in b.tasks
        }
        scenario_task_window = {
            t.request_id: b.window_code for b in scenario_result.blocks for t in b.tasks
        }

        newly_scheduled = sorted(list(scenario_scheduled_set - baseline_scheduled_set))
        unscheduled_after = sorted(list(baseline_scheduled_set - scenario_scheduled_set))
        moved = sorted([
            r_id
            for r_id in (baseline_scheduled_set & scenario_scheduled_set)
            if baseline_task_window.get(r_id) != scenario_task_window.get(r_id)
        ])

        # Convert block plans to API schemas (in-memory)
        baseline_blocks = build_in_memory_block_responses(baseline_result.blocks, target_date, "BASELINE")
        scenario_blocks = build_in_memory_block_responses(scenario_result.blocks, target_date, "SCENARIO")

        # Generate explanation
        explanation = generate_explanation(
            scenario_type=request.scenario_type,
            request_id=request.request_id,
            window_id=request.window_id,
            difference=difference,
            newly_scheduled=newly_scheduled,
            unscheduled=unscheduled_after,
            moved=moved,
            emergency_scheduled=(request.request_id in scenario_scheduled_set) if request.request_id else False,
            baseline_emergency_scheduled=(request.request_id in baseline_scheduled_set) if request.request_id else False,
        )

        now_utc = datetime.now(timezone.utc)
        sim_id = f"SIM_{request.scenario_type}_{now_utc.strftime('%Y%m%d_%H%M%S')}_{now_utc.microsecond:06d}"

        return SimulationRunResponse(
            simulation_id=sim_id,
            scenario_type=request.scenario_type,
            target_date=target_date,
            baseline=baseline_metrics,
            scenario=scenario_metrics,
            difference=difference,
            newly_scheduled_tasks=newly_scheduled,
            unscheduled_tasks_after_simulation=unscheduled_after,
            moved_tasks=moved,
            baseline_blocks=baseline_blocks,
            scenario_blocks=scenario_blocks,
            explanation=explanation,
        )
