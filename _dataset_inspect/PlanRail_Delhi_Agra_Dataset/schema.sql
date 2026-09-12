-- PlanRail PostgreSQL schema (load CSVs after creating tables)
-- Use CSV column names as-is. Foreign keys can be enabled after initial import.

CREATE TABLE stations (
 station_id TEXT PRIMARY KEY, station_code TEXT UNIQUE NOT NULL, station_name TEXT NOT NULL,
 latitude DOUBLE PRECISION, longitude DOUBLE PRECISION, km_from_ndls NUMERIC,
 source_type TEXT, source_note TEXT
);
CREATE TABLE railway_sections (
 section_id TEXT PRIMARY KEY, from_station_code TEXT, to_station_code TEXT,
 from_station_name TEXT, to_station_name TEXT, distance_km NUMERIC,
 track_configuration TEXT, electrification TEXT, traffic_class TEXT
);
CREATE TABLE trains (
 train_number TEXT PRIMARY KEY, train_name TEXT, train_type TEXT,
 origin_code TEXT, destination_code TEXT, service_pattern TEXT, is_synthetic_schedule BOOLEAN
);
CREATE TABLE train_schedules (
 schedule_id TEXT PRIMARY KEY, train_number TEXT, station_code TEXT, station_name TEXT,
 sequence INT, arrival_time TEXT, departure_time TEXT, day INT, km_from_origin NUMERIC
);
CREATE TABLE assets (
 asset_id TEXT PRIMARY KEY, section_id TEXT, asset_type TEXT, department TEXT,
 installation_year INT, condition_score NUMERIC, criticality TEXT, last_maintenance_date DATE
);
CREATE TABLE maintenance_requests (
 request_id TEXT PRIMARY KEY, asset_id TEXT, section_id TEXT, department TEXT,
 asset_type TEXT, maintenance_type TEXT, severity INT, criticality_score INT,
 duration_hours NUMERIC, created_date DATE, due_date DATE, overdue_days INT,
 baseline_risk_score NUMERIC, status TEXT
);
CREATE TABLE maintenance_history (
 history_id TEXT PRIMARY KEY, asset_id TEXT, section_id TEXT, event_date DATE,
 event_type TEXT, severity INT, downtime_hours NUMERIC
);
CREATE TABLE crew_availability (
 crew_id TEXT PRIMARY KEY, crew_name TEXT, department TEXT,
 available_from_hour INT, available_to_hour INT, team_size INT
);
CREATE TABLE task_compatibility (
 department_a TEXT, department_b TEXT, compatibility TEXT,
 PRIMARY KEY(department_a, department_b)
);
CREATE TABLE traffic_windows (
 traffic_window_id TEXT PRIMARY KEY, section_id TEXT, hour INT,
 train_count INT, traffic_level TEXT
);
CREATE TABLE maintenance_windows (
 window_id TEXT PRIMARY KEY, section_id TEXT, start_hour INT,
 start_time TEXT, end_time TEXT, expected_train_count INT,
 traffic_level TEXT, is_feasible BOOLEAN, window_reason TEXT
);
CREATE TABLE freight_train_movements (
 freight_train_id TEXT PRIMARY KEY, movement_date DATE NOT NULL,
 origin_station_code TEXT NOT NULL, destination_station_code TEXT NOT NULL,
 commodity TEXT NOT NULL, load_tonnes DOUBLE PRECISION NOT NULL,
 planned_entry_time TEXT NOT NULL, planned_exit_time TEXT NOT NULL,
 traffic_priority TEXT NOT NULL, corridor TEXT NOT NULL DEFAULT 'Delhi-Agra',
 data_status TEXT NOT NULL DEFAULT 'SIMULATED_BY_PLANRAIL',
 source_basis TEXT NOT NULL, planning_use TEXT NOT NULL, simulation_note TEXT NOT NULL,
 reference_1 TEXT, reference_1_url TEXT, reference_2 TEXT, reference_2_url TEXT,
 reference_3 TEXT, reference_3_url TEXT, reference_4 TEXT, reference_4_url TEXT
);

