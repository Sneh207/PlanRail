# PlanRail — Database Schema

## 1. users

```text
id
name
email
password_hash
role
created_at
```

Roles:

```text
CONTROLLER
MAINTENANCE
ADMIN
```

---

# 2. stations

```text
id
station_code
station_name
latitude
longitude
zone
division
```

---

# 3. railway_sections

```text
id
section_code
start_station_id
end_station_id
distance_km
geometry
traffic_level
risk_score
```

---

# 4. assets

```text
id
asset_code
section_id
department
asset_type
latitude
longitude
installation_date
condition_score
criticality
last_maintenance_date
next_due_date
```

Departments:

```text
ENGINEERING
OHE
SIGNALLING
```

---

# 5. maintenance_tasks

```text
id
task_code
asset_id
section_id
department
maintenance_type
defect_type
severity
criticality
detected_date
due_date
overdue_days
estimated_duration
crew_required
status
priority_score
risk_score
```

---

# 6. trains

```text
id
train_number
train_name
train_type
priority
```

---

# 7. train_movements

```text
id
train_id
section_id
station_id
scheduled_arrival
scheduled_departure
actual_arrival
actual_departure
delay_minutes
travel_date
```

---

# 8. block_windows

```text
id
section_id
date
start_time
end_time
duration_minutes
traffic_level
available
```

---

# 9. maintenance_compatibility

```text
id
task_type_a
task_type_b
compatible
reason
```

---

# 10. optimized_blocks

```text
id
section_id
date
start_time
end_time
duration_minutes
status
optimization_score
```

---

# 11. block_tasks

```text
id
block_id
maintenance_task_id
```

---

# 12. simulation_runs

```text
id
created_at
scenario_name
traffic_multiplier
cancelled_block_id
emergency_task
original_metrics
new_metrics
```

---

# Relationships

```text
Station
  ↓
Railway Section
  ↓
Assets
  ↓
Maintenance Tasks

Train
  ↓
Train Movements
  ↓
Railway Section

Maintenance Tasks
  ↓
Optimized Blocks
```
