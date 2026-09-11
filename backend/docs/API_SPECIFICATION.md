# PlanRail REST API Specification

**Version:** `v1`  
**Base URL:** `/api/v1`  
**Status:** Single Source of Truth for PlanRail Decision-Support System REST API  

---

## Standard Error Format

All error responses return a consistent error object wrapper:

```json
{
  "detail": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Maintenance request MR0001 was not found"
  }
}
```

### Standard Error Codes
- `RESOURCE_NOT_FOUND` (HTTP 404)
- `VALIDATION_ERROR` (HTTP 422)
- `BAD_REQUEST` (HTTP 400)
- `NOT_IMPLEMENTED` (HTTP 501)
- `INTERNAL_SERVER_ERROR` (HTTP 500)

---

## Standard Pagination Format

All list endpoints support pagination query parameters and return a unified container response.

### Query Parameters
- `page` (integer, default: 1, min: 1)
- `page_size` (integer, default: 20, min: 1, max: 100)

### Response Body Format
```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 150
}
```

---

## 1. Health

### GET `/api/v1/health`
**Purpose:** Basic application health check.  
**Authentication:** None.  

#### Response (200 OK)
```json
{
  "status": "ok"
}
```

---

### GET `/api/v1/health/db`
**Purpose:** Database connectivity & PostGIS status check.  
**Authentication:** None.  

#### Response (200 OK)
```json
{
  "status": "ok",
  "database": "connected",
  "postgis": true
}
```

---

## 2. Dashboard

### GET `/api/v1/dashboard`
**Purpose:** Summary metric card aggregation for the controller dashboard.  
**Authentication:** None (Mock Role).  

#### Response (200 OK)
```json
{
  "total_maintenance_requests": 150,
  "pending_requests": 120,
  "critical_high_requests": 45,
  "overdue_requests": 8,
  "available_maintenance_windows": 408,
  "total_trains": 24,
  "latest_optimization": {
    "run_id": "OPT-2026-09-01-001",
    "status": "COMPLETED",
    "created_at": "2026-09-01T10:00:00Z"
  }
}
```

---

## 3. Stations

### GET `/api/v1/stations`
**Purpose:** List all railway stations.  
**Query Parameters:**  
- `page` (int, default: 1)
- `page_size` (int, default: 20)
- `search` (string, optional - filter by name or code)

#### Response (200 OK)
```json
{
  "items": [
    {
      "station_id": "ST001",
      "station_code": "NDLS",
      "station_name": "New Delhi",
      "latitude": 28.64244,
      "longitude": 77.21833,
      "km_from_ndls": 0.0,
      "source_type": "PRIMARY"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 18
}
```

---

### GET `/api/v1/stations/{station_id}`
**Purpose:** Retrieve a single station by `station_id` or `station_code`.  

#### Response (200 OK)
```json
{
  "station_id": "ST001",
  "station_code": "NDLS",
  "station_name": "New Delhi",
  "latitude": 28.64244,
  "longitude": 77.21833,
  "km_from_ndls": 0.0,
  "source_type": "PRIMARY"
}
```

---

## 4. Railway Sections

### GET `/api/v1/sections`
**Purpose:** List railway line sections between stations.  
**Query Parameters:** `page`, `page_size`

#### Response (200 OK)
```json
{
  "items": [
    {
      "section_id": "SEC001",
      "section_code": "NDLS-NZM",
      "from_station_code": "NDLS",
      "to_station_code": "NZM",
      "from_station_name": "New Delhi",
      "to_station_name": "Hazrat Nizamuddin",
      "distance_km": 7.2,
      "track_configuration": "DOUBLE",
      "electrification": "ELECTRIFIED",
      "traffic_class": "HIGH_DENSITY",
      "geometry": null
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 17
}
```

---

### GET `/api/v1/sections/{section_id}`
**Purpose:** Retrieve a single section by `section_id` or `section_code`.  

---

## 5. Assets

### GET `/api/v1/assets`
**Purpose:** List railway track assets.  
**Query Parameters:**  
- `section_id` (string)
- `department` (string: TRACK, SIGNALING, TRD, MECHANICAL)
- `asset_type` (string)
- `criticality` (string: HIGH, MEDIUM, LOW)
- `page`, `page_size`

#### Response (200 OK)
```json
{
  "items": [
    {
      "asset_id": "AST0001",
      "section_id": "SEC001",
      "asset_type": "TRACK_SEGMENT",
      "department": "TRACK",
      "installation_year": 2018,
      "condition_score": 78.5,
      "criticality": "HIGH",
      "last_maintenance_date": "2026-06-15"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 85
}
```

---

### GET `/api/v1/assets/{asset_id}`
**Purpose:** Retrieve a single asset by `asset_id`.  

---

## 6. Maintenance Requests

### GET `/api/v1/maintenance`
**Purpose:** List maintenance requests.  
**Query Parameters:**  
- `status` (PENDING, APPROVED, SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED)
- `department` (TRACK, SIGNALING, TRD, MECHANICAL)
- `section_id` (string)
- `asset_id` (string)
- `severity` (CRITICAL, HIGH, MEDIUM, LOW)
- `page`, `page_size`

#### Response (200 OK)
```json
{
  "items": [
    {
      "request_id": "MR0001",
      "asset_id": "AST0001",
      "section_id": "SEC001",
      "department": "TRACK",
      "asset_type": "TRACK_SEGMENT",
      "maintenance_type": "RAIL_REPLACEMENT",
      "severity": "HIGH",
      "criticality_score": 85.0,
      "duration_hours": 3.5,
      "created_date": "2026-08-20",
      "due_date": "2026-09-05",
      "overdue_days": 0,
      "baseline_risk_score": 75.0,
      "status": "PENDING"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 150
}
```

---

### GET `/api/v1/maintenance/{request_id}`
**Purpose:** Retrieve a single maintenance request with maintenance history.  

---

## 7. Trains

### GET `/api/v1/trains`
**Purpose:** List trains traversing the corridor.  
**Query Parameters:** `page`, `page_size`, `train_type`

#### Response (200 OK)
```json
{
  "items": [
    {
      "train_number": "12002",
      "train_name": "Shatabdi Express",
      "train_type": "PREMIUM",
      "origin_code": "NDLS",
      "destination_code": "AGC",
      "service_pattern": "DAILY",
      "is_synthetic_schedule": false
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 24
}
```

---

### GET `/api/v1/trains/{train_number}`
**Purpose:** Retrieve details for a single train.  

---

### GET `/api/v1/trains/{train_number}/schedule`
**Purpose:** Retrieve station-by-station schedule entries for a train.  

#### Response (200 OK)
```json
[
  {
    "schedule_id": "SCH001",
    "train_number": "12002",
    "station_code": "NDLS",
    "station_name": "New Delhi",
    "arrival_time": null,
    "departure_time": "06:00:00",
    "day_number": 1,
    "sequence": 1
  }
]
```

---

## 8. Maintenance Windows

### GET `/api/v1/maintenance-windows`
**Purpose:** List available maintenance windows.  
**Query Parameters:**  
- `section_id`
- `hour` (0 to 23)
- `traffic_level` (LOW, MEDIUM, HIGH)
- `is_feasible` (boolean)
- `page`, `page_size`

#### Response (200 OK)
```json
{
  "items": [
    {
      "window_id": "MW0001",
      "section_id": "SEC001",
      "start_hour": 1,
      "start_time": "01:00:00",
      "end_time": "02:00:00",
      "expected_train_count": 2,
      "traffic_level": "LOW",
      "is_feasible": true,
      "window_reason": "Low traffic period"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 408
}
```

---

## 9. Traffic Windows

### GET `/api/v1/traffic-windows`
**Purpose:** List traffic density windows per section and hour.  
**Query Parameters:** `section_id`, `hour`, `traffic_level`, `page`, `page_size`

---

## 10. Optimization (Contract)

### POST `/api/v1/optimization/generate`
**Purpose:** Trigger OR-Tools maintenance block optimizer.  
**Status:** Contract Defined (Returns HTTP 501 Not Implemented if optimizer is unavailable).  

#### Request Body
```json
{
  "target_date": "2026-09-10",
  "selected_request_ids": ["MR0001", "MR0002"],
  "max_block_duration_hours": 4.0
}
```

#### Response (501 Not Implemented)
```json
{
  "detail": {
    "code": "NOT_IMPLEMENTED",
    "message": "Optimization engine is not yet connected."
  }
}
```

---

## 11. Blocks

### GET `/api/v1/blocks`
**Purpose:** Retrieve generated maintenance blocks.  

---

### GET `/api/v1/blocks/{block_id}`
**Purpose:** Retrieve block details and assigned tasks.  

---

## 12. AI Priority & Risk (Contract)

### POST `/api/v1/ai/predict`
**Purpose:** Predict request priority and risk category.  
**Status:** Deterministic fallback / HTTP 501 Not Implemented.  

#### Request Body
```json
{
  "request_id": "MR0001"
}
```

#### Response (200 OK - Fallback/Contract)
```json
{
  "request_id": "MR0001",
  "priority_score": 91,
  "risk_score": 78,
  "risk_category": "HIGH"
}
```

---

## 13. Simulation (Contract)

### POST `/api/v1/simulation/run`
**Purpose:** What-If simulator endpoint.  
**Status:** Returns HTTP 501 Not Implemented until solver integration.  
