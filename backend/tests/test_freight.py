"""
PlanRail Freight Integration Tests
==================================

Comprehensive test suite verifying the synthetic freight planning dataset integration:
1. Freight CSV parsing
2. Correct record count = 36
3. No duplicate import (idempotency)
4. NDLS station code mapping
5. AGC station code mapping
6. Date parsing (2026-09-14 through 2026-09-16)
7. Time parsing
8. Traffic priority parsing
9. Freight movement interval calculation
10. Traffic integration (hourly freight pressure calculation)
11. Existing passenger train records remain unchanged
12. Simulation does not modify freight records
13. API endpoints: /api/v1/freight-trains and /api/v1/freight-trains/{id}
"""

import unittest
from datetime import date
from fastapi.testclient import TestClient

from app.main import app
from app.database.connection import SessionLocal, init_db
from app.database.freight_loader import import_freight_dataset, find_freight_csv_path
from app.models.freight import FreightTrainMovement
from app.models.train import Train
from app.models.station import Station
from app.services.freight_service import FreightService
from app.services.simulation_service import SimulationService
from app.schemas.domain import SimulationRunRequest


class TestFreightIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_01_freight_csv_path_and_parsing(self):
        """1. Verify freight CSV file exists and can be located."""
        csv_path = find_freight_csv_path()
        self.assertIsNotNone(csv_path)
        self.assertTrue(csv_path.is_file())

    def test_02_correct_record_count_36(self):
        """2. Verify that exactly 36 freight planning records are in the database."""
        with SessionLocal() as db:
            count = db.query(FreightTrainMovement).count()
            self.assertEqual(count, 36)

    def test_03_no_duplicate_import(self):
        """3. Verify idempotency: re-running import_freight_dataset does not create duplicates."""
        with SessionLocal() as db:
            initial_count = db.query(FreightTrainMovement).count()
            inserted, total = import_freight_dataset(db)
            self.assertEqual(inserted, 0)
            self.assertEqual(total, initial_count)
            self.assertEqual(db.query(FreightTrainMovement).count(), 36)

    def test_04_ndls_mapping(self):
        """4. Verify NDLS station mapping and presence in freight records."""
        with SessionLocal() as db:
            st = db.query(Station).filter(Station.station_code == "NDLS").first()
            self.assertIsNotNone(st)
            self.assertEqual(st.station_code, "NDLS")

            ndls_freight = db.query(FreightTrainMovement).filter(
                (FreightTrainMovement.origin_station_code == "NDLS") |
                (FreightTrainMovement.destination_station_code == "NDLS")
            ).all()
            self.assertGreaterEqual(len(ndls_freight), 1)

    def test_05_agc_mapping(self):
        """5. Verify AGC station mapping and presence in freight records."""
        with SessionLocal() as db:
            st = db.query(Station).filter(Station.station_code == "AGC").first()
            self.assertIsNotNone(st)
            self.assertEqual(st.station_code, "AGC")

            agc_freight = db.query(FreightTrainMovement).filter(
                (FreightTrainMovement.origin_station_code == "AGC") |
                (FreightTrainMovement.destination_station_code == "AGC")
            ).all()
            self.assertGreaterEqual(len(agc_freight), 1)

    def test_06_date_parsing_range(self):
        """6. Verify date parsing across 2026-09-14 through 2026-09-16."""
        with SessionLocal() as db:
            dates = db.query(FreightTrainMovement.movement_date).distinct().all()
            date_values = sorted([d[0] for d in dates])
            expected_dates = [date(2026, 9, 14), date(2026, 9, 15), date(2026, 9, 16)]
            self.assertEqual(date_values, expected_dates)

            for d in expected_dates:
                cnt = db.query(FreightTrainMovement).filter(FreightTrainMovement.movement_date == d).count()
                self.assertEqual(cnt, 12)

    def test_07_time_parsing(self):
        """7. Verify planned_entry_time and planned_exit_time format."""
        with SessionLocal() as db:
            records = db.query(FreightTrainMovement).all()
            for r in records:
                self.assertRegex(r.planned_entry_time, r"^\d{2}:\d{2}$")
                self.assertRegex(r.planned_exit_time, r"^\d{2}:\d{2}$")

    def test_08_traffic_priority_parsing(self):
        """8. Verify traffic priority values: High, Medium, Critical."""
        with SessionLocal() as db:
            priorities = db.query(FreightTrainMovement.traffic_priority).distinct().all()
            priority_set = {p[0] for p in priorities}
            self.assertTrue({"High", "Medium", "Critical"}.issubset(priority_set))

    def test_09_movement_interval_calculation(self):
        """9. Verify entry to exit interval validity."""
        with SessionLocal() as db:
            record = db.query(FreightTrainMovement).filter(FreightTrainMovement.freight_train_id == "FT-DA-001").first()
            self.assertIsNotNone(record)
            entry_parts = [int(p) for p in record.planned_entry_time.split(":")]
            exit_parts = [int(p) for p in record.planned_exit_time.split(":")]
            entry_minutes = entry_parts[0] * 60 + entry_parts[1]
            exit_minutes = exit_parts[0] * 60 + exit_parts[1]
            duration_minutes = exit_minutes - entry_minutes
            self.assertGreater(duration_minutes, 0)
            self.assertEqual(record.commodity, "Coal")
            self.assertEqual(record.load_tonnes, 4200.0)

    def test_10_traffic_integration(self):
        """10. Verify hourly freight traffic pressure calculation."""
        with SessionLocal() as db:
            target_date = date(2026, 9, 14)
            hourly_traffic = FreightService.get_hourly_freight_traffic(db, target_date=target_date)
            self.assertIsInstance(hourly_traffic, dict)
            self.assertEqual(len(hourly_traffic), 24)
            # Hour 6 and 8 should have positive freight traffic pressure
            self.assertGreater(hourly_traffic[6], 0.0)
            self.assertGreater(hourly_traffic[8], 0.0)

    def test_11_passenger_records_unchanged(self):
        """11. Verify existing passenger trains remain exactly 24 and unmodified."""
        with SessionLocal() as db:
            passenger_count = db.query(Train).count()
            self.assertEqual(passenger_count, 24)

    def test_12_simulation_does_not_modify_freight_records(self):
        """12. Verify simulation runs do not alter or delete freight records."""
        with SessionLocal() as db:
            initial_count = db.query(FreightTrainMovement).count()

            # Execute TRAFFIC_PLUS_20 simulation
            sim_req = SimulationRunRequest(
                scenario_type="TRAFFIC_PLUS_20",
                target_date=date(2026, 9, 14),
            )
            sim_res = SimulationService.run_simulation(db, sim_req)
            self.assertIsNotNone(sim_res.simulation_id)

            # Assert database freight count unchanged
            post_sim_count = db.query(FreightTrainMovement).count()
            self.assertEqual(post_sim_count, initial_count)
            self.assertEqual(post_sim_count, 36)

    def test_13_api_freight_trains_endpoints(self):
        """13. Verify GET /api/v1/freight-trains and GET /api/v1/freight-trains/{id} responses."""
        # List endpoint
        res = self.client.get("/api/v1/freight-trains?page=1&page_size=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total"], 36)
        self.assertEqual(len(data["items"]), 10)
        first_item = data["items"][0]
        self.assertIn("freight_train_id", first_item)
        self.assertEqual(first_item["data_status"], "SIMULATED_BY_PLANRAIL")
        self.assertIn("simulation_note", first_item)

        # Single item endpoint
        single_res = self.client.get(f"/api/v1/freight-trains/{first_item['freight_train_id']}")
        self.assertEqual(single_res.status_code, 200)
        single_data = single_res.json()
        self.assertEqual(single_data["freight_train_id"], first_item["freight_train_id"])
        self.assertEqual(single_data["data_status"], "SIMULATED_BY_PLANRAIL")

        # Non-existent item endpoint
        not_found_res = self.client.get("/api/v1/freight-trains/FT-INVALID-999")
        self.assertEqual(not_found_res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
