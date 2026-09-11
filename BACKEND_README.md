# PlanRail AI — Backend Architecture & Developer Guide

This document is the **comprehensive technical guide for backend engineers, data scientists, and systems integrators**. It details the internal mechanics, component design, execution lifecycle, data contracts, and integration patterns of the PlanRail AI system.

---

## Table of Contents

- [1. Backend Architectural Philosophy](#1-backend-architectural-philosophy)
- [2. Component & Directory Layout](#2-component--directory-layout)
- [3. End-to-End Execution Flow](#3-end-to-end-execution-flow)
- [4. Module-by-Module Technical Reference](#4-module-by-module-technical-reference)
  - [4.1 Data Loader (`src/data_loader.py`)](#41-data-loader-srcdata_loaderpy)
  - [4.2 Feature Engineering (`src/feature_engineering.py`)](#42-feature-engineering-srcfeature_engineeringpy)
  - [4.3 Predictive Risk Engine (`src/ai/risk_model.py`)](#43-predictive-risk-engine-srcairisk_modelpy)
  - [4.4 Traffic Disruption Engine (`src/ai/traffic_impact.py`)](#44-traffic-disruption-engine-srcaitraffic_impactpy)
  - [4.5 Priority Intelligence Engine (`src/ai/priority_engine.py`)](#45-priority-intelligence-engine-srcaipriority_enginepy)
  - [4.6 CP-SAT Block Optimizer (`src/optimizer/block_optimizer.py`)](#46-cp-sat-block-optimizer-srcoptimizerblock_optimizerpy)
  - [4.7 Operational Constraints (`src/optimizer/constraints.py`)](#47-operational-constraints-srcoptimizerconstraintspy)
  - [4.8 Decision Explainer (`src/explainability/explainer.py`)](#48-decision-explainer-srcexplainabilityexplainerpy)
  - [4.9 What-If Scenario Engine (`src/what_if/scenario_engine.py`)](#49-what-if-scenario-engine-srcwhat_ifscenario_enginepy)
  - [4.10 Baseline Comparison Simulator (`src/baseline_comparison.py`)](#410-baseline-comparison-simulator-srcbaseline_comparisonpy)
- [5. Data Contracts & Output Schemas](#5-data-contracts--output-schemas)
  - [5.1 DataFrame In-Memory Transformations](#51-dataframe-in-memory-transformations)
  - [5.2 `optimized_blocks.json` Schema](#52-optimized_blocksjson-schema)
  - [5.3 `ai_scores.csv` Schema](#53-ai_scorescsv-schema)
- [6. Building a Production REST / FastAPI Service](#6-building-a-production-rest--fastapi-service)
- [7. Error Handling, Fallbacks & Safety Defaults](#7-error-handling-fallbacks--safety-defaults)
- [8. Extending the Engine (New Corridors, Rules, & Retraining)](#8-extending-the-engine-new-corridors-rules--retraining)

---

## 1. Backend Architectural Philosophy

PlanRail avoids "one big black-box model" in favor of a **hybrid architecture** that uses the right tool for each distinct computational subproblem:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            HYBRID ARCHITECTURAL SPLIT                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Machine Learning (XGBoost)       → Probability of asset failure          │
│ 2. Analytical Physics & Timetable   → Train disruption & headway cascade    │
│ 3. Domain Multi-Criteria Scoring    → Maintenance priority harmonization   │
│ 4. Constraint Optimization (CP-SAT) → Crew allocation, bundling, scheduling │
│ 5. TreeSHAP + Natural Language      → Deterministic controller auditability │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why this separation matters for Railways:
- **ML for uncertainty:** Predicting asset deterioration from multi-variable sensor/age data is stochastic and nonlinear $\rightarrow$ Solved with **XGBoost**.
- **Analytical logic for timetables:** Train headways and block windows follow strict physical timetables $\rightarrow$ Solved with **deterministic formulas**.
- **Constraint Programming for scheduling:** Combining cross-departmental crews, non-overlapping windows, and high-priority train exclusion is NP-hard $\rightarrow$ Solved with **Google OR-Tools CP-SAT (Satisfiability Modulo Theories)**.
- **Auditability for safety:** Sectional train controllers require exact reasons before granting line possession $\rightarrow$ Solved with **SHAP attribution + rule breakdowns**.

---

## 2. Component & Directory Layout

```
Railway/
│
├── run_pipeline.py                 # Pipeline Orchestrator (CLI & programmatic API)
├── retrain_model.py                # Offline Optuna HPO training loop
├── requirements.txt                # Python environment requirements
│
├── PlanRail_Delhi_Agra_Dataset/     # Raw CSV telemetry & historical logs
│   ├── maintenance_tasks_v5_strong_signal.csv
│   └── maintenance_tasks_v6_final_xgb.csv   # Active dataset (10,000 tasks)
│
├── models/
│   └── risk_model_xgb.joblib       # Serialized XGBoost model + threshold + metadata
│
├── output/                         # Artifact output directory
│   ├── ai_scores.csv
│   ├── optimized_blocks.json
│   ├── explainability_report.txt
│   ├── training_report.txt
│   ├── confusion_matrix.png
│   ├── roc_curve.png
│   └── shap_summary_beeswarm.png
│
└── src/                            # Core python package
    ├── __init__.py
    ├── config.py                   # Central source of truth (weights, timetables, paths)
    ├── data_loader.py              # I/O ingestion, type-casting, timetable extraction
    ├── feature_engineering.py      # Feature normalization and derived indicators
    ├── baseline_comparison.py      # FCFS & Priority-only benchmark runner
    │
    ├── ai/                         # Machine learning & analytical engines
    │   ├── risk_model.py           # XGBoost classifier + SHAP explanations
    │   ├── priority_engine.py      # Multi-criteria weighted priority scorer
    │   └── traffic_impact.py       # Headway disruption & delay propagation model
    │
    ├── optimizer/                  # Mathematical scheduling solvers
    │   ├── block_optimizer.py      # CP-SAT constraint optimizer & task bundling
    │   └── constraints.py          # Crew shifts, compatibility, timetable windows
    │
    ├── explainability/             # Explainable AI & audit reports
    │   └── explainer.py            # Natural language reason generator
    │
    └── what_if/                    # Simulation & sensitivity analysis
        └── scenario_engine.py      # Parametric perturbation & delta benchmarking
```

---

## 3. End-to-End Execution Flow

When `run_pipeline.py::run_pipeline()` executes, it runs a 9-step pipeline:

```mermaid
sequenceDiagram
    autonumber
    participant CLI as run_pipeline.py
    participant DL as DataLoader
    participant FE as FeatureEngineering
    participant RM as RiskModel (XGBoost)
    participant TM as TrafficImpactModel
    participant PE as PriorityEngine
    participant OPT as BlockOptimizer (OR-Tools)
    participant EXP as Explainer
    participant BASE as BaselineComparison
    participant FS as File System / Output

    CLI->>DL: load_maintenance_tasks()
    DL-->>CLI: DataFrame (10,000 rows)
    
    CLI->>FE: engineer_features(df)
    FE-->>CLI: DataFrame + Normalized & Derived columns
    
    CLI->>RM: predict(df)
    RM-->>CLI: DataFrame + [risk_probability, risk_score, risk_category]
    
    CLI->>TM: score_batch(df)
    TM-->>CLI: DataFrame + [traffic_impact_score, traffic_worst_case, traffic_best_case]
    
    CLI->>PE: score_batch(df)
    PE-->>CLI: DataFrame + [priority_score, priority_category, priority_components]
    
    CLI->>OPT: optimize(df, traffic_model)
    OPT->>OPT: _find_bundles() + CP-SAT Solve
    OPT-->>CLI: {blocks, summary, unscheduled_tasks, scheduling_reasons}
    
    CLI->>EXP: generate_report(df, blocks, summary)
    EXP-->>CLI: Natural-language report text
    
    CLI->>BASE: compare_all(FCFS, PriorityOnly, PlanRail)
    BASE-->>CLI: Empirical Benchmark Markdown Table
    
    CLI->>FS: Export CSV, JSON, TXT to output/
```

---

## 4. Module-by-Module Technical Reference

### 4.1 Data Loader (`src/data_loader.py`)

#### Purpose
Safely ingests CSV files, coerces numeric data types, filters corrupt rows, and provides timetable accessors.

#### Key Functions
- `load_maintenance_tasks(path: str = None) -> pd.DataFrame`
  - Loads task records from `config.MAINTENANCE_TASKS_CSV`.
  - Coerces 12 numeric fields (`severity`, `criticality`, `overdue_days`, `condition_score`, etc.) with `errors="coerce"`.
  - Drops records missing `task_id` or `section_id`.
- `load_historical_maintenance(path: str = None) -> pd.DataFrame`
  - Loads records for offline retraining; validates presence of all columns in `config.RISK_FEATURE_COLUMNS` and `config.RISK_TARGET_COLUMN`.
- `get_available_windows(section_id: str) -> list[dict]`
  - Computes hourly time windows excluding high-priority train intervals (`has_priority == True`).

---

### 4.2 Feature Engineering (`src/feature_engineering.py`)

#### Purpose
Transforms raw telemetry into normalized $[0, 100]$ features and computes domain-specific health indicators.

#### Transformations
1. **Min-Max Clipping to $[0, 100]$ Scale:**
   $$\text{val}_{\text{norm}} = \text{clip}\left(\frac{\text{val} - \text{low}}{\text{high} - \text{low}} \times 100, 0, 100\right)$$
   Ranges configured in `config.NORMALIZATION_RANGES` (e.g. `severity`: $1\text{--}10$, `overdue_days`: $0\text{--}60$, `condition_score`: $0\text{--}100$).
2. **Derived Domain Features:**
   - **`overdue_ratio`**: How overdue an inspection is relative to its annual cycle:
     $$\text{overdue\_ratio} = \min\left(\frac{\text{overdue\_days}}{\text{maintenance\_frequency} \times 30} \times 100, 100\right)$$
   - **`failure_rate`**: Historic failures normalized by asset operational age:
     $$\text{failure\_rate} = \min\left(\frac{\text{historical\_failures}}{\text{asset\_age}} \times 20, 100\right)$$
   - **`condition_risk`**: Complement of structural health:
     $$\text{condition\_risk} = 100 - \text{condition\_score}$$

---

### 4.3 Predictive Risk Engine (`src/ai/risk_model.py`)

#### Purpose
Executes XGBoost ML inference to calculate the probability $P(\text{became\_critical} = 1)$ and categorizes tasks.

#### Class: `RiskModel`
```python
class RiskModel:
    def __init__(self, model=None)
    def train(self, df: pd.DataFrame, save_path: str = None) -> dict
    def predict(self, df: pd.DataFrame) -> pd.DataFrame
    @classmethod
    def load(cls, model_path: str) -> "RiskModel"
    def get_feature_importances(self) -> dict
    def get_shap_explanation(self, task_features: dict) -> dict
```

#### Key Technical Decisions
- **Optimized Recall Thresholding (`_tune_threshold`):**  
  Standard ML classifiers default to $0.50$. In railway track maintenance, a False Negative (undetected rail fracture) causes derailments, while a False Positive results in a precautionary manual check. The threshold is mathematically tuned using precision-recall curves to guarantee $\ge 85\%$ Recall on critical failures (calibrated threshold: **$0.5421$**).
- **Categorization Tiers:**
  - $P < 0.30 \implies \text{LOW}$
  - $0.30 \le P < 0.70 \implies \text{MEDIUM}$
  - $P \ge 0.70 \implies \text{HIGH}$

---

### 4.4 Traffic Disruption Engine (`src/ai/traffic_impact.py`)

#### Purpose
Quantifies the operational cost of placing a physical maintenance possession on a track section during specific time windows.

#### Class: `TrafficImpactModel`
```python
class TrafficImpactModel:
    def __init__(self, weights: dict = None)
    def score_window(self, section_id: str, start_minutes: int, end_minutes: int) -> dict
    def score_batch(self, df: pd.DataFrame) -> pd.DataFrame
```

#### Analytical Scoring Formula
The score $T \in [0, 100]$ combines 5 weighted factors (`config.TRAFFIC_WEIGHTS`):
$$T = 0.30 \cdot W_{\text{trains}} + 0.25 \cdot W_{\text{headway}} + 0.20 \cdot W_{\text{peak}} + 0.15 \cdot W_{\text{util}} + 0.10 \cdot W_{\text{delay}}$$

- **Peak Hour Windows:** Morning ($06:00\text{--}10:00$) and Evening ($17:00\text{--}21:00$) receive a heavy penalty ($100$ vs $15$).
- **Headway Ratio:** $\frac{\text{block\_duration}}{\text{avg\_section\_headway}}$ measures how many train paths are severed.
- **Delay Cascade:** Expected delay in train-minutes $= \text{trains} \times (\text{duration} \times 0.5) \times 1.3$ (accounting for knock-on network propagation).

---

### 4.5 Priority Intelligence Engine (`src/ai/priority_engine.py`)

#### Purpose
Harmonizes multi-source criteria into a transparent, actionable score ($0\text{--}100$) deciding which tasks get scheduled first.

#### Class: `PriorityEngine`
```python
class PriorityEngine:
    def __init__(self, weights: dict = None)
    def score_task(self, severity_norm, criticality_norm, overdue_norm, risk_score, traffic_impact) -> dict
    def score_batch(self, df: pd.DataFrame) -> pd.DataFrame
```

#### Weight Distribution (`config.PRIORITY_WEIGHTS`)
- **Severity ($30\%$):** Physical defect rating.
- **Criticality ($25\%$):** Mainline vs loop line vs crossover asset location.
- **Overdue ($20\%$):** Days past mandatory inspection schedule.
- **Risk ($15\%$):** XGBoost failure probability ($P_{\text{risk}} \times 100$).
- **Traffic Impact ($10\%$):** Minimizing disruption to passengers.

Tasks are categorized: **LOW ($0\text{--}35$)**, **MEDIUM ($35\text{--}60$)**, **HIGH ($60\text{--}80$)**, **CRITICAL ($80\text{--}100$)**.

---

### 4.6 CP-SAT Block Optimizer (`src/optimizer/block_optimizer.py`)

#### Purpose
Solves the combinatorial multi-task bundling, crew assignment, and time-slot scheduling problem using **Google OR-Tools CP-SAT**.

#### Class: `BlockOptimizer`
```python
class BlockOptimizer:
    def __init__(self, objective_weights: dict = None)
    def optimize(self, tasks_df: pd.DataFrame, traffic_model=None) -> dict
    def _find_bundles(self, tasks: list[dict]) -> list[list[dict]]
    def _schedule_section(...) -> tuple[list[dict], list[dict], dict]
```

#### Multi-Task Bundling Algorithm (`_find_bundles`)
1. Sorts all section tasks by `priority_score` descending.
2. For each unassigned task, initializes a candidate bundle.
3. Iterates over remaining tasks on the same section:
   - Verifies departmental compatibility via `constraints.check_department_compatibility()`.
   - Verifies that aggregated departmental crew counts do not exceed `config.CREW_CAPACITY`.
4. Merges tasks into a unified block whose duration equals $\max(\text{duration}_i)$, eliminating redundant line possessions.

#### CP-SAT Mathematical Formulation
- **Decision Variables:**
  - $x_{b, w} \in \{0, 1\}$: Binary variable indicating if bundle $b$ is assigned to available window $w$.
- **Objective Function (Minimize):**
  $$\min \sum_{b, w} x_{b, w} \cdot \left[ w_1 \cdot \text{Delay Penalty}_b + w_2 \cdot \text{Disruption}_{w} + w_3 \cdot \text{Duration}_b - w_4 \cdot \text{Priority}_b \right]$$
- **Constraints:**
  - **Single Assignment:** $\sum_{w} x_{b, w} \le 1, \quad \forall b$
  - **No Window Overlap:** Bundles assigned to window $w$ cannot exceed window capacity or violate minimum gap ($30\text{ min}$).
  - **Global Crew Balance:** Concurrent active blocks across all 5 sections cannot exceed departmental crew limits.
  - **Timetable Clearance:** Windows intersecting Rajdhani/Shatabdi train paths are strictly pruned prior to variable instantiation.

---

### 4.7 Operational Constraints (`src/optimizer/constraints.py`)

#### Purpose
Defines physical Indian Railways rules: crew shift limits, department compatibility matrices, and timetable exclusion intervals.

#### Key Functions
- `get_blocked_windows(section_id: str) -> list[tuple[int, int]]`: Returns intervals (in minutes from midnight) where express trains pass.
- `get_available_slots(section_id: str) -> list[tuple[int, int]]`: Inverts blocked windows within $[0, 1440]$ minutes.
- `check_department_compatibility(departments: list[str]) -> bool`: Evaluates pairwise safety compatibility:
  - `(ENGINEERING, OHE) = True` (Track & Catenary can work in tandem)
  - `(ENGINEERING, SIGNALLING) = True` (Track & Signals can work in tandem)
  - `(OHE, S&T) = False` (High-voltage catenary isolation conflicts with certain signal power testing)
- `get_task_dependencies(tasks: list[dict]) -> list[tuple]`: Enforces sequential predecessor-successor constraints (e.g. `TRACK_REPAIR` requires Engineering $\rightarrow$ OHE $\rightarrow$ Signalling).

---

### 4.8 Decision Explainer (`src/explainability/explainer.py`)

#### Purpose
Transforms internal vector states, SHAP scores, and solver decisions into auditable reports for rail controllers.

#### Key Functions
- `explain_task_full(task: dict, feature_importances: dict, block: dict) -> str`: Generates breakdown of priority components and SHAP risk drivers.
- `explain_block(block: dict) -> str`: Explains why a specific window (e.g., 02:00–04:00 vs 08:00–10:00) was chosen, which crews were matched, and minutes saved via bundling.
- `generate_report(tasks_df, blocks, summary, feature_importances) -> str`: Aggregates the complete 24-hour executive controller briefing.

---

### 4.9 What-If Scenario Engine (`src/what_if/scenario_engine.py`)

#### Purpose
Enables non-destructive simulation of external shocks (traffic surges, crew strikes, delayed works).

#### Method Signature
```python
def run_scenario(
    self,
    tasks_df: pd.DataFrame,
    scenario_name: str = "Modified",
    traffic_change_pct: float = 0.0,
    crew_changes: dict = None,             # e.g. {"ENGINEERING": 1}
    severity_multiplier: float = 1.0,      # e.g. 1.5 (+50% severity)
    remove_sections: list[str] = None,     # e.g. ["S01_AGC_TDL"]
    task_duration_changes: dict = None,    # e.g. {"H00042": 240}
    schedule_window: tuple[int, int] = None, # e.g. (22*60, 4*60)
    department_unavailable: list[str] = None # e.g. ["OHE"]
) -> dict
```
Automatically resets global state (`config.CREW_CAPACITY`, `config.SCHEDULE_START`) in a `finally` block to prevent test contamination.

---

### 4.10 Baseline Comparison Simulator (`src/baseline_comparison.py`)

#### Purpose
Quantifies PlanRail's value proposition against traditional railway practices:
1. **FCFS (First-Come-First-Served):** Greedily assigns tasks in submission order into the first open slot without bundling or traffic optimization.
2. **Priority-Only Heuristic:** Greedily assigns high-priority tasks without cross-departmental bundling.
3. **PlanRail CP-SAT:** Integrated multi-department optimization.

---

## 5. Data Contracts & Output Schemas

### 5.1 DataFrame In-Memory Transformations

During pipeline execution, the main `tasks_df` DataFrame transitions through the following schema expansions:

```
[Raw CSV: 14 columns]
       ↓ (Feature Engineering)
[+9 Normalized columns (_norm), +3 Derived columns (overdue_ratio, failure_rate, condition_risk)]
       ↓ (XGBoost Risk Model)
[+risk_probability (float 0-1), +risk_score (0-100), +risk_category (LOW/MED/HIGH)]
       ↓ (Traffic Impact Model)
[+traffic_impact_score, +traffic_worst_case, +traffic_best_case]
       ↓ (Priority Engine)
[+priority_score (0-100), +priority_category, +priority_components (dict)]
```

---

### 5.2 `optimized_blocks.json` Schema

```json
{
  "blocks": [
    {
      "block_id": "B001",
      "section": "S03_ALJN_CNJ",
      "start": "18:00",
      "end": "19:00",
      "start_minutes": 1080,
      "end_minutes": 1140,
      "duration_minutes": 60,
      "tasks": ["H07918", "H04428", "H07150", "H05318"],
      "task_count": 4,
      "departments": ["SIGNALLING", "ENGINEERING", "OHE"],
      "train_conflicts": 0,
      "traffic_impact": 66.0,
      "expected_delay": 140.4,
      "avg_priority": 76.7,
      "avg_risk": 0.9312,
      "time_saved": 180,
      "bundled": true,
      "is_night_block": false,
      "scheduling_reason": [
        "Medium-traffic window: acceptable disruption",
        "4 compatible tasks bundled (SIGNALLING, ENGINEERING, OHE), saving 180 min",
        "Required crews available",
        "No priority train (Rajdhani/Shatabdi) conflict"
      ]
    }
  ],
  "summary": {
    "total_blocks": 15,
    "total_block_hours": 15.0,
    "tasks_scheduled": 119,
    "tasks_unscheduled": 9881,
    "coverage_pct": 1.2,
    "train_conflicts": 0,
    "bundled_blocks": 15,
    "time_saved_minutes": 6240,
    "estimated_train_delay": 1376.7,
    "night_blocks": 5,
    "dependency_chains": 5,
    "crew_utilization_pct": 12.5,
    "avg_traffic_impact": 51.6
  },
  "unscheduled_tasks": ["H00002", "H00005"]
}
```

---

### 5.3 `ai_scores.csv` Schema

Exported table containing granular scores for each input task:

| Column | Type | Example | Description |
|:---|:---:|:---:|:---|
| `task_id` | str | `H02337` | Unique task ID |
| `asset_id` | str | `A202` | Physical asset identifier |
| `section_id` | str | `S04_CNJ_NDK` | Corridor section |
| `department` | str | `SIGNALLING` | Maintenance department |
| `severity` | int | `9` | Raw defect severity ($1\text{--}10$) |
| `criticality` | int | `10` | Operational criticality ($1\text{--}10$) |
| `condition_score` | float | `36.0` | Asset health ($0\text{--}100$) |
| `risk_probability` | float | `0.9782` | XGBoost failure probability ($0.0\text{--}1.0$) |
| `risk_category` | str | `HIGH` | Low / Medium / High |
| `traffic_impact_score`| float | `39.0` | Disruption rating ($0\text{--}100$) |
| `priority_score` | float | `80.1` | Composite priority score ($0\text{--}100$) |
| `priority_category` | str | `CRITICAL` | LOW / MEDIUM / HIGH / CRITICAL |

---

## 6. Building a Production REST / FastAPI Service

To expose PlanRail AI as an HTTP microservice for web or mobile dashboards, integrate directly with `run_pipeline.py` or individual modules:

```python
# app.py — Example FastAPI Service Wrapper
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from src.ai.risk_model import RiskModel
from src.optimizer.block_optimizer import BlockOptimizer
from src.ai.traffic_impact import TrafficImpactModel
from src import config

app = FastAPI(title="PlanRail AI Backend API", version="1.0.0")

# Load model once at startup
risk_model = RiskModel.load("models/risk_model_xgb.joblib")
traffic_model = TrafficImpactModel()
optimizer = BlockOptimizer()

class SingleTaskPayload(BaseModel):
    task_id: str
    asset_id: str
    section_id: str
    department: str
    severity: int
    criticality: int
    overdue_days: int
    condition_score: float
    historical_failures: int
    train_density: float
    asset_age: float
    maintenance_frequency: float
    previous_defects: int

@app.post("/api/v1/predict-risk")
def predict_risk(payload: SingleTaskPayload):
    """Predict failure risk for an individual asset defect."""
    df = pd.DataFrame([payload.model_dump()])
    scored_df = risk_model.predict(df)
    row = scored_df.iloc[0]
    return {
        "task_id": row["task_id"],
        "risk_probability": float(row["risk_probability"]),
        "risk_category": row["risk_category"],
        "risk_score": float(row["risk_score"])
    }

@app.post("/api/v1/optimize-schedule")
def optimize_schedule():
    """Trigger 24-hour CP-SAT optimization across corridor."""
    from run_pipeline import run_pipeline
    result = run_pipeline(run_baseline=False)
    return {
        "status": "success",
        "total_blocks": len(result["blocks"]),
        "summary": result["summary"],
        "blocks": result["blocks"]
    }
```

---

## 7. Error Handling, Fallbacks & Safety Defaults

1. **Missing Trained Model Fallback (`run_pipeline.py:118`):**  
   If `models/risk_model_xgb.joblib` is deleted or missing, the pipeline logs a warning and automatically falls back to an **expert-weighted heuristic failure score**:
   $$\text{Fallback Risk} = 0.30 \cdot S + 0.25 \cdot C + 0.20 \cdot (100 - \text{Condition}) + 0.15 \cdot O + 0.10 \cdot H$$
2. **Missing Available Windows:**  
   If a corridor section has no viable block windows (e.g. dense high-speed traffic), tasks are gracefully diverted to `unscheduled_tasks` without crashing the CP-SAT solver.
3. **Windows UTF-8 Encoding Safeguard (`run_pipeline.py:60`):**  
   Automatically executes `sys.stdout.reconfigure(encoding="utf-8")` on Windows hosts to handle Unicode characters and box-drawing tables without `UnicodeEncodeError`.

---

## 8. Extending the Engine (New Corridors, Rules, & Retraining)

### Adding a New Corridor Section
To add a new corridor (e.g. `S06_NDL_GZB` for New Delhi to Ghaziabad):
1. Open [`src/config.py`](src/config.py).
2. Append section characteristics to `SECTION_UTILIZATION`, `AVG_HEADWAY_MINUTES`, and `ALTERNATIVE_ROUTES`.
3. Add the hourly train frequency and priority flags to `TRAIN_TIMETABLE["S06_NDL_GZB"]`.
4. Re-run `python run_pipeline.py`.

### Tuning Optimization Weights
To favor passenger punctuality over maintenance speed, adjust `OPTIMIZER_WEIGHTS` in [`src/config.py`](src/config.py):
```python
OPTIMIZER_WEIGHTS = {
    "maintenance_delay":    0.15,
    "expected_train_delay": 0.40,   # Increased punctuality priority
    "traffic_disruption":   0.25,   # Increased disruption avoidance
    "crew_idle_time":       0.05,
    "block_duration":       0.05,
    "risk_exposure":        0.10,
}
```

### Triggering Model Retraining
When historical failure records are updated:
```bash
python retrain_model.py
```
This launches 100 Optuna trials searching parameter space, regenerates ROC and Confusion Matrix plots in `output/`, and updates `models/risk_model_xgb.joblib`.
