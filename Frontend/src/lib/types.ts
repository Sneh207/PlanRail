export interface PaginatedResponse<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
}

export interface StationResponse {
  station_id: string;
  station_code: string;
  station_name: string;
  latitude: number;
  longitude: number;
  km_from_ndls: number | null;
  source_type?: string | null;
}

export interface SectionResponse {
  section_id: string;
  section_code: string;
  from_station_code: string;
  to_station_code: string;
  from_station_name?: string | null;
  to_station_name?: string | null;
  distance_km: number;
  track_configuration: string;
  electrification: string;
  traffic_class: string;
  geometry?: string | null;
}

export interface AssetResponse {
  asset_id: string;
  section_id: string;
  asset_type: string;
  department: string;
  installation_year?: number | null;
  condition_score?: number | null;
  criticality: string;
  last_maintenance_date?: string | null;
}

export interface MaintenanceHistoryResponse {
  history_id: string;
  asset_id: string;
  section_id: string;
  event_date: string;
  event_type: string;
  severity: number | string;
  downtime_hours: number;
}

export interface MaintenanceRequestResponse {
  request_id: string;
  asset_id: string;
  section_id: string;
  department: string;
  asset_type: string;
  maintenance_type: string;
  severity: number | string;
  criticality_score?: number | null;
  duration_hours: number;
  created_date?: string | null;
  due_date: string;
  overdue_days?: number | null;
  baseline_risk_score?: number | null;
  status: string;
}

export interface MaintenanceRequestDetailResponse extends MaintenanceRequestResponse {
  history: MaintenanceHistoryResponse[];
}

export interface TrainResponse {
  train_number: string;
  train_name: string;
  train_type: string;
  origin_code: string;
  destination_code: string;
  service_pattern: string;
  is_synthetic_schedule: boolean;
}

export interface TrainScheduleResponse {
  schedule_id: string;
  train_number: string;
  station_code: string;
  station_name?: string | null;
  arrival_time?: string | null;
  departure_time?: string | null;
  day_number: number;
  sequence: number;
}

export interface MaintenanceWindowResponse {
  window_id: string;
  section_id: string;
  start_hour: number;
  start_time: string;
  end_time: string;
  expected_train_count: number;
  traffic_level: string;
  is_feasible: boolean;
  window_reason?: string | null;
}


export interface TrafficWindowResponse {
  traffic_window_id: string;
  section_id: string;
  hour: number;
  train_count: number;
  traffic_level: string;
}

export interface OptimizationSummary {
  run_id: string;
  status: string;
  created_at: string;
}

export interface DashboardResponse {
  total_maintenance_requests: number;
  pending_requests: number;
  critical_high_requests: number;
  overdue_requests: number;
  available_maintenance_windows: number;
  total_trains: number;
  latest_optimization?: OptimizationSummary | null;
}

export interface BlockTaskResponse {
  block_task_id: string;
  block_id: string;
  request_id: string;
  sequence: number;
}

export interface OptimizedBlockResponse {
  block_id: string;
  run_id: string;
  section_id: string;
  start_time: string;
  end_time: string;
  duration_hours: number;
  status: string;
  tasks: BlockTaskResponse[];
}

export interface OptimizationGenerateRequest {
  target_date: string;
  selected_request_ids?: string[] | null;
  max_block_duration_hours?: number;
}

export interface OptimizationGenerateResponse {
  run_id: string;
  status: string;
  target_date: string;
  total_requests_considered: number;
  scheduled_tasks_count: number;
  unscheduled_tasks_count: number;
  blocks_count: number;
  solve_time_ms: number;
  blocks: OptimizedBlockResponse[];
}

export interface AIPredictRequest {
  request_id: string;
}

export interface AIPredictResponse {
  request_id: string;
  risk_probability?: number | null;
  risk_score: number;
  risk_category: string;
  traffic_impact_score?: number | null;
  traffic_impact_category?: string | null;
  priority_score: number;
  priority_category?: string | null;
  priority_components?: {
    severity: number;
    criticality: number;
    overdue: number;
    risk: number;
    traffic_impact: number;
  } | null;
  risk_contributing_factors?: string[] | null;
  explanation?: string | null;
  model_status?: string | null;
}

export interface AIHighAttentionTask {
  request_id: string;
  asset_id: string;
  section_id: string;
  department: string;
  asset_type: string;
  priority_score: number;
  priority_category: string;
  risk_score: number;
  risk_category: string;
  traffic_impact_score: number;
  traffic_impact_category: string;
  overdue_days: number;
  duration_hours: number;
  top_drivers: string[];
}

export interface AIInsightsResponse {
  total_requests_analyzed: number;
  risk_distribution: Record<string, number>;
  priority_distribution: Record<string, number>;
  department_distribution: Record<string, number>;
  high_attention_tasks: AIHighAttentionTask[];
  corridor_ai_recommendation: string;
  model_status: string;
}

export interface SimulationMetrics {
  scheduled_tasks: number;
  unscheduled_tasks: number;
  blocks: number;
  total_scheduled_duration_hours: number;
  objective_score: number;
  total_expected_train_exposure: number;
}

export interface SimulationDifference {
  scheduled_tasks_delta: number;
  blocks_delta: number;
  scheduled_duration_delta_hours: number;
  objective_delta: number;
  train_exposure_delta: number;
}

export interface SimulationRunRequest {
  scenario_type: "TRAFFIC_PLUS_20" | "EMERGENCY_MAINTENANCE" | "REMOVE_MAINTENANCE_WINDOW";
  target_date: string;
  request_id?: string | null;
  window_id?: string | null;
}

export interface SimulationRunResponse {
  simulation_id: string;
  scenario_type: string;
  target_date: string;
  baseline: SimulationMetrics;
  scenario: SimulationMetrics;
  difference: SimulationDifference;
  newly_scheduled_tasks: string[];
  unscheduled_tasks_after_simulation: string[];
  moved_tasks: string[];
  baseline_blocks: OptimizedBlockResponse[];
  scenario_blocks: OptimizedBlockResponse[];
  explanation: string;
}

export interface FreightTrainMovementResponse {
  freight_train_id: string;
  movement_date: string;
  origin_station_code: string;
  destination_station_code: string;
  commodity: string;
  load_tonnes: number;
  planned_entry_time: string;
  planned_exit_time: string;
  traffic_priority: string;
  corridor: string;
  data_status: string;
  source_basis: string;
  planning_use: string;
  simulation_note: string;
  reference_1?: string | null;
  reference_1_url?: string | null;
  reference_2?: string | null;
  reference_2_url?: string | null;
  reference_3?: string | null;
  reference_3_url?: string | null;
  reference_4?: string | null;
  reference_4_url?: string | null;
}

