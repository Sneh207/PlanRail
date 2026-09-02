# PlanRail Delhi–Agra Prototype Dataset

## What this dataset is
A clean, relational, SIH-ready prototype dataset for the PlanRail software.
It is designed for React + FastAPI + PostgreSQL/PostGIS + Python + OR-Tools.

## Data status
REAL/REFERENCE:
- Station names and route order are based on published Delhi–Agra railway route references.
- Coordinates are approximate prototype coordinates for mapping.

SYNTHETIC / DOMAIN-CALIBRATED:
- train timetable rows
- assets
- maintenance requests
- maintenance history
- crew availability
- compatibility rules
- traffic windows
- maintenance windows
- AI features

Important: this is NOT operational railway data and must not be used for real train operations.

## Start here (MVP)
Load these six files first:
1. stations.csv
2. railway_sections.csv
3. trains.csv
4. train_schedules.csv
5. assets.csv
6. maintenance_requests.csv

Then add:
7. maintenance_history.csv
8. crew_availability.csv
9. task_compatibility.csv
10. traffic_windows.csv
11. maintenance_windows.csv

`ai_training_features.csv` is already feature-engineered for the prototype ML layer.

## How the software uses the data

### Dashboard / Map
stations.csv -> Leaflet station markers
railway_sections.csv -> corridor sections/lines
assets.csv -> asset markers/details

### Train / Traffic module
trains.csv + train_schedules.csv
-> show trains and compute how many trains affect each section/hour.

### Maintenance module
maintenance_requests.csv + assets.csv
-> show pending jobs, severity, due date, duration and location.

### AI module
maintenance_requests + assets + maintenance_history
-> build risk/priority features.
For the first MVP, `ai_training_features.csv` can be used directly to demonstrate the priority model.
Do not call its priority_score "real historical ground truth"; it is a prototype baseline score.

### Optimization module
maintenance_requests + maintenance_windows + traffic_windows + task_compatibility + crew_availability
-> OR-Tools candidate schedule.
Core constraints:
- task must fit in a window
- avoid high-traffic windows unless allowed
- respect crew availability
- respect section/location
- compatible tasks may be bundled
- avoid overlapping incompatible work

### What-if simulator
Copy the selected plan to a scenario and modify one or more inputs:
- traffic +20%
- remove a maintenance window
- add emergency maintenance
- reduce available windows
Then rerun OR-Tools and compare KPIs.

## Primary joins
maintenance_requests.asset_id = assets.asset_id
maintenance_requests.section_id = railway_sections.section_id
train_schedules.train_number = trains.train_number
train_schedules.station_code = stations.station_code
assets.section_id = railway_sections.section_id
maintenance_history.asset_id = assets.asset_id
traffic_windows.section_id = railway_sections.section_id
maintenance_windows.section_id = railway_sections.section_id

## Suggested database tables
stations, railway_sections, trains, train_schedules, assets,
maintenance_requests, maintenance_history, crew_availability,
task_compatibility, traffic_windows, maintenance_windows.

## KPIs
number_of_blocks
total_block_hours
train_conflicts
critical_tasks_completed
maintenance_coverage
asset_availability
bundled_task_count
