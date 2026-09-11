"""
PlanRail Optimization Service & API Integration Tests
=====================================================

Tests database persistence, transaction integrity, API contract validation,
and edge case handling for the OR-Tools optimization engine.
"""

from __future__ import annotations

import unittest
from datetime import date, datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models.block import BlockStatus, BlockTask, MaintenanceWindow, OptimizationRun, OptimizedBlock


class TestOptimizationServiceAndAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create an in-memory SQLite database with StaticPool so all connections share the DB
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        with cls.engine.connect() as conn:
            # Core domain tables matching Alembic migration schema
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

            # Seed test data
            conn.execute(text("INSERT INTO stations (id, station_id, station_code, station_name, latitude, longitude, km_from_ndls) VALUES (1, 'ST001', 'NDLS', 'New Delhi', 28.64, 77.22, 0.0), (2, 'ST002', 'NZM', 'Nizamuddin', 28.58, 77.25, 7.0)"))
            conn.execute(text("INSERT INTO railway_sections (id, section_id, section_code, from_station_code, to_station_code, distance_km) VALUES (1, 'SEC_DEL_NZM', 'SEC_DEL_NZM', 'NDLS', 'NZM', 7.0), (2, 'SEC_NZM_FDB', 'SEC_NZM_FDB', 'NZM', 'NDLS', 21.0)"))
            conn.execute(text("INSERT INTO assets (id, asset_id, section_id, asset_type, department, criticality) VALUES (1, 'AST_TRK_01', 'SEC_DEL_NZM', 'Track', 'Engineering', 'CRITICAL'), (2, 'AST_SIG_01', 'SEC_DEL_NZM', 'Signal', 'Signalling', 'HIGH'), (3, 'AST_OHE_01', 'SEC_DEL_NZM', 'OHE', 'Electrical', 'HIGH')"))
            conn.execute(text("INSERT INTO maintenance_compatibility (department_a, department_b, compatibility) VALUES ('Engineering', 'Signalling', 'COMPATIBLE'), ('Engineering', 'Electrical', 'INCOMPATIBLE')"))
            conn.execute(text("INSERT INTO maintenance_windows (id, window_id, section_id, start_hour, start_time, end_time, expected_train_count, traffic_level, is_feasible) VALUES (1, 'MW_DEL_NZM_01', 'SEC_DEL_NZM', 1, '01:00:00', '05:00:00', 0, 'LOW', 1), (2, 'MW_DEL_NZM_02', 'SEC_DEL_NZM', 10, '10:00:00', '14:00:00', 8, 'HIGH', 1)"))
            conn.execute(text("INSERT INTO maintenance_requests (id, request_id, asset_id, section_id, department, maintenance_type, severity, criticality_score, duration_hours, due_date, status, priority_score) VALUES (1, 'MR0001', 'AST_TRK_01', 'SEC_DEL_NZM', 'Engineering', 'Track Tamping', 4.0, 4.5, 2.0, '2026-09-10 12:00:00', 'PENDING', 90.0), (2, 'MR0002', 'AST_SIG_01', 'SEC_DEL_NZM', 'Signalling', 'Relay Check', 3.5, 4.0, 1.5, '2026-09-10 12:00:00', 'PENDING', 85.0), (3, 'MR0003', 'AST_OHE_01', 'SEC_DEL_NZM', 'Electrical', 'OHE Wire Fix', 4.5, 5.0, 3.0, '2026-09-10 12:00:00', 'PENDING', 95.0)"))
            conn.commit()

        cls.SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)

        def override_get_db():
            test_db = cls.SessionTesting()
            try:
                yield test_db
            finally:
                test_db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()

    def test_01_optimization_generate_api_success(self):
        """Test 1-5: Valid generation returns 200, correct schema, metrics, and block tasks."""
        payload = {
            "target_date": "2026-09-10",
            "max_block_duration_hours": 4.0,
        }
        res = self.client.post("/api/v1/optimization/generate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Schema & run_id
        self.assertTrue(data["run_id"].startswith("RUN_20260910_"))
        self.assertIn(data["status"], ("OPTIMAL", "FEASIBLE"))
        self.assertEqual(data["target_date"], "2026-09-10")
        self.assertEqual(data["total_requests_considered"], 3)
        self.assertGreaterEqual(data["scheduled_tasks_count"], 1)
        self.assertEqual(
            data["scheduled_tasks_count"] + data["unscheduled_tasks_count"],
            data["total_requests_considered"],
        )
        self.assertEqual(len(data["blocks"]), data["blocks_count"])

        # Block verification
        block = data["blocks"][0]
        self.assertIn("block_id", block)
        self.assertEqual(block["section_id"], "SEC_DEL_NZM")
        self.assertGreater(block["duration_hours"], 0)
        self.assertGreater(len(block["tasks"]), 0)

        # Task verification
        task = block["tasks"][0]
        self.assertIn("block_task_id", task)
        self.assertIn("request_id", task)
        self.assertIn("sequence", task)

    def test_02_database_persistence_verification(self):
        """Test 6-9: Verify rows were committed to OptimizationRun, OptimizedBlock, BlockTask."""
        db = self.SessionTesting()
        try:
            runs = db.query(OptimizationRun).all()
            self.assertGreaterEqual(len(runs), 1)
            last_run = runs[-1]
            self.assertEqual(last_run.status, "OPTIMAL")

            blocks = db.query(OptimizedBlock).filter(OptimizedBlock.optimization_run_id == last_run.id).all()
            self.assertGreaterEqual(len(blocks), 1)

            for b in blocks:
                self.assertEqual(b.section_id, 1)  # Section PK is 1
                self.assertEqual(b.status, BlockStatus.PROPOSED)
                self.assertGreater(len(b.block_tasks), 0)
                for bt in b.block_tasks:
                    self.assertGreater(bt.maintenance_request_id, 0)
                    self.assertGreaterEqual(bt.sequence_order, 1)
        finally:
            db.close()

    def test_03_repeated_optimization_runs_independence(self):
        """Test 12: Repeated optimization does not overwrite or corrupt previous runs."""
        db = self.SessionTesting()
        try:
            initial_runs = db.query(OptimizationRun).count()
            initial_blocks = db.query(OptimizedBlock).count()
        finally:
            db.close()

        # Run second optimization
        payload = {"target_date": "2026-09-10", "max_block_duration_hours": 3.0}
        res = self.client.post("/api/v1/optimization/generate", json=payload)
        self.assertEqual(res.status_code, 200)

        db = self.SessionTesting()
        try:
            new_runs = db.query(OptimizationRun).count()
            new_blocks = db.query(OptimizedBlock).count()
            self.assertEqual(new_runs, initial_runs + 1)
            self.assertGreater(new_blocks, initial_blocks)
        finally:
            db.close()

    def test_04_selected_request_ids_filtering(self):
        """Test specific request ID targeting."""
        payload = {
            "target_date": "2026-09-10",
            "selected_request_ids": ["MR0001"],
            "max_block_duration_hours": 4.0,
        }
        res = self.client.post("/api/v1/optimization/generate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_requests_considered"], 1)
        self.assertEqual(data["scheduled_tasks_count"], 1)
        self.assertEqual(data["blocks"][0]["tasks"][0]["request_id"], "MR0001")

    def test_05_invalid_request_handling(self):
        """Test 10: Invalid request payloads return 422 or 400."""
        # Non-existent target date format
        res = self.client.post("/api/v1/optimization/generate", json={"target_date": "invalid-date"})
        self.assertEqual(res.status_code, 422)

        # Empty selection that has no matching records
        res_empty = self.client.post("/api/v1/optimization/generate", json={"target_date": "2026-09-10", "selected_request_ids": ["MR_NON_EXISTENT"]})
        self.assertEqual(res_empty.status_code, 400)
        self.assertEqual(res_empty.json()["detail"]["code"], "NO_ELIGIBLE_REQUESTS")

    def test_06_blocks_api_endpoint_integration(self):
        """Test 11: GET /api/v1/blocks returns all persisted blocks."""
        res = self.client.get("/api/v1/blocks")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("items", data)
        self.assertGreaterEqual(data["total"], 1)
        first_item = data["items"][0]
        self.assertIn("block_id", first_item)
        self.assertIn("tasks", first_item)


if __name__ == "__main__":
    unittest.main()
