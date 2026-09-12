from typing import Optional, List, Union, Literal
from datetime import date, time, datetime
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

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

class ActionRequiredItem(BaseModel):
    id: str
    type: str  # "CRITICAL_MAINTENANCE", "PENDING_BLOCK_DECISION", "UPCOMING_WINDOW"
    title: str
    section_id: str
    badge_text: str
    badge_tone: str  # "red", "amber", "blue", "green"
    risk_score: Optional[float] = None
    priority_score: Optional[float] = None
    action_target: str
    action_label: str
    secondary_target: Optional[str] = None
    secondary_label: Optional[str] = None

class DashboardResponse(BaseModel):
    total_maintenance_requests: int
    pending_requests: int
    critical_high_requests: int
    overdue_requests: int
    available_maintenance_windows: int
    total_trains: int
    total_freight_trains: Optional[int] = 36
    latest_optimization: Optional[OptimizationSummary] = None
    action_required: List[ActionRequiredItem] = []

class MaintenanceStatusUpdateRequest(BaseModel):
    status: str  # "PENDING", "ACCEPTED", "IN_PROGRESS", "COMPLETED", "CANCELLED"

class EmergencyMaintenanceCreateRequest(BaseModel):
    section_id: str
    asset_id: Optional[str] = None
    department: str = "Engineering"
    asset_type: Optional[str] = "Track / Permanent Way"
    maintenance_type: str = "Emergency Repair"
    severity: float = 5.0
    criticality_score: float = 5.0
    duration_hours: float = 2.0
    description: Optional[str] = None
    due_date: Optional[date] = None

class BlockStatusUpdateRequest(BaseModel):
    status: str  # "PROPOSED", "APPROVED", "MODIFIED", "REJECTED", "COMPLETED"

class AdminConfigResponse(BaseModel):
    max_block_duration_hours: float = 4.0
    emergency_priority_multiplier: float = 1.5
    critical_freight_multiplier: float = 1.5
    high_freight_multiplier: float = 1.2
    auto_approval_threshold: float = 80.0
    corridor_speed_limit_kmh: int = 160
    dispatch_mode: str = "AUTOMATIC_OPTIMIZATION"
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AdminConfigUpdateRequest(BaseModel):
    max_block_duration_hours: Optional[float] = None
    emergency_priority_multiplier: Optional[float] = None
    critical_freight_multiplier: Optional[float] = None
    high_freight_multiplier: Optional[float] = None
    auto_approval_threshold: Optional[float] = None
    corridor_speed_limit_kmh: Optional[int] = None
    dispatch_mode: Optional[str] = None


# Optimization / Contract Schemas
class OptimizationGenerateRequest(BaseModel):
    target_date: date
    selected_request_ids: Optional[List[str]] = None
    max_block_duration_hours: Optional[float] = 4.0

class FeatureContribution(BaseModel):
    feature: str
    feature_name: str
    feature_value: float
    contribution: float
    impact: str  # "INCREASES_RISK" | "DECREASES_RISK" | "NEUTRAL"
    display_text: str

class AIPredictRequest(BaseModel):
    request_id: str

class AIPredictResponse(BaseModel):
    request_id: str
    risk_probability: Optional[float] = None
    risk_score: float
    risk_category: str
    traffic_impact_score: Optional[float] = None
    traffic_impact_category: Optional[str] = None
    priority_score: float
    priority_category: Optional[str] = None
    priority_components: Optional[dict[str, float]] = None
    risk_contributing_factors: Optional[List[str]] = None
    feature_contributions: Optional[List[FeatureContribution]] = None
    shap_values: Optional[dict[str, float]] = None
    explanation: Optional[str] = None
    model_status: Optional[str] = "XGBOOST_TRAINED_MODEL"

    model_config = ConfigDict(from_attributes=True)

class AIHighAttentionTask(BaseModel):
    request_id: str
    asset_id: str
    section_id: str
    department: str
    asset_type: str
    priority_score: float
    priority_category: str
    risk_score: float
    risk_category: str
    traffic_impact_score: float
    traffic_impact_category: str
    overdue_days: int
    duration_hours: float
    top_drivers: List[str] = []

class AIInsightsResponse(BaseModel):
    total_requests_analyzed: int
    risk_distribution: dict[str, int]
    priority_distribution: dict[str, int]
    department_distribution: dict[str, int]
    high_attention_tasks: List[AIHighAttentionTask] = []
    corridor_ai_recommendation: str
    model_status: str

# Blocks Schemas
class BlockTaskResponse(BaseModel):
    block_task_id: str
    block_id: str
    request_id: str
    sequence: int

    model_config = ConfigDict(from_attributes=True)

    @field_validator("block_task_id", mode="before")
    @classmethod
    def coerce_task_id(cls, v):
        return f"BT_{v}" if isinstance(v, int) else str(v)

    @field_validator("block_id", "request_id", mode="before")
    @classmethod
    def coerce_str_ids(cls, v):
        return str(v)


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

    @field_validator("block_id", "run_id", "section_id", mode="before")
    @classmethod
    def coerce_block_strings(cls, v):
        return str(v) if v is not None else ""


class OptimizationGenerateResponse(BaseModel):
    run_id: str
    status: str
    target_date: date
    total_requests_considered: int
    scheduled_tasks_count: int
    unscheduled_tasks_count: int
    blocks_count: int
    solve_time_ms: float
    blocks: List[OptimizedBlockResponse] = []

    model_config = ConfigDict(from_attributes=True)


# What-If Simulation Schemas
class SimulationRunRequest(BaseModel):
    scenario_type: Literal[
        "TRAFFIC_PLUS_20",
        "EMERGENCY_MAINTENANCE",
        "REMOVE_MAINTENANCE_WINDOW",
    ]
    target_date: date
    request_id: Optional[str] = None
    window_id: Optional[str] = None

    @model_validator(mode="after")
    def validate_scenario_requirements(self):
        if self.scenario_type == "EMERGENCY_MAINTENANCE":
            if not self.request_id or not str(self.request_id).strip():
                raise ValueError("request_id is required for EMERGENCY_MAINTENANCE scenario.")
        elif self.scenario_type == "REMOVE_MAINTENANCE_WINDOW":
            if not self.window_id or not str(self.window_id).strip():
                raise ValueError("window_id is required for REMOVE_MAINTENANCE_WINDOW scenario.")
        return self


class SimulationMetrics(BaseModel):
    scheduled_tasks: int
    unscheduled_tasks: int
    blocks: int
    total_scheduled_duration_hours: float
    objective_score: float
    total_expected_train_exposure: int


class SimulationDifference(BaseModel):
    scheduled_tasks_delta: int
    blocks_delta: int
    scheduled_duration_delta_hours: float
    objective_delta: float
    train_exposure_delta: int


class SimulationRunResponse(BaseModel):
    simulation_id: str
    scenario_type: str
    target_date: date

    baseline: SimulationMetrics
    scenario: SimulationMetrics
    difference: SimulationDifference

    newly_scheduled_tasks: List[str]
    unscheduled_tasks_after_simulation: List[str]
    moved_tasks: List[str]

    baseline_blocks: List[OptimizedBlockResponse]
    scenario_blocks: List[OptimizedBlockResponse]

    explanation: str

    model_config = ConfigDict(from_attributes=True)


# Freight Train Movement Schema (Simulated Planning Dataset)
class FreightTrainMovementResponse(BaseModel):
    freight_train_id: str
    movement_date: date
    origin_station_code: str
    destination_station_code: str
    commodity: str
    load_tonnes: float
    planned_entry_time: str
    planned_exit_time: str
    traffic_priority: str
    corridor: str = "Delhi-Agra"
    data_status: str = "SIMULATED_BY_PLANRAIL"
    source_basis: str
    planning_use: str
    simulation_note: str
    reference_1: Optional[str] = None
    reference_1_url: Optional[str] = None
    reference_2: Optional[str] = None
    reference_2_url: Optional[str] = None
    reference_3: Optional[str] = None
    reference_3_url: Optional[str] = None
    reference_4: Optional[str] = None
    reference_4_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
