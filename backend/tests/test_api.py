import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestPlanRailAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/v1/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "ok"})

    def test_health_db(self):
        res = self.client.get("/api/v1/health/db")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["database"], "connected")

    def test_dashboard(self):
        res = self.client.get("/api/v1/dashboard")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_maintenance_requests", data)
        self.assertIn("total_trains", data)

    def test_stations(self):
        res = self.client.get("/api/v1/stations")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["total"], 18)
        self.assertGreater(len(data["items"]), 0)

        # Specific station ST001
        res_st = self.client.get("/api/v1/stations/ST001")
        self.assertEqual(res_st.status_code, 200)
        self.assertEqual(res_st.json()["station_id"], "ST001")

        # Invalid station
        res_inv = self.client.get("/api/v1/stations/ST99999")
        self.assertEqual(res_inv.status_code, 404)

    def test_sections(self):
        res = self.client.get("/api/v1/sections")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["total"], 17)

    def test_assets(self):
        res = self.client.get("/api/v1/assets")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["total"], 85)

    def test_maintenance(self):
        res = self.client.get("/api/v1/maintenance")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["total"], 150)

        # Specific MR0001
        res_mr = self.client.get("/api/v1/maintenance/MR0001")
        self.assertEqual(res_mr.status_code, 200)
        self.assertEqual(res_mr.json()["request_id"], "MR0001")

    def test_trains(self):
        res = self.client.get("/api/v1/trains")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["total"], 24)

        # Train schedule
        train_num = data["items"][0]["train_number"]
        res_sch = self.client.get(f"/api/v1/trains/{train_num}/schedule")
        self.assertEqual(res_sch.status_code, 200)
        self.assertIsInstance(res_sch.json(), list)

    def test_windows(self):
        res_maint = self.client.get("/api/v1/maintenance-windows")
        self.assertEqual(res_maint.status_code, 200)
        self.assertGreaterEqual(res_maint.json()["total"], 408)

        res_traf = self.client.get("/api/v1/traffic-windows")
        self.assertEqual(res_traf.status_code, 200)
        self.assertGreaterEqual(res_traf.json()["total"], 408)

    def test_optimization_generate(self):
        res_opt = self.client.post(
            "/api/v1/optimization/generate",
            json={"target_date": "2026-09-10", "max_block_duration_hours": 4.0}
        )
        self.assertEqual(res_opt.status_code, 200)
        data = res_opt.json()
        self.assertIn("run_id", data)
        self.assertIn(data["status"], ("OPTIMAL", "FEASIBLE"))
        self.assertGreaterEqual(data["total_requests_considered"], 1)
        self.assertGreaterEqual(data["scheduled_tasks_count"], 1)
        self.assertGreaterEqual(data["blocks_count"], 1)
        self.assertEqual(len(data["blocks"]), data["blocks_count"])
        self.assertEqual(
            data["scheduled_tasks_count"] + data["unscheduled_tasks_count"],
            data["total_requests_considered"]
        )
        
        # Verify first block structure
        first_block = data["blocks"][0]
        self.assertIn("block_id", first_block)
        self.assertIn("section_id", first_block)
        self.assertIn("duration_hours", first_block)
        self.assertGreater(len(first_block["tasks"]), 0)
        self.assertIn("request_id", first_block["tasks"][0])

    def test_blocks_list_after_optimization(self):
        res_blocks = self.client.get("/api/v1/blocks")
        self.assertEqual(res_blocks.status_code, 200)
        data = res_blocks.json()
        self.assertIn("items", data)
        self.assertIn("total", data)

    def test_simulation_contract(self):
        res_sim = self.client.post("/api/v1/simulation/run", json={"scenario_type": "TRAFFIC_PLUS_20", "target_date": "2026-09-10"})
        self.assertEqual(res_sim.status_code, 200)
        self.assertIn("simulation_id", res_sim.json())

    def test_ai_predict(self):
        res_ai = self.client.post("/api/v1/ai/predict", json={"request_id": "MR0001"})
        self.assertEqual(res_ai.status_code, 200)
        self.assertEqual(res_ai.json()["request_id"], "MR0001")

if __name__ == "__main__":
    unittest.main()
