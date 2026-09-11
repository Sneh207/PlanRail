# PlanRail — UI/UX Specification

## Design Goal

The interface should look like a professional railway operations dashboard.

Do not make it look like a generic AI website.

Use:

* clean dashboard
* dark/light neutral professional interface
* clear status indicators
* maps
* tables
* timelines
* charts

---

# Navigation

Sidebar:

```text
PlanRail

Dashboard
Railway Network
Maintenance
Block Planning
AI Insights
What-If Simulator
Analytics
Data Management
Settings
```

---

# Dashboard

Top:

```text
PlanRail
Delhi–Agra Corridor
Current Planning Period
```

KPI cards:

```text
Pending Maintenance
Critical Tasks
Available Windows
Planned Blocks
Block Hours
Coverage
```

Middle:

* Railway map
* Risk distribution
* Maintenance by department

Bottom:

* Current block plan
* AI recommendations

---

# Railway Network

Large map.

Colors/status:

```text
Normal
Maintenance
High Risk
Critical
```

Click section → side panel.

---

# Maintenance

Use searchable table.

Columns:

```text
Task
Department
Section
Severity
Priority
Risk
Due
Status
```

Click task → detail panel.

---

# Block Planning

Top button:

```text
GENERATE OPTIMAL PLAN
```

After generation:

```text
Before
After
Improvement
```

Timeline/Gantt:

```text
08  10  12  14  16  18

S01    ████████
       Track + OHE

S02             █████
                Signal
```

---

# AI Recommendation Card

```text
AI RECOMMENDATION

Section S01
10:00–12:00

Tasks:
Engineering M001
OHE M021

Priority: 92
Risk: High
Traffic: Low
Conflicts: 0

Why recommended?
✓ High priority maintenance
✓ Compatible tasks
✓ Low traffic window
✓ No critical train conflict

[VIEW DETAILS]
```

---

# What-If Simulator

Left side:

Scenario controls.

Right side:

Before vs After.

Example:

```text
BLOCKS
9 → 11

BLOCK HOURS
18 → 22

CONFLICTS
3 → 5

COVERAGE
94% → 91%
```

---

# UX Rules

1. Keep important information visible.
2. Avoid excessive animations.
3. Never hide the reason behind an AI recommendation.
4. Every destructive action requires confirmation.
5. Use consistent terminology.
6. Use tooltips for technical terms.
7. Mobile responsiveness is optional for prototype.
