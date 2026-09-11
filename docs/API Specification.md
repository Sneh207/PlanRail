# PlanRail — API Specification

Base URL:

```text
/api/v1
```

---

## Dashboard

### GET /dashboard/summary

Returns:

```json
{
  "total_assets": 1250,
  "pending_tasks": 126,
  "critical_tasks": 18,
  "planned_blocks": 9,
  "block_hours": 18,
  "maintenance_coverage": 94
}
```

---

## Stations

### GET /stations

### GET /stations/{id}

---

## Sections

### GET /sections

### GET /sections/{id}

---

## Assets

### GET /assets

Parameters:

```text
section_id
department
risk
```

---

## Maintenance

### GET /maintenance

Parameters:

```text
section_id
department
severity
status
```

### GET /maintenance/{id}

---

## AI Priority

### POST /ai/priority

Input:

```json
{
  "task_ids": ["M001", "M002"]
}
```

Output:

```json
{
  "tasks": [
    {
      "task_id": "M001",
      "priority": 91,
      "risk": 78
    }
  ]
}
```

---

## Train Data

### GET /trains

### GET /train-movements

Parameters:

```text
date
section_id
```

---

## Optimization

### POST /optimization/generate

Input:

```json
{
  "date": "2026-09-01",
  "section_ids": ["S01", "S02"],
  "objective": "MINIMIZE_DISRUPTION"
}
```

Output:

```json
{
  "blocks": [],
  "metrics": {
    "blocks": 9,
    "block_hours": 18,
    "train_conflicts": 3,
    "maintenance_coverage": 94
  }
}
```

---

## Block Details

### GET /blocks

### GET /blocks/{id}

---

## What-If Simulation

### POST /simulation/run

Input:

```json
{
  "traffic_multiplier": 1.2,
  "cancelled_block_id": null,
  "emergency_task_id": null
}
```

Output:

```json
{
  "original": {},
  "simulated": {},
  "difference": {}
}
```

---

## Approval

### POST /blocks/{id}/approve

### POST /blocks/{id}/reject

### POST /blocks/{id}/modify

---

## Data Upload

### POST /data/upload

Accept CSV.

Allowed:

```text
trains.csv
stations.csv
sections.csv
assets.csv
maintenance_tasks.csv
block_windows.csv
```

---

# API Rules

1. Use Pydantic models.
2. Validate every request.
3. Return consistent errors.
4. Never expose database credentials.
5. AI/optimization logic must remain in services.
6. Routes should remain thin.
