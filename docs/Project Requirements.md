# PlanRail — Project Requirements

## 1. Users

### Railway Controller / Planner

Can:

* View railway network
* View maintenance tasks
* View train traffic
* Generate optimized plans
* Review AI recommendations
* Approve/reject/modify plans
* Run what-if simulations
* View analytics

### Maintenance Department User

Can:

* View assigned maintenance tasks
* View task priority
* View recommended maintenance window
* View block details

### Admin

Can:

* Manage users
* Upload datasets
* Manage railway sections
* Manage maintenance records

---

# 2. Functional Requirements

## FR-01 — Dashboard

Display:

* Total railway sections
* Total assets
* Pending maintenance
* Critical maintenance
* Planned blocks
* Total block hours
* Estimated maintenance coverage

---

## FR-02 — Railway Network

Display Delhi–Agra railway sections on an interactive map.

Each section should show:

* Section ID
* Start station
* End station
* Asset count
* Maintenance count
* Traffic level
* Risk level

---

## FR-03 — Maintenance Management

Display maintenance tasks with:

* Task ID
* Department
* Asset
* Section
* Maintenance type
* Severity
* Criticality
* Due date
* Overdue days
* Estimated duration
* Required crew
* AI priority
* Risk score

---

## FR-04 — AI Priority

Calculate a priority score from 0–100.

Factors may include:

* Severity
* Asset criticality
* Overdue duration
* Failure risk
* Train density
* Historical maintenance behavior

---

## FR-05 — Risk Prediction

Predict the probability that an asset/task becomes critical within a defined period.

Output:

* Risk probability
* Risk category
* Main contributing factors

---

## FR-06 — Train Traffic

Display:

* Train number
* Train type
* Route
* Section
* Scheduled arrival/departure
* Historical delay
* Expected delay/traffic impact

---

## FR-07 — Block Optimization

The system should:

1. Collect pending maintenance tasks.
2. Calculate priority.
3. Identify possible maintenance windows.
4. Check train conflicts.
5. Check task compatibility.
6. Bundle compatible tasks.
7. Optimize block selection.
8. Generate recommended blocks.

---

## FR-08 — Explainable Recommendation

Every recommended block should provide:

* Why the block was selected
* Tasks included
* Priority of tasks
* Traffic level
* Conflict status
* Estimated benefit

---

## FR-09 — What-If Simulation

The user should be able to change scenarios such as:

* Increase traffic
* Cancel a block
* Add emergency maintenance
* Reduce available maintenance windows
* Change maintenance duration

The system should regenerate the plan and compare it with the original.

---

## FR-10 — Analytics

Show:

* Block reduction
* Block hours saved
* Train conflicts reduced
* Maintenance coverage
* Critical task completion
* Department-wise maintenance
* Risk distribution

---

# 3. Non-Functional Requirements

## Performance

Prototype optimization should ideally return within a few seconds for the selected dataset.

## Reliability

Invalid data should not crash the application.

## Explainability

AI recommendations must provide understandable reasons.

## Security

Authentication should exist in the MVP, but enterprise-grade security is future scope.

## Scalability

Architecture should allow expansion from Delhi–Agra to additional corridors later.

---

# 4. Explicit Non-Requirements

Do NOT build during this MVP:

* Real railway control
* Real TMS integration
* Real SMMS integration
* Real TDMS integration
* Real COA integration
* Nationwide railway optimization
* Mobile application
* Microservices architecture
* Kubernetes
* Autonomous railway decision-making
