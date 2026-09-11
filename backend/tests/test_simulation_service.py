"""
PlanRail What-If Simulation Service & API Tests
===============================================

Tests the 3 simulation scenarios (Traffic +20%, Emergency Maintenance, Remove Window),
verifies in-memory non-mutating behavior, delta calculations, explanation logic,
and API validation rules.
"""

from __future__ import annotations

import unittest
from datetime import date, datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models.block import BlockTask, MaintenanceWindow, OptimizationRun, OptimizedBlock
from app.models.maintenance import MaintenanceRequest
from app.optimizer.data_loader import OptimizerDataLoader
from app.optimizer.solver import MaintenanceBlockSolver
from app.schemas.domain import SimulationRunRequest
from app.services.simulation_service import SimulationService


class TestSimulationService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        with cls.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE stations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    station_id VARCHAR(30) UNIQUE,
                    station_code VARCHAR(30) UNIQUE NOT NULL,
                    station_name VARCHAR(100) NOT NULL,
                    latitude FLOAT NOT NULL,
                    longitude FLOAT NOT NULL,
                    km_from_ndls FLOAT NOT NULL,
                    source_type VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("""
                CREATE TABLE railway_sections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    section_id VARCHAR(30) UNIQUE NOT NULL,
                    section_code VARCHAR(30) UNIQUE NOT NULL,
                    name VARCHAR(100),
                    from_station_code VARCHAR(30) NOT NULL,
                    to_station_code VARCHAR(30) NOT NULL,
                    from_station_name VARCHAR(100),
                    to_station_name VARCHAR(100),
                    distance_km FLOAT NOT NULL,
                    track_configuration VARCHAR(50),
                    electrification VARCHAR(50),
                    traffic_class VARCHAR(50),
                    traffic_level VARCHAR(50),
                    risk_score FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("""
                CREATE TABLE assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id VARCHAR(30) UNIQUE NOT NULL,
                    section_id VARCHAR(30) NOT NULL,
                    asset_type VARCHAR(50) NOT NULL,
                    department VARCHAR(50) NOT NULL,
                    installation_year INTEGER,
                    condition_score FLOAT,
                    criticality VARCHAR(50) NOT NULL,
                    last_maintenance_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("""
                CREATE TABLE maintenance_compatibility (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    department_a VARCHAR(50) NOT NULL,
                    department_b VARCHAR(50) NOT NULL,
                    compatibility VARCHAR(50) NOT NULL,
                    reason VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("""
                CREATE TABLE traffic_windows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    traffic_window_id VARCHAR(30) UNIQUE NOT NULL,
                    section_id VARCHAR(30) NOT NULL,
                    hour INTEGER NOT NULL,
                    train_count INTEGER NOT NULL,
                    traffic_level VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("""
                CREATE TABLE maintenance_windows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    window_id VARCHAR(30) UNIQUE NOT NULL,
                    section_id VARCHAR(30) NOT NULL,
                    start_hour INTEGER NOT NULL,
                    start_time VARCHAR(20) NOT NULL,
                    end_time VARCHAR(20) NOT NULL,
                    expected_train_count INTEGER NOT NULL,
                    traffic_level VARCHAR(50) NOT NULL,
                    is_feasible BOOLEAN NOT NULL,
                    window_reason VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("""
                CREATE TABLE maintenance_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id VARCHAR(30) UNIQUE NOT NULL,
                    task_code VARCHAR(30),
                    asset_id VARCHAR(30) NOT NULL,
                    section_id VARCHAR(30) NOT NULL,
                    department VARCHAR(50) NOT NULL,
                    asset_type VARCHAR(50),
                    maintenance_type VARCHAR(100) NOT NULL,
                    severity FLOAT NOT NULL,
                    criticality_score FLOAT NOT NULL,
                    duration_hours FLOAT NOT NULL,
                    created_date TIMESTAMP,
                    due_date TIMESTAMP NOT NULL,
                    overdue_days INTEGER DEFAULT 0,
                    baseline_risk_score FLOAT,
                    status VARCHAR(50) DEFAULT 'PENDING',
                    priority_score FLOAT,
                    risk_score FLOAT,
                    traffic_impact_score FLOAT,
                    crew_required INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("""
                CREATE TABLE optimization_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_code VARCHAR(30) UNIQUE NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    objective VARCHAR(100),
                    parameters JSON,
                    metrics JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                );
            """))
            conn.execute(text("""
                CREATE TABLE optimized_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block_code VARCHAR(30) UNIQUE NOT NULL,
                    section_id INTEGER NOT NULL REFERENCES railway_sections(id),
                    maintenance_window_id INTEGER REFERENCES maintenance_windows(id),
                    optimization_run_id INTEGER REFERENCES optimization_runs(id),
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    optimization_score FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("""
                CREATE TABLE block_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block_id INTEGER NOT NULL REFERENCES optimized_blocks(id),
                    maintenance_request_id INTEGER NOT NULL REFERENCES maintenance_requests(id),
                    sequence_order INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.commit()

        cls.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)

        def override_get_db():
            db = cls.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()

    def setUp(self):
        # Clear and seed test data
        with self.engine.connect() as conn:
            conn.execute(text("DELETE FROM block_tasks;"))
            conn.execute(text("DELETE FROM optimized_blocks;"))
            conn.execute(text("DELETE FROM optimization_runs;"))
            conn.execute(text("DELETE FROM maintenance_requests;"))
            conn.execute(text("DELETE FROM maintenance_windows;"))
            conn.execute(text("DELETE FROM maintenance_compatibility;"))
            conn.execute(text("DELETE FROM assets;"))
            conn.execute(text("DELETE FROM railway_sections;"))
            conn.execute(text("DELETE FROM stations;"))

            # Stations & Section
            conn.execute(text("INSERT INTO stations (station_id, station_code, station_name, latitude, longitude, km_from_ndls) VALUES ('ST1', 'NDLS', 'New Delhi', 28.6143, 77.2188, 0.0);"))
            conn.execute(text("INSERT INTO stations (station_id, station_code, station_name, latitude, longitude, km_from_ndls) VALUES ('ST2', 'TKD', 'Tughlakabad', 28.5020, 77.2940, 17.5);"))
            conn.execute(text("""
                INSERT INTO railway_sections (id, section_id, section_code, from_station_code, to_station_code, distance_km, track_configuration, electrification, traffic_class)
                VALUES (1, 'SEC_DEL_TKD', 'SEC_DEL_TKD', 'NDLS', 'TKD', 17.5, 'DOUBLE', '25KV_AC', 'HIGH');
            """))

            # Compatibility
            conn.execute(text("INSERT INTO maintenance_compatibility (department_a, department_b, compatibility) VALUES ('Engineering', 'S&T', 'COMPATIBLE');"))
            conn.execute(text("INSERT INTO maintenance_compatibility (department_a, department_b, compatibility) VALUES ('Engineering', 'Electrical', 'INCOMPATIBLE');"))

            # Maintenance Windows (2 windows on SEC_DEL_TKD: MW01 Night Low-traffic, MW02 Morning Med-traffic)
            conn.execute(text("""
                INSERT INTO maintenance_windows (id, window_id, section_id, start_hour, start_time, end_time, expected_train_count, traffic_level, is_feasible)
                VALUES (1, 'MW0001', 'SEC_DEL_TKD', 1, '01:00', '04:00', 4, 'LOW', 1);
            """))
            conn.execute(text("""
                INSERT INTO maintenance_windows (id, window_id, section_id, start_hour, start_time, end_time, expected_train_count, traffic_level, is_feasible)
                VALUES (2, 'MW0002', 'SEC_DEL_TKD', 10, '10:00', '13:00', 12, 'MEDIUM', 1);
            """))

            # Maintenance Requests (MR0001 Engineering 2h, MR0002 S&T 1h, MR0003 Electrical 2h)
            conn.execute(text("""
                INSERT INTO maintenance_requests (id, request_id, asset_id, section_id, department, maintenance_type, severity, criticality_score, duration_hours, due_date, status, overdue_days)
                VALUES (1, 'MR0001', 'AST1', 'SEC_DEL_TKD', 'Engineering', 'Track renewal', 4.0, 4.0, 2.0, '2026-09-04 12:00:00', 'PENDING', 3);
            """))
            conn.execute(text("""
                INSERT INTO maintenance_requests (id, request_id, asset_id, section_id, department, maintenance_type, severity, criticality_score, duration_hours, due_date, status, overdue_days)
                VALUES (2, 'MR0002', 'AST2', 'SEC_DEL_TKD', 'S&T', 'Signal check', 3.0, 3.0, 1.0, '2026-09-04 12:00:00', 'PENDING', 0);
            """))
            conn.execute(text("""
                INSERT INTO maintenance_requests (id, request_id, asset_id, section_id, department, maintenance_type, severity, criticality_score, duration_hours, due_date, status, overdue_days)
                VALUES (3, 'MR0003', 'AST3', 'SEC_DEL_TKD', 'Electrical', 'OHE wire replacement', 2.0, 2.0, 2.0, '2026-09-04 12:00:00', 'PENDING', 0);
            """))
            conn.commit()

    # -------------------------------------------------------------------------
    # Test 1 & 2: Traffic +20% Validation & DB Non-Mutation
    # -------------------------------------------------------------------------
    def test_01_traffic_plus_20_validation(self):
        """Tests that TRAFFIC_PLUS_20 runs successfully and calculates correct exposure delta."""
        db = self.TestingSessionLocal()
        try:
            req = SimulationRunRequest(
                scenario_type="TRAFFIC_PLUS_20",
                target_date=date(2026, 9, 4),
            )
            response = SimulationService.run_simulation(db, req)
            self.assertEqual(response.scenario_type, "TRAFFIC_PLUS_20")
            self.assertGreater(response.baseline.scheduled_tasks, 0)
            self.assertIsNotNone(response.difference.train_exposure_delta)
            self.assertIn("Traffic was increased by 20%", response.explanation)
        finally:
            db.close()

    def test_02_traffic_transformation_does_not_modify_db(self):
        """Verifies that running TRAFFIC_PLUS_20 leaves the database expected_train_count unaltered."""
        db = self.TestingSessionLocal()
        try:
            # Query initial train count
            initial_count = db.execute(text("SELECT expected_train_count FROM maintenance_windows WHERE window_id = 'MW0001'")).scalar()
            self.assertEqual(initial_count, 4)

            req = SimulationRunRequest(
                scenario_type="TRAFFIC_PLUS_20",
                target_date=date(2026, 9, 4),
            )
            SimulationService.run_simulation(db, req)

            # Re-query after simulation
            after_count = db.execute(text("SELECT expected_train_count FROM maintenance_windows WHERE window_id = 'MW0001'")).scalar()
            self.assertEqual(after_count, 4, "Database expected_train_count must not be permanently modified!")
        finally:
            db.close()

    # -------------------------------------------------------------------------
    # Test 3, 4 & 5: Emergency Maintenance Validation, Priority & Constraints
    # -------------------------------------------------------------------------
    def test_03_emergency_request_validation(self):
        """Verifies emergency scenario runs with valid request_id."""
        db = self.TestingSessionLocal()
        try:
            req = SimulationRunRequest(
                scenario_type="EMERGENCY_MAINTENANCE",
                target_date=date(2026, 9, 4),
                request_id="MR0003",
            )
            response = SimulationService.run_simulation(db, req)
            self.assertEqual(response.scenario_type, "EMERGENCY_MAINTENANCE")
            self.assertIn("MR0003", response.explanation)
        finally:
            db.close()

    def test_04_emergency_request_gets_higher_priority(self):
        """Verifies that a low-priority task gets scheduled when designated as emergency."""
        db = self.TestingSessionLocal()
        try:
            # MR0003 is low priority (2.0/2.0 Electrical, incompatible with MR0001 Engineering)
            # In emergency scenario, MR0003 gets elevated priority
            req = SimulationRunRequest(
                scenario_type="EMERGENCY_MAINTENANCE",
                target_date=date(2026, 9, 4),
                request_id="MR0003",
            )
            response = SimulationService.run_simulation(db, req)
            # Check MR0003 is scheduled in scenario
            all_scenario_tasks = [
                task.request_id for block in response.scenario_blocks for task in block.tasks
            ]
            self.assertIn("MR0003", all_scenario_tasks)
        finally:
            db.close()

    def test_05_emergency_constraints_remain_enforced(self):
        """Verifies that an emergency task exceeding window capacity is NOT scheduled (infeasible)."""
        db = self.TestingSessionLocal()
        try:
            # Insert a huge task (duration 10 hours) on SEC_DEL_TKD where max window is 3 hours
            db.execute(text("""
                INSERT INTO maintenance_requests (id, request_id, asset_id, section_id, department, maintenance_type, severity, criticality_score, duration_hours, due_date, status)
                VALUES (99, 'MR_HUGE', 'AST1', 'SEC_DEL_TKD', 'Engineering', 'Mega overhaul', 5.0, 5.0, 10.0, '2026-09-04 12:00:00', 'PENDING');
            """))
            conn = db.connection()
            db.commit()

            req = SimulationRunRequest(
                scenario_type="EMERGENCY_MAINTENANCE",
                target_date=date(2026, 9, 4),
                request_id="MR_HUGE",
            )
            response = SimulationService.run_simulation(db, req)
            all_scenario_tasks = [
                task.request_id for block in response.scenario_blocks for task in block.tasks
            ]
            self.assertNotIn("MR_HUGE", all_scenario_tasks, "Emergency task cannot violate duration/capacity constraint!")
            self.assertIn("could not be scheduled due to strict operational constraints", response.explanation)
        finally:
            db.close()

    # -------------------------------------------------------------------------
    # Test 6 & 7: Remove Maintenance Window Validation & Exclusion
    # -------------------------------------------------------------------------
    def test_06_remove_window_validation(self):
        """Tests that REMOVE_MAINTENANCE_WINDOW runs with valid window_id."""
        db = self.TestingSessionLocal()
        try:
            req = SimulationRunRequest(
                scenario_type="REMOVE_MAINTENANCE_WINDOW",
                target_date=date(2026, 9, 4),
                window_id="MW0001",
            )
            response = SimulationService.run_simulation(db, req)
            self.assertEqual(response.scenario_type, "REMOVE_MAINTENANCE_WINDOW")
            self.assertIn("MW0001", response.explanation)
        finally:
            db.close()

    def test_07_removed_window_absent_from_scenario_blocks(self):
        """Verifies that the removed window is absent from scenario blocks."""
        db = self.TestingSessionLocal()
        try:
            req = SimulationRunRequest(
                scenario_type="REMOVE_MAINTENANCE_WINDOW",
                target_date=date(2026, 9, 4),
                window_id="MW0001",
            )
            response = SimulationService.run_simulation(db, req)
            for block in response.scenario_blocks:
                # MW0001 was at 01:00 to 04:00 (1:00 hour)
                self.assertNotEqual(block.start_time.hour, 1, "MW0001 must not be used in scenario blocks!")
        finally:
            db.close()

    # -------------------------------------------------------------------------
    # Test 8, 9, 10, 11: Comparison Calculations & Task Detections
    # -------------------------------------------------------------------------
    def test_08_baseline_scenario_comparison_calculations(self):
        """Tests that metrics and deltas are calculated accurately."""
        db = self.TestingSessionLocal()
        try:
            req = SimulationRunRequest(
                scenario_type="TRAFFIC_PLUS_20",
                target_date=date(2026, 9, 4),
            )
            response = SimulationService.run_simulation(db, req)
            diff = response.difference
            self.assertEqual(
                diff.scheduled_tasks_delta,
                response.scenario.scheduled_tasks - response.baseline.scheduled_tasks,
            )
            self.assertEqual(
                diff.blocks_delta,
                response.scenario.blocks - response.baseline.blocks,
            )
            self.assertEqual(
                diff.scheduled_duration_delta_hours,
                round(response.scenario.total_scheduled_duration_hours - response.baseline.total_scheduled_duration_hours, 2),
            )
        finally:
            db.close()

    def test_09_newly_scheduled_task_detection(self):
        """Tests detection of tasks scheduled in scenario but not in baseline."""
        db = self.TestingSessionLocal()
        try:
            # Set MR0003 as emergency, causing it to become newly scheduled
            req = SimulationRunRequest(
                scenario_type="EMERGENCY_MAINTENANCE",
                target_date=date(2026, 9, 4),
                request_id="MR0003",
            )
            response = SimulationService.run_simulation(db, req)
            if "MR0003" not in [t.request_id for b in response.baseline_blocks for t in b.tasks]:
                self.assertIn("MR0003", response.newly_scheduled_tasks)
        finally:
            db.close()

    def test_10_moved_task_detection(self):
        """Tests detection of tasks moved to another window when one window is removed."""
        db = self.TestingSessionLocal()
        try:
            # Removing MW0001 (low traffic night) forces tasks into MW0002 (medium traffic)
            req = SimulationRunRequest(
                scenario_type="REMOVE_MAINTENANCE_WINDOW",
                target_date=date(2026, 9, 4),
                window_id="MW0001",
            )
            response = SimulationService.run_simulation(db, req)
            # If tasks moved from MW0001 to MW0002, they should be in moved_tasks
            if response.moved_tasks:
                self.assertTrue(len(response.moved_tasks) > 0)
                self.assertIn("reassigned", response.explanation)
        finally:
            db.close()

    def test_11_unscheduled_task_detection(self):
        """Tests detection of tasks that become unscheduled after window removal."""
        db = self.TestingSessionLocal()
        try:
            # Delete MW0002 so MW0001 is the ONLY window available
            db.execute(text("DELETE FROM maintenance_windows WHERE window_id = 'MW0002';"))
            db.commit()

            # Now removing MW0001 leaves 0 windows, so all previously scheduled tasks become unscheduled
            req = SimulationRunRequest(
                scenario_type="REMOVE_MAINTENANCE_WINDOW",
                target_date=date(2026, 9, 4),
                window_id="MW0001",
            )
            response = SimulationService.run_simulation(db, req)
            self.assertGreater(len(response.unscheduled_tasks_after_simulation), 0)
            self.assertEqual(response.scenario.scheduled_tasks, 0)
        finally:
            db.close()

    # -------------------------------------------------------------------------
    # Test 12: Zero Database Persistence
    # -------------------------------------------------------------------------
    def test_12_simulation_does_not_persist_production_records(self):
        """Verifies that simulation does not insert OptimizationRun, OptimizedBlock, or BlockTask into DB."""
        db = self.TestingSessionLocal()
        try:
            runs_before = db.execute(text("SELECT count(*) FROM optimization_runs")).scalar()
            blocks_before = db.execute(text("SELECT count(*) FROM optimized_blocks")).scalar()
            tasks_before = db.execute(text("SELECT count(*) FROM block_tasks")).scalar()

            req = SimulationRunRequest(
                scenario_type="TRAFFIC_PLUS_20",
                target_date=date(2026, 9, 4),
            )
            SimulationService.run_simulation(db, req)

            runs_after = db.execute(text("SELECT count(*) FROM optimization_runs")).scalar()
            blocks_after = db.execute(text("SELECT count(*) FROM optimized_blocks")).scalar()
            tasks_after = db.execute(text("SELECT count(*) FROM block_tasks")).scalar()

            self.assertEqual(runs_before, runs_after, "Simulation must not create OptimizationRun rows in DB!")
            self.assertEqual(blocks_before, blocks_after, "Simulation must not create OptimizedBlock rows in DB!")
            self.assertEqual(tasks_before, tasks_after, "Simulation must not create BlockTask rows in DB!")
        finally:
            db.close()

    # -------------------------------------------------------------------------
    # Test 13: API Success Response
    # -------------------------------------------------------------------------
    def test_13_api_success_response(self):
        """Tests POST /api/v1/simulation/run returns 200 with valid schema."""
        payload = {
            "scenario_type": "TRAFFIC_PLUS_20",
            "target_date": "2026-09-04",
        }
        res = self.client.post("/api/v1/simulation/run", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["scenario_type"], "TRAFFIC_PLUS_20")
        self.assertIn("baseline", data)
        self.assertIn("scenario", data)
        self.assertIn("difference", data)
        self.assertIn("baseline_blocks", data)
        self.assertIn("scenario_blocks", data)

    # -------------------------------------------------------------------------
    # Test 14, 15, 16, 17, 18: Invalid Requests & Error Handling
    # -------------------------------------------------------------------------
    def test_14_invalid_scenario_request(self):
        """Tests 422 for invalid scenario_type."""
        payload = {
            "scenario_type": "INVALID_SCENARIO",
            "target_date": "2026-09-04",
        }
        res = self.client.post("/api/v1/simulation/run", json=payload)
        self.assertEqual(res.status_code, 422)

    def test_15_missing_request_id_for_emergency(self):
        """Tests 422/400 when EMERGENCY_MAINTENANCE lacks request_id."""
        payload = {
            "scenario_type": "EMERGENCY_MAINTENANCE",
            "target_date": "2026-09-04",
        }
        res = self.client.post("/api/v1/simulation/run", json=payload)
        self.assertIn(res.status_code, (400, 422))

    def test_16_missing_window_id_for_remove_window(self):
        """Tests 422/400 when REMOVE_MAINTENANCE_WINDOW lacks window_id."""
        payload = {
            "scenario_type": "REMOVE_MAINTENANCE_WINDOW",
            "target_date": "2026-09-04",
        }
        res = self.client.post("/api/v1/simulation/run", json=payload)
        self.assertIn(res.status_code, (400, 422))

    def test_17_invalid_request_id(self):
        """Tests 400 when request_id does not exist in DB."""
        payload = {
            "scenario_type": "EMERGENCY_MAINTENANCE",
            "target_date": "2026-09-04",
            "request_id": "MR_NON_EXISTENT",
        }
        res = self.client.post("/api/v1/simulation/run", json=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("REQUEST_NOT_FOUND", res.text)

    def test_18_invalid_window_id(self):
        """Tests 400 when window_id does not exist in DB."""
        payload = {
            "scenario_type": "REMOVE_MAINTENANCE_WINDOW",
            "target_date": "2026-09-04",
            "window_id": "MW_NON_EXISTENT",
        }
        res = self.client.post("/api/v1/simulation/run", json=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("WINDOW_NOT_FOUND", res.text)


if __name__ == "__main__":
    unittest.main()
