# PlanRail — What-If Simulation Engine API Documentation

The **What-If Simulation Engine** provides decision-support capabilities for Indian Railways maintenance controllers. It enables simulation and comparative analysis of hypothetical operational scenarios against an optimal baseline schedule without modifying production database records.

> [!IMPORTANT]
> **Decision Support Disclaimer**:
> What-If simulation is a decision-support feature. It does not modify operational database records or automatically approve maintenance blocks.
>
> **Traffic Modeling Disclaimer**:
> The optimizer is traffic-aware using expected train counts and traffic levels. It does not model individual train movements as decision variables.

---

## 1. API Endpoint

- **Route**: `POST /api/v1/simulation/run`
- **Authentication**: Bearer token (when enabled) / Standard JSON contract
- **Content-Type**: `application/json`

---

## 2. Request Schema

```typescript
interface SimulationRunRequest {
  scenario_type: "TRAFFIC_PLUS_20" | "EMERGENCY_MAINTENANCE" | "REMOVE_MAINTENANCE_WINDOW";
  target_date: string; // ISO date format "YYYY-MM-DD"
  request_id?: string; // Required for EMERGENCY_MAINTENANCE (e.g. "MR0001")
  window_id?: string;  // Required for REMOVE_MAINTENANCE_WINDOW (e.g. "MW00001")
}
```

### Validation Rules
1. **`TRAFFIC_PLUS_20`**:
   - `target_date` is required.
   - `request_id` and `window_id` are ignored.
2. **`EMERGENCY_MAINTENANCE`**:
   - `target_date` and `request_id` are required.
   - Returns `400 Bad Request` (`REQUEST_NOT_FOUND`) if `request_id` does not exist in the database.
3. **`REMOVE_MAINTENANCE_WINDOW`**:
   - `target_date` and `window_id` are required.
   - Returns `400 Bad Request` (`WINDOW_NOT_FOUND`) if `window_id` does not exist in the database.

---

## 3. Scenarios

### Scenario A — Traffic +20% (`TRAFFIC_PLUS_20`)
- **Description**: Simulates a 20% surge in train traffic across all maintenance windows on the target date (`simulated_train_count = ceil(expected_train_count * 1.20)`).
- **Optimizer Impact**: Windows with higher baseline traffic incur amplified penalty costs in the CP-SAT objective function, steering the optimizer toward lower-traffic or night windows where feasible.
- **Data Safety**: Operates on an in-memory deep copy of candidate maintenance windows; database records remain completely untouched.

### Scenario B — Emergency Maintenance (`EMERGENCY_MAINTENANCE`)
- **Description**: Evaluates the scheduling of a critical or emergent maintenance request (`request_id`).
- **Optimizer Impact**: Injects an elevated bounded priority reward bonus (+15,000 points) into the CP-SAT objective, ensuring the emergency task is prioritized above normal maintenance tasks.
- **Strict Constraints Enforced**:
  - Section consistency (must match the railway section).
  - Window capacity (task duration must fit inside window duration and max block duration).
  - Department compatibility (incompatible tasks are never bundled together).
  - If operational constraints cannot be satisfied, the task is reported as infeasible rather than forced into an infeasible block.

### Scenario C — Remove Maintenance Window (`REMOVE_MAINTENANCE_WINDOW`)
- **Description**: Evaluates railway network resilience by removing a specified maintenance window (`window_id`) from the solver candidate set.
- **Optimizer Impact**: Re-solves the optimization model over remaining feasible windows. Identifies tasks that dynamically reallocated to alternative windows (`moved_tasks`) versus tasks that could not be accommodated (`unscheduled_tasks_after_simulation`).

---

## 4. Response Schema

```typescript
interface SimulationMetrics {
  scheduled_tasks: number;
  unscheduled_tasks: number;
  blocks: number;
  total_scheduled_duration_hours: number;
  objective_score: number;
  total_expected_train_exposure: number;
}

interface SimulationDifference {
  scheduled_tasks_delta: number;
  blocks_delta: number;
  scheduled_duration_delta_hours: number;
  objective_delta: number;
  train_exposure_delta: number;
}

interface BlockTaskResponse {
  block_task_id: string;
  block_id: string;
  request_id: string;
  sequence: number;
}

interface OptimizedBlockResponse {
  block_id: string;
  run_id: string;
  section_id: string;
  start_time: string; // ISO Datetime
  end_time: string;   // ISO Datetime
  duration_hours: number;
  status: "SIMULATED" | "PROPOSED" | "APPROVED" | "CANCELLED";
  tasks: BlockTaskResponse[];
}

interface SimulationRunResponse {
  simulation_id: string;
  scenario_type: string;
  target_date: string;
  baseline: SimulationMetrics;
  scenario: SimulationMetrics;
  difference: SimulationDifference;
  newly_scheduled_tasks: string[];
  unscheduled_tasks_after_simulation: string[];
  moved_tasks: string[];
  baseline_blocks: OptimizedBlockResponse[];
  scenario_blocks: OptimizedBlockResponse[];
  explanation: string;
}
```

---

## 5. Example API Interaction

### Request
```http
POST /api/v1/simulation/run HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "scenario_type": "REMOVE_MAINTENANCE_WINDOW",
  "target_date": "2026-09-04",
  "window_id": "MW00001"
}
```

### Response (200 OK)
```json
{
  "simulation_id": "SIM_REMOVE_MAINTENANCE_WINDOW_20260904_161500_123456",
  "scenario_type": "REMOVE_MAINTENANCE_WINDOW",
  "target_date": "2026-09-04",
  "baseline": {
    "scheduled_tasks": 28,
    "unscheduled_tasks": 87,
    "blocks": 22,
    "total_scheduled_duration_hours": 37.5,
    "objective_score": 142500.0,
    "total_expected_train_exposure": 44
  },
  "scenario": {
    "scheduled_tasks": 28,
    "unscheduled_tasks": 87,
    "blocks": 22,
    "total_scheduled_duration_hours": 37.5,
    "objective_score": 142500.0,
    "total_expected_train_exposure": 44
  },
  "difference": {
    "scheduled_tasks_delta": 0,
    "blocks_delta": 0,
    "scheduled_duration_delta_hours": 0.0,
    "objective_delta": 0.0,
    "train_exposure_delta": 0
  },
  "newly_scheduled_tasks": [],
  "unscheduled_tasks_after_simulation": [],
  "moved_tasks": [
    "MR0003", "MR0011", "MR0016", "MR0019", "MR0034",
    "MR0036", "MR0038", "MR0046", "MR0062", "MR0073",
    "MR0090", "MR0100", "MR0120", "MR0137", "MR0140"
  ],
  "baseline_blocks": [ ... ],
  "scenario_blocks": [ ... ],
  "explanation": "Maintenance window MW00001 was removed from the simulation. The optimizer reassigned 15 feasible tasks to alternative windows where capacity allowed."
}
```

---

## 6. Architecture & Simulation Methodology

```text
Database (PostgreSQL / SQLite)
      ↓
OptimizerDataLoader.prepare_solver_inputs(target_date)
      ↓
Baseline Solve: MaintenanceBlockSolver.solve()
      ↓
In-Memory Scenario Transformation:
  - TRAFFIC_PLUS_20: ceil(expected_train_count * 1.20)
  - EMERGENCY_MAINTENANCE: priority_score = 1000.0 (bonus reward)
  - REMOVE_MAINTENANCE_WINDOW: filter out target window_id
      ↓
Scenario Solve: MaintenanceBlockSolver.solve()
      ↓
Comparison & Metrics Engine:
  - Metric deltas (scheduled_tasks_delta, blocks_delta, etc.)
  - Task diff tracking (newly_scheduled, unscheduled_after, moved_tasks)
  - Factual explainability generator
      ↓
SimulationRunResponse (200 OK, Read-Only, 0 DB writes)
```

---

## 7. Limitations & Modeling Boundary

1. **Static Time Windows**: Maintenance windows are discrete intervals. Dynamic rescheduling of individual train paths is outside the scope of block planning.
2. **Deterministic Section Capacity**: Non-overlapping constraints operate at the railway section level (`RailwaySection`). Simultaneous blocks on parallel tracks within the same section require multi-track configuration flags.
3. **Crew/Equipment Availability**: Solver currently assumes standard crew availability if tasks meet department compatibility constraints.
