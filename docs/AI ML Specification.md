# PlanRail — AI/ML Specification

## 1. AI Philosophy

AI should solve real problems in the system.

Do not add AI merely for presentation.

PlanRail has three prediction/intelligence components:

1. Maintenance Priority
2. Maintenance Risk
3. Traffic/Operational Impact

Scheduling itself is handled by OR-Tools.

---

# 2. Maintenance Priority

## Prototype

Use weighted scoring.

```text
Priority =
0.30 × Severity
+ 0.25 × Criticality
+ 0.20 × Overdue
+ 0.15 × Risk
+ 0.10 × Traffic Impact
```

Normalize every component to 0–100.

Output:

```text
0–39 = LOW
40–69 = MEDIUM
70–84 = HIGH
85–100 = CRITICAL
```

---

# 3. Maintenance Risk Model

Goal:

Predict probability that an asset/task becomes critical.

Features:

```text
asset age
condition score
severity
criticality
overdue days
maintenance frequency
historical failures
train density
previous defects
```

Preferred model:

XGBoost.

Fallback:

Random Forest.

Output:

```text
risk_probability
risk_category
```

Example:

```text
Risk = 82%

Category = HIGH
```

---

# 4. Traffic Impact

Predict or estimate traffic impact using:

```text
train count
train type
historical delay
section utilization
freight demand
time of day
day of week
```

For prototype, a statistical model or engineered traffic score is acceptable.

Do not claim real-time prediction if only historical/static data is being used.

---

# 5. Explainability

For each prediction, return major contributing factors.

Example:

```text
Priority = 91

Main reasons:

High asset criticality
+22

Overdue by 12 days
+19

High failure risk
+21

High train density
+14
```

If using XGBoost, use feature importance/SHAP if feasible.

---

# 6. Optimization Inputs

AI outputs:

```text
priority
risk
traffic impact
```

These are passed to the optimization engine.

---

# 7. AI Pipeline

```text
Raw Data
   ↓
Cleaning
   ↓
Feature Engineering
   ↓
Prediction
   ↓
Priority/Risk
   ↓
Optimization
```

---

# 8. Evaluation

Priority/risk model:

* Precision
* Recall
* F1
* ROC-AUC where appropriate

Optimization:

* Blocks reduced
* Block hours reduced
* Train conflicts
* Maintenance coverage
* Critical task completion

The optimization metrics are more important for the SIH demonstration than claiming extremely high ML accuracy.

---

# 9. Data Limitation

Real TMS/SMMS/TDMS/COA maintenance records are not assumed to be publicly available.

The prototype must clearly label synthetic maintenance data.

Synthetic data should be generated using rules derived from official railway maintenance documentation rather than random values.
