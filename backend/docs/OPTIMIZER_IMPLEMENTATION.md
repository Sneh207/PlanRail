# PlanRail — OR-Tools CP-SAT Optimizer Implementation

## 1. Overview & Architecture

The PlanRail Optimization Engine implements a mathematical constraint satisfaction model using **Google OR-Tools CP-SAT** (`ortools.sat.python.cp_model`).

It schedules maintenance work requests onto eligible corridor sections while respecting maintenance window capacities, maximum block durations, non-overlapping section occupancy, and cross-department safety compatibility.

```
                    ┌─────────────────────────┐
                    │  Database / ORM Models  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  OptimizerDataLoader    │
                    │  (app/optimizer/data_   │
                    │   loader.py)            │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │ MaintenanceBlockSolver  │
                    │ (app/optimizer/solver.py│
                    │  CP-SAT Engine)         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   OptimizationResult    │
                    │  - Scheduled tasks      │
                    │  - Optimized blocks     │
                    │  - Explainability meta  │
                    └─────────────────────────┘
```

---

## 2. Mathematical Formulation

### 2.1 Decision Variables
* $x_{r, w} \in \{0, 1\}$: Binary variable indicating whether maintenance request $r$ is assigned to maintenance window $w$.
  * *Filtered Pre-Creation*: Only created when $r.\text{section\_id} == w.\text{section\_id}$, $w.\text{is\_feasible} == \text{True}$, and $r.\text{duration\_minutes} \le \min(w.\text{duration\_minutes}, \text{max\_block\_duration\_minutes})$.
* $y_w \in \{0, 1\}$: Binary variable indicating whether maintenance window $w$ is activated as a maintenance block.

### 2.2 Hard Operational Constraints

1. **At-Most-Once Scheduling**:
   $$\sum_{w \in W_{s(r)}} x_{r, w} \le 1 \quad \forall r \in R$$
   *Every maintenance request is scheduled at most once.*

2. **Section Consistency**:
   *Requests can only be assigned to windows belonging to the exact railway section.*

3. **Window Capacity & Maximum Block Duration Limit**:
   $$\sum_{r \in R_s} \text{duration\_minutes}(r) \cdot x_{r, w} \le \min(\text{window\_duration}(w), \text{max\_block\_duration}) \cdot y_w \quad \forall w \in W$$

4. **Window Activation Linking**:
   $$x_{r, w} \le y_w \quad \forall r \in R, \forall w \in W$$

5. **Same-Section Non-Overlap**:
   For any two maintenance windows $w_1, w_2$ on the same section where time intervals overlap:
   $$y_{w_1} + y_{w_2} \le 1$$

6. **Multi-Department Incompatibility Exclusion**:
   For any pair of requests $r_1, r_2$ where $\text{Compatibility}(\text{dept}(r_1), \text{dept}(r_2)) == \text{"INCOMPATIBLE"}$:
   $$x_{r_1, w} + x_{r_2, w} \le 1 \quad \forall w \in W$$

---

## 3. Objective Function & Scoring Weights

The objective balances operational urgency and train traffic impact:

$$\text{MAXIMIZE} \quad \sum_{(r,w)} \text{TaskReward}(r) \cdot x_{r, w} - \sum_{w} \text{WindowCost}(w) \cdot y_w$$

### 3.1 Task Reward Terms
$$\text{TaskReward}(r) = \text{BaseReward} + \text{PriorityReward} + \text{CriticalityReward} + \text{SeverityReward} + \text{OverdueReward}$$
* $\text{BaseReward} = 1000$
* $\text{PriorityReward} = \text{round}(\text{priority\_score}_r \times 15.0)$
* $\text{CriticalityReward} = \text{round}(\text{criticality\_score}_r \times 100.0)$
* $\text{SeverityReward} = \text{round}(\text{severity}_r \times 100.0)$
* $\text{OverdueReward} = \min(3000, \text{overdue\_days}_r \times 150)$

### 3.2 Window & Traffic Cost Terms
$$\text{WindowCost}(w) = \text{BaseBlockCost} + (\text{expected\_train\_count}_w \times 50) + \text{TrafficLevelPenalty}(w)$$
* $\text{BaseBlockCost} = 250$
* $\text{TrafficLevelPenalty}(\text{"LOW"}) = 0$
* $\text{TrafficLevelPenalty}(\text{"MEDIUM"}) = 100$
* $\text{TrafficLevelPenalty}(\text{"HIGH"}) = 400$

---

## 4. Solver Configuration & Performance

* **Engine**: Google OR-Tools CP-SAT (`CpSolver`)
* **Time Limit**: $5.0\text{ seconds}$
* **Random Seed**: $42$ (Deterministic & reproducible)
* **Search Workers**: $4$ parallel threads
* **Delhi–Agra Prototype Benchmark**:
  * Eligible requests evaluated: $123$
  * Feasible windows evaluated: $384$
  * Solve time: **$55.16\text{ ms}$**
  * Status: **OPTIMAL**
  * Blocks generated: $25$ blocks covering $31$ high-priority maintenance requests.

---

## 5. Explainability Metadata

Every generated block computes explainable factual metrics:
* `task_count`: Number of scheduled maintenance requests.
* `departments`: List of participating departments.
* `is_bundled`: `True` if multiple requests or cross-department tasks are packaged together.
* `duration_hours`: Exact total duration of scheduled tasks.
* `traffic_level` & `expected_train_count`: Traffic disruption metrics.
* `optimization_score`: Composite efficiency score ($0.0 - 100.0\%$) reflecting duration density and traffic lull utilization.

---

## 6. Assumptions & Limitations

> [!IMPORTANT]
> **The optimizer is traffic-aware but does not model individual train movements as decision variables.**
> Train impact is evaluated through aggregated hourly traffic counts and expected train density per maintenance window.

> [!NOTE]
> **Crew routing is deferred because the current crew dataset does not contain spatial/depot assignment information.**
> Crew availability remains advisory at the departmental level.
