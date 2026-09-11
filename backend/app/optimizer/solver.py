"""
PlanRail OR-Tools CP-SAT Optimizer Core
========================================

Pure, database-independent constraint programming solver for railway maintenance
block scheduling. Uses Google OR-Tools CP-SAT.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from datetime import date, datetime, time as dt_time, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from ortools.sat.python import cp_model


# =============================================================================
# Input Data Structures
# =============================================================================

@dataclass
class MaintenanceRequestInput:
    """Represents a candidate maintenance task for optimization."""
    id: int                                # Database integer PK
    request_id: str                        # Business code (e.g. "MR0001")
    section_id: str                        # Section code (e.g. "SEC_DEL_TKD")
    department: str                        # e.g. "Engineering", "S&T", "Electrical"
    duration_hours: float                  # Work duration in hours
    due_date: Optional[datetime] = None    # Deadline timestamp
    severity: float = 1.0                  # 1.0 to 5.0
    criticality_score: float = 1.0         # 1.0 to 5.0
    overdue_days: int = 0                  # Days past due_date
    priority_score: Optional[float] = None # 0.0 to 100.0 (AI or computed)
    risk_score: Optional[float] = None     # 0.0 to 100.0 (AI or computed)
    maintenance_type: str = ""             # Descriptive type
    status: str = "PENDING"                # e.g. "PENDING"

    @property
    def duration_minutes(self) -> int:
        """Returns integer duration in minutes for CP-SAT solver."""
        return max(1, int(math.ceil(self.duration_hours * 60.0)))


@dataclass
class MaintenanceWindowInput:
    """Represents an available time window on a section."""
    id: int                                # Database integer PK
    window_id: str                         # Business code (e.g. "MW_DEL_TKD_01")
    section_id: str                        # Section code
    start_hour: int                        # 0 to 23
    start_minute: int = 0                  # 0 to 59
    duration_minutes: int = 240            # Window capacity in minutes (e.g. 4 hrs = 240)
    expected_train_count: int = 0          # Scheduled trains in this window
    traffic_level: str = "LOW"             # "LOW", "MEDIUM", "HIGH"
    is_feasible: bool = True               # Feasibility flag
    window_reason: Optional[str] = None    # Descriptive reason

    @property
    def start_time_minutes(self) -> int:
        """Minutes from midnight (0..1439)."""
        return (self.start_hour * 60) + self.start_minute

    @property
    def end_time_minutes(self) -> int:
        """End minutes from midnight (can exceed 1440 for cross-midnight windows)."""
        return self.start_time_minutes + self.duration_minutes


@dataclass
class TrafficWindowInput:
    """Hourly traffic count on a railway section."""
    section_id: str
    hour: int
    train_count: int
    traffic_level: str


# =============================================================================
# Output Data Structures
# =============================================================================

@dataclass
class ScheduledTask:
    """Details of a task scheduled inside a block."""
    request_id: str
    db_id: int
    department: str
    maintenance_type: str
    duration_hours: float
    duration_minutes: int
    priority_score: Optional[float]
    criticality_score: float
    severity: float
    sequence_order: int


@dataclass
class OptimizedBlockPlan:
    """Represents an optimized maintenance block comprising one or more tasks."""
    block_code: str
    section_id: str
    section_db_id: Optional[int]
    maintenance_window_id: Optional[int]
    window_code: str
    start_time_minutes: int
    end_time_minutes: int
    duration_minutes: int
    duration_hours: float
    tasks: List[ScheduledTask] = field(default_factory=list)
    
    # Explainability metadata
    task_count: int = 0
    departments: List[str] = field(default_factory=list)
    is_bundled: bool = False
    expected_train_count: int = 0
    traffic_level: str = "LOW"
    avg_priority_score: float = 0.0
    optimization_score: float = 0.0


@dataclass
class OptimizationResult:
    """Complete structured solver result."""
    status: str                            # "OPTIMAL", "FEASIBLE", "INFEASIBLE", "UNKNOWN"
    solve_time_ms: float
    objective_value: float
    scheduled_task_ids: List[str]
    unscheduled_task_ids: List[str]
    blocks: List[OptimizedBlockPlan]
    metrics: Dict[str, Any]


# =============================================================================
# CP-SAT Solver Implementation
# =============================================================================

class MaintenanceBlockSolver:
    """
    CP-SAT Optimization Engine for Indian Railways Maintenance Block Planning.
    
    Objective:
        Maximize high-priority & overdue maintenance completed while minimizing
        train disruption (traffic penalty) and block activation overhead.
    """

    def __init__(
        self,
        time_limit_seconds: float = 5.0,
        random_seed: int = 42,
        num_search_workers: int = 4,
    ):
        self.time_limit_seconds = time_limit_seconds
        self.random_seed = random_seed
        self.num_search_workers = num_search_workers

    def solve(
        self,
        requests: List[MaintenanceRequestInput],
        windows: List[MaintenanceWindowInput],
        compatibility_rules: Optional[Dict[Tuple[str, str], str]] = None,
        max_block_duration_hours: float = 4.0,
        target_date: Optional[date] = None,
        section_id_map: Optional[Dict[str, int]] = None,
    ) -> OptimizationResult:
        """
        Executes CP-SAT model solve.
        
        Args:
            requests: Filtered eligible candidate maintenance requests.
            windows: Available maintenance windows (only feasible ones considered).
            compatibility_rules: Dict mapping (dept_a, dept_b) -> "COMPATIBLE"|"CONDITIONAL"|"INCOMPATIBLE".
            max_block_duration_hours: Maximum block length constraint in hours.
            target_date: Target date for timestamp computation.
            section_id_map: Optional mapping from section code to integer database PK.
        """
        start_wall_time = time.perf_counter()
        compatibility = compatibility_rules or {}
        max_block_duration_minutes = int(math.ceil(max_block_duration_hours * 60.0))
        section_db_map = section_id_map or {}

        # ---------------------------------------------------------------------
        # 1. Filter and index candidate elements
        # ---------------------------------------------------------------------
        # Only feasible windows
        feasible_windows = [w for w in windows if w.is_feasible and w.duration_minutes > 0]
        window_by_id = {w.window_id: w for w in feasible_windows}
        
        # Group windows by section
        windows_by_section: Dict[str, List[MaintenanceWindowInput]] = {}
        for w in feasible_windows:
            windows_by_section.setdefault(w.section_id, []).append(w)

        # Index eligible requests
        eligible_requests = [r for r in requests if r.duration_minutes > 0]
        request_by_id = {r.request_id: r for r in eligible_requests}

        # If no requests or no feasible windows, return early valid result
        if not eligible_requests or not feasible_windows:
            solve_time_ms = (time.perf_counter() - start_wall_time) * 1000.0
            return OptimizationResult(
                status="FEASIBLE" if not eligible_requests else "INFEASIBLE",
                solve_time_ms=round(solve_time_ms, 2),
                objective_value=0.0,
                scheduled_task_ids=[],
                unscheduled_task_ids=[r.request_id for r in eligible_requests],
                blocks=[],
                metrics={
                    "total_requests": len(eligible_requests),
                    "scheduled_requests": 0,
                    "unscheduled_requests": len(eligible_requests),
                    "total_blocks": 0,
                    "solve_time_ms": round(solve_time_ms, 2),
                    "reason": "No feasible windows or candidate requests",
                },
            )

        # ---------------------------------------------------------------------
        # 2. Build CP-SAT Model & Decision Variables
        # ---------------------------------------------------------------------
        model = cp_model.CpModel()

        # x[r_id, w_id]: Task r assigned to Window w
        x: Dict[Tuple[str, str], cp_model.IntVar] = {}
        # y[w_id]: Window w is activated as a maintenance block
        y: Dict[str, cp_model.IntVar] = {}

        # Pre-filter candidate pairs: request and window must share same section,
        # and individual task duration cannot exceed window capacity or max block duration
        candidate_windows_for_req: Dict[str, List[str]] = {r.request_id: [] for r in eligible_requests}
        candidate_reqs_for_window: Dict[str, List[str]] = {w.window_id: [] for w in feasible_windows}

        for r in eligible_requests:
            sec_windows = windows_by_section.get(r.section_id, [])
            for w in sec_windows:
                effective_cap = min(w.duration_minutes, max_block_duration_minutes)
                if r.duration_minutes <= effective_cap:
                    var_name = f"x_{r.request_id}_{w.window_id}"
                    x_var = model.NewBoolVar(var_name)
                    x[(r.request_id, w.window_id)] = x_var
                    candidate_windows_for_req[r.request_id].append(w.window_id)
                    candidate_reqs_for_window[w.window_id].append(r.request_id)

        # Create y variables only for windows with at least one candidate request
        for w in feasible_windows:
            if candidate_reqs_for_window[w.window_id]:
                y[w.window_id] = model.NewBoolVar(f"y_{w.window_id}")

        # ---------------------------------------------------------------------
        # 3. Add Constraints
        # ---------------------------------------------------------------------

        # Constraint 4.1: At-Most-Once per Request
        for r in eligible_requests:
            cand_wins = candidate_windows_for_req[r.request_id]
            if cand_wins:
                model.Add(sum(x[(r.request_id, w_id)] for w_id in cand_wins) <= 1)

        # Constraint 4.3 & 4.4: Window Capacity & Activation Linking
        for w_id, cand_reqs in candidate_reqs_for_window.items():
            if not cand_reqs:
                continue
            w = window_by_id[w_id]
            effective_cap = min(w.duration_minutes, max_block_duration_minutes)
            y_var = y[w_id]

            # sum(duration * x) <= effective_cap * y
            durations = [request_by_id[r_id].duration_minutes for r_id in cand_reqs]
            vars_list = [x[(r_id, w_id)] for r_id in cand_reqs]
            model.Add(
                sum(d * v for d, v in zip(durations, vars_list)) <= effective_cap * y_var
            )

            # Activation linking: each individual x <= y
            for v in vars_list:
                model.Add(v <= y_var)

        # Constraint 4.5: Same-Section Non-Overlap
        # If two maintenance windows on the same section overlap in time, at most one can be active.
        for sec_id, sec_windows in windows_by_section.items():
            active_sec_windows = [w for w in sec_windows if w.window_id in y]
            n_wins = len(active_sec_windows)
            for i in range(n_wins):
                w1 = active_sec_windows[i]
                for j in range(i + 1, n_wins):
                    w2 = active_sec_windows[j]
                    # Overlap check: max(start1, start2) < min(end1, end2)
                    overlap = max(w1.start_time_minutes, w2.start_time_minutes) < min(
                        w1.end_time_minutes, w2.end_time_minutes
                    )
                    if overlap:
                        model.Add(y[w1.window_id] + y[w2.window_id] <= 1)

        # Constraint 4.6: Multi-Department Incompatibility
        # Incompatible department pairs cannot be bundled in the same window.
        for w_id, cand_reqs in candidate_reqs_for_window.items():
            if len(cand_reqs) < 2:
                continue
            n_reqs = len(cand_reqs)
            for i in range(n_reqs):
                r1 = request_by_id[cand_reqs[i]]
                for j in range(i + 1, n_reqs):
                    r2 = request_by_id[cand_reqs[j]]
                    if r1.department == r2.department:
                        continue  # Same department is always compatible
                    
                    pair_key_1 = (r1.department, r2.department)
                    pair_key_2 = (r2.department, r1.department)
                    comp_status = compatibility.get(pair_key_1) or compatibility.get(pair_key_2)

                    if comp_status == "INCOMPATIBLE":
                        # Both cannot be in this window simultaneously
                        model.Add(x[(r1.request_id, w_id)] + x[(r2.request_id, w_id)] <= 1)

        # ---------------------------------------------------------------------
        # 4. Objective Function Formulation
        # ---------------------------------------------------------------------
        # MAXIMIZE: Task Completion Reward + Priority/Risk Reward
        # MINIMIZE: Block Activation Overhead + Traffic Disruption Cost
        
        obj_rewards = []
        obj_costs = []

        # Request assignment reward
        for (r_id, w_id), x_var in x.items():
            r = request_by_id[r_id]
            
            # Base task completion reward
            task_reward = 1000
            
            # Priority reward (priority_score or heuristic)
            p_score = r.priority_score if r.priority_score is not None else (r.severity * 10.0 + r.criticality_score * 10.0)
            priority_reward = int(round(p_score * 15.0))
            
            # Criticality & severity reward
            crit_reward = int(round(r.criticality_score * 100.0))
            sev_reward = int(round(r.severity * 100.0))
            
            # Overdue escalation reward
            overdue_reward = min(3000, r.overdue_days * 150)
            
            total_task_reward = task_reward + priority_reward + crit_reward + sev_reward + overdue_reward
            obj_rewards.append(total_task_reward * x_var)

        # Window activation cost
        for w_id, y_var in y.items():
            w = window_by_id[w_id]
            
            # Base block creation overhead
            base_block_cost = 250
            
            # Traffic disruption penalty based on expected trains
            train_penalty = w.expected_train_count * 50
            
            # Traffic level penalty
            traffic_lvl_penalty = 0
            if w.traffic_level.upper() == "MEDIUM":
                traffic_lvl_penalty = 100
            elif w.traffic_level.upper() == "HIGH":
                traffic_lvl_penalty = 400
                
            total_window_cost = base_block_cost + train_penalty + traffic_lvl_penalty
            obj_costs.append(total_window_cost * y_var)

        model.Maximize(sum(obj_rewards) - sum(obj_costs))

        # ---------------------------------------------------------------------
        # 5. Solver Invocation
        # ---------------------------------------------------------------------
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.time_limit_seconds
        solver.parameters.random_seed = self.random_seed
        solver.parameters.num_search_workers = self.num_search_workers

        status_code = solver.Solve(model)
        solve_time_ms = (time.perf_counter() - start_wall_time) * 1000.0

        # Map CP-SAT status
        if status_code == cp_model.OPTIMAL:
            status_str = "OPTIMAL"
        elif status_code == cp_model.FEASIBLE:
            status_str = "FEASIBLE"
        elif status_code == cp_model.INFEASIBLE:
            status_str = "INFEASIBLE"
        else:
            status_str = "UNKNOWN"

        # ---------------------------------------------------------------------
        # 6. Extract Solution & Build Explainability Metadata
        # ---------------------------------------------------------------------
        scheduled_tasks_by_window: Dict[str, List[ScheduledTask]] = {}
        scheduled_task_ids: Set[str] = set()

        if status_str in ("OPTIMAL", "FEASIBLE"):
            for (r_id, w_id), x_var in x.items():
                if solver.Value(x_var) == 1:
                    r = request_by_id[r_id]
                    scheduled_task_ids.add(r_id)
                    
                    st = ScheduledTask(
                        request_id=r.request_id,
                        db_id=r.id,
                        department=r.department,
                        maintenance_type=r.maintenance_type,
                        duration_hours=r.duration_hours,
                        duration_minutes=r.duration_minutes,
                        priority_score=r.priority_score,
                        criticality_score=r.criticality_score,
                        severity=r.severity,
                        sequence_order=1,  # updated during block assembly
                    )
                    scheduled_tasks_by_window.setdefault(w_id, []).append(st)

        # Assemble OptimizedBlockPlan records
        blocks: List[OptimizedBlockPlan] = []
        block_idx = 1
        date_str = target_date.strftime("%Y%m%d") if target_date else datetime.now(timezone.utc).strftime("%Y%m%d")

        for w_id, task_list in scheduled_tasks_by_window.items():
            if not task_list:
                continue
            w = window_by_id[w_id]
            
            # Sort tasks inside block by criticality / priority descending
            task_list.sort(key=lambda t: (t.priority_score or 0.0, t.criticality_score), reverse=True)
            for seq, task in enumerate(task_list, start=1):
                task.sequence_order = seq

            total_dur_min = sum(t.duration_minutes for t in task_list)
            distinct_depts = list(dict.fromkeys(t.department for t in task_list))
            p_scores = [t.priority_score for t in task_list if t.priority_score is not None]
            avg_p = sum(p_scores) / len(p_scores) if p_scores else 0.0
            
            # Optimization score calculation (0 to 100)
            traffic_factor = 1.0 if w.traffic_level == "LOW" else (0.75 if w.traffic_level == "MEDIUM" else 0.5)
            density_factor = min(1.0, total_dur_min / max(1, w.duration_minutes))
            opt_score = round((0.5 * density_factor + 0.5 * traffic_factor) * 100.0, 1)

            block_code = f"BLK_{date_str}_{w.section_id}_{block_idx:02d}"
            block_idx += 1

            block_plan = OptimizedBlockPlan(
                block_code=block_code,
                section_id=w.section_id,
                section_db_id=section_db_map.get(w.section_id),
                maintenance_window_id=w.id,
                window_code=w.window_id,
                start_time_minutes=w.start_time_minutes,
                end_time_minutes=w.start_time_minutes + total_dur_min,
                duration_minutes=total_dur_min,
                duration_hours=round(total_dur_min / 60.0, 2),
                tasks=task_list,
                task_count=len(task_list),
                departments=distinct_depts,
                is_bundled=len(task_list) > 1 or len(distinct_depts) > 1,
                expected_train_count=w.expected_train_count,
                traffic_level=w.traffic_level,
                avg_priority_score=round(avg_p, 1),
                optimization_score=opt_score,
            )
            blocks.append(block_plan)

        unscheduled_ids = [r.request_id for r in eligible_requests if r.request_id not in scheduled_task_ids]

        metrics = {
            "total_requests_considered": len(eligible_requests),
            "scheduled_tasks_count": len(scheduled_task_ids),
            "unscheduled_tasks_count": len(unscheduled_ids),
            "blocks_count": len(blocks),
            "total_scheduled_duration_minutes": sum(b.duration_minutes for b in blocks),
            "solve_time_ms": round(solve_time_ms, 2),
            "objective_value": round(solver.ObjectiveValue(), 2) if status_str in ("OPTIMAL", "FEASIBLE") else 0.0,
            "deterministic_seed": self.random_seed,
        }

        return OptimizationResult(
            status=status_str,
            solve_time_ms=round(solve_time_ms, 2),
            objective_value=metrics["objective_value"],
            scheduled_task_ids=list(scheduled_task_ids),
            unscheduled_task_ids=unscheduled_ids,
            blocks=blocks,
            metrics=metrics,
        )
