# PlanRail 🚆

## AI-Powered Railway Maintenance Block Planning System

PlanRail is an AI-assisted decision-support platform designed to optimize railway maintenance block planning.

It coordinates maintenance activities across Engineering, OHE and Signalling while considering train operations, maintenance priority, asset risk and available maintenance windows.

---

# Problem

Railway maintenance activities may be planned independently by different departments.

This can lead to:

* Repeated blocks
* Poor coordination
* Unnecessary train disruption
* Under-utilization of maintenance windows
* Difficulty prioritizing critical assets

---

# Solution

PlanRail combines:

```text
Railway Data
+
Maintenance Data
+
AI Risk Prediction
+
Traffic Analysis
+
OR-Tools Optimization
```

to generate coordinated maintenance block recommendations.

---

# Key Features

### AI Maintenance Priority

Ranks maintenance tasks based on:

* severity
* asset criticality
* overdue duration
* failure risk
* traffic impact

### Predictive Risk

Predicts the probability of maintenance becoming critical.

### Intelligent Maintenance Bundling

Identifies compatible maintenance tasks that can potentially be performed during the same block.

### Constraint Optimization

Uses Google OR-Tools to generate maintenance plans while considering operational constraints.

### Explainable AI

Shows why a task or block was recommended.

### What-If Simulation

Allows controllers to test scenarios such as:

* increased train traffic
* cancelled blocks
* emergency maintenance
* reduced maintenance windows

### GIS Dashboard

Visualizes railway sections, assets, risks and maintenance plans.

---

# Architecture

```text
React
 ↓
FastAPI
 ↓
PostgreSQL/PostGIS
 ↓
AI + Optimization
 ↓
Optimized Maintenance Plan
```

---

# Technology Stack

Frontend:

* React
* Vite
* Tailwind CSS
* Leaflet
* Recharts

Backend:

* Python
* FastAPI
* SQLAlchemy

Database:

* PostgreSQL
* PostGIS

AI:

* Scikit-learn
* XGBoost
* Pandas
* NumPy

Optimization:

* Google OR-Tools

---

# Data

The prototype uses:

* Public railway datasets
* Historical train data
* Railway geospatial data
* Freight statistics
* Official railway maintenance documentation
* Domain-calibrated synthetic maintenance data

Real TMS/SMMS/TDMS/COA data is not assumed to be publicly available.

---

# Prototype Corridor

The initial prototype focuses on:

**Delhi–Agra railway corridor**

The architecture is designed to support additional corridors later.

---

# Human-in-the-Loop

PlanRail does not autonomously control railway operations.

AI generates recommendations.

A railway controller reviews and approves the final plan.

---

# Expected Demonstration

The prototype demonstrates:

```text
Independent Maintenance Planning
              ↓
          PlanRail
              ↓
AI Priority + Risk
              ↓
Traffic Analysis
              ↓
Maintenance Bundling
              ↓
OR-Tools Optimization
              ↓
Optimized Block Plan
```

The system compares:

* blocks before/after
* block hours
* train conflicts
* maintenance coverage
* critical task completion

---

# Future Scope

* Real TMS integration
* Real SMMS integration
* Real TDMS integration
* Real COA integration
* Live train feeds
* Real-time traffic forecasting
* Nationwide railway network
* Advanced predictive maintenance
* Digital twin
* Mobile controller application

---

# Disclaimer

PlanRail is an academic/prototype decision-support system.

Its synthetic maintenance data and optimization results should not be interpreted as actual Indian Railways operational recommendations.
