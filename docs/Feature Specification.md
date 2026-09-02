# PlanRail — Feature Specification

# F-01 Dashboard

## Purpose

Give the controller an overview of the railway maintenance situation.

## Components

KPI cards:

* Pending Tasks
* Critical Tasks
* Available Windows
* Planned Blocks
* Block Hours
* Maintenance Coverage

Charts:

* Maintenance by department
* Risk distribution
* Block utilization
* Before vs After optimization

---

# F-02 Railway Map

Display:

* Stations
* Railway sections
* Assets
* High-risk sections
* Maintenance locations

Clicking a section opens:

```text
Section ID
Stations
Traffic level
Assets
Pending tasks
Critical tasks
Risk score
Recommended block
```

---

# F-03 Maintenance Tasks

Table columns:

```text
Task ID
Department
Asset
Section
Severity
Criticality
Overdue
Risk
Priority
Status
```

Filters:

* Department
* Severity
* Risk
* Section
* Status

---

# F-04 AI Priority

Button:

`Calculate Priority`

Output:

```text
Priority Score: 91/100
Risk: 78%
Category: CRITICAL
```

---

# F-05 Generate Plan

Main button:

`GENERATE OPTIMAL PLAN`

Process:

```text
Load tasks
→ Calculate priority
→ Check traffic
→ Find available windows
→ Bundle compatible tasks
→ Run OR-Tools
→ Validate
→ Return plan
```

---

# F-06 Block Plan

Display blocks using a timeline/Gantt-style interface.

Example:

```text
10:00 ───────── 12:00

Engineering + OHE

Section: S04
Tasks: M001, M002
Traffic: LOW
Conflicts: 0
```

---

# F-07 Recommendation Details

Show:

```text
Recommended Block
Section
Time
Duration

Included Tasks

Why selected:
- High priority
- Low traffic
- Compatible tasks
- No train conflict

Expected benefit
```

---

# F-08 What-If Simulator

Controls:

```text
Traffic: Normal / +10% / +20% / +30%

Available windows:
Normal / Reduced

Emergency task:
None / Add

Block:
Select block → Cancel
```

Click:

`SIMULATE`

Return:

```text
Original Plan
New Plan

Blocks: 9 → 11
Hours: 18 → 22
Conflicts: 3 → 5
Coverage: 94% → 91%
```

---

# F-09 Plan Approval

Buttons:

* Approve
* Modify
* Reject

Approval changes the plan status.

---

# F-10 Analytics

Show:

```text
Before Optimization
After Optimization
Improvement
```

Important metrics:

* Blocks reduced
* Block hours saved
* Conflicts reduced
* Maintenance coverage
* Critical tasks completed

---

# F-11 Data Upload

Admin can upload CSV files.

Required files:

* trains.csv
* stations.csv
* sections.csv
* assets.csv
* maintenance_tasks.csv
* block_windows.csv

Uploaded data must be validated before insertion.
