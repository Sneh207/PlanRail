from typing import Optional, List, Union
from datetime import date, time, datetime
from pydantic import BaseModel, ConfigDict

# Station Schemas
class StationResponse(BaseModel):
    station_id: str
    station_code: str
    station_name: str
    latitude: float
    longitude: float
    km_from_ndls: float
    source_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Section Schemas
class SectionResponse(BaseModel):
    section_id: str
    section_code: str
    from_station_code: str
    to_station_code: str
    from_station_name: Optional[str] = None
    to_station_name: Optional[str] = None
    distance_km: float
    track_configuration: str
    electrification: str
    traffic_class: str
    geometry: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Asset Schemas
class AssetResponse(BaseModel):
    asset_id: str
    section_id: str
    asset_type: str
    department: str
    installation_year: Optional[int] = None
    condition_score: Optional[float] = None
    criticality: str
    last_maintenance_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)

# History Schema for Nested Detail
class MaintenanceHistoryResponse(BaseModel):
    history_id: str
    asset_id: str
    section_id: str
    event_date: datetime
    event_type: str
    severity: Union[str, float]
    downtime_hours: float

    model_config = ConfigDict(from_attributes=True)

# Maintenance Request Schemas
class MaintenanceRequestResponse(BaseModel):
    request_id: str
    asset_id: str
    section_id: str
    department: str
    asset_type: str
    maintenance_type: str
    severity: Union[str, float]
    criticality_score: Optional[float] = None
    duration_hours: float
    created_date: Optional[date] = None
    due_date: date
    overdue_days: Optional[int] = None
    baseline_risk_score: Optional[float] = None
    status: str

    model_config = ConfigDict(from_attributes=True)

class MaintenanceRequestDetailResponse(MaintenanceRequestResponse):
    history: List[MaintenanceHistoryResponse] = []

# Train Schemas
class TrainResponse(BaseModel):
    train_number: str
    train_name: str
    train_type: str
    origin_code: str
    destination_code: str
    service_pattern: str
    is_synthetic_schedule: bool

    model_config = ConfigDict(from_attributes=True)

class TrainScheduleResponse(BaseModel):
    schedule_id: str
    train_number: str
    station_code: str
    station_name: Optional[str] = None
    arrival_time: Optional[time] = None
    departure_time: Optional[time] = None
    day_number: int
    sequence: int

    model_config = ConfigDict(from_attributes=True)

# Maintenance & Traffic Windows
class MaintenanceWindowResponse(BaseModel):
    window_id: str
    section_id: str
    start_hour: int
    start_time: time
    end_time: time
    expected_train_count: int
    traffic_level: str
    is_feasible: bool
    window_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class TrafficWindowResponse(BaseModel):
    traffic_window_id: str
    section_id: str
    hour: int
    train_count: int
    traffic_level: str

    model_config = ConfigDict(from_attributes=True)

# Dashboard Schema
class OptimizationSummary(BaseModel):
    run_id: str
    status: str
    created_at: datetime

class DashboardResponse(BaseModel):
    total_maintenance_requests: int
    pending_requests: int
    critical_high_requests: int
    overdue_requests: int
    available_maintenance_windows: int
    total_trains: int
    latest_optimization: Optional[OptimizationSummary] = None

# Optimization / Contract Schemas
class OptimizationGenerateRequest(BaseModel):
    target_date: date
    selected_request_ids: Optional[List[str]] = None
    max_block_duration_hours: Optional[float] = 4.0

class AIPredictRequest(BaseModel):
    request_id: str

class AIPredictResponse(BaseModel):
    request_id: str
    priority_score: float
    risk_score: float
    risk_category: str

class SimulationRunRequest(BaseModel):
    selected_request_ids: List[str]
    blocked_window_ids: Optional[List[str]] = None

# Blocks Schemas
class BlockTaskResponse(BaseModel):
    block_task_id: str
    block_id: str
    request_id: str
    sequence: int

    model_config = ConfigDict(from_attributes=True)

class OptimizedBlockResponse(BaseModel):
    block_id: str
    run_id: str
    section_id: str
    start_time: datetime
    end_time: datetime
    duration_hours: float
    status: str
    tasks: List[BlockTaskResponse] = []

    model_config = ConfigDict(from_attributes=True)
