import urllib.request
import json
import unittest

BASE_URL = "http://127.0.0.1:8000/api/v1"

def make_request(path, method="GET", body=None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode('utf-8') if body else None
    headers = {"Content-Type": "application/json"} if body else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            return response.status, json.loads(res_body) if res_body else None
    except urllib.error.HTTPError as e:
        res_body = e.read().decode('utf-8')
        return e.code, json.loads(res_body) if res_body else None

class TestPlanRailAPIE2E(unittest.TestCase):
    def test_01_health(self):
        status, data = make_request("/health")
        self.assertEqual(status, 200)
        self.assertEqual(data, {"status": "ok"})

    def test_02_health_db(self):
        status, data = make_request("/health/db")
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["database"], "connected")
        self.assertIn("postgis", data)

    def test_03_dashboard(self):
        status, data = make_request("/dashboard")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(data["total_maintenance_requests"], 150)
        self.assertEqual(data["total_trains"], 24)

    def test_04_stations(self):
        status, data = make_request("/stations?page=1&page_size=5")
        self.assertEqual(status, 200)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["page_size"], 5)
        self.assertGreaterEqual(data["total"], 18)

        st_status, st_data = make_request("/stations")
        self.assertEqual(st_status, 200)
        self.assertEqual(st_data["total"], 18)
        self.assertEqual(len(st_data["items"]), 18)

    def test_05_sections(self):
        sec_status, sec_data = make_request("/sections")
        self.assertEqual(sec_status, 200)
        self.assertEqual(sec_data["total"], 17)
        self.assertEqual(len(sec_data["items"]), 17)

    def test_06_assets(self):
        ast_status, ast_data = make_request("/assets")
        self.assertEqual(ast_status, 200)
        self.assertEqual(ast_data["total"], 85)

    def test_07_maintenance(self):
        maint_status, maint_data = make_request("/maintenance")
        self.assertEqual(maint_status, 200)
        self.assertEqual(maint_data["total"], 150)

    def test_08_trains(self):
        tr_status, tr_data = make_request("/trains")
        self.assertEqual(tr_status, 200)
        self.assertEqual(tr_data["total"], 24)

    def test_09_windows(self):
        mw_status, mw_data = make_request("/maintenance-windows")
        self.assertEqual(mw_status, 200)
        self.assertEqual(mw_data["total"], 408)

        traf_status, traf_data = make_request("/traffic-windows")
        self.assertEqual(traf_status, 200)
        self.assertEqual(traf_data["total"], 408)

    def test_10_optimization_generate(self):
        opt_status, opt_data = make_request("/optimization/generate", method="POST", body={"target_date": "2026-09-10", "max_block_duration_hours": 4.0})
        self.assertEqual(opt_status, 200)
        self.assertIn("run_id", opt_data)
        self.assertIn(opt_data["status"], ("OPTIMAL", "FEASIBLE"))
        self.assertGreaterEqual(opt_data["scheduled_tasks_count"], 1)
        self.assertGreaterEqual(opt_data["blocks_count"], 1)

    def test_11_simulation_run(self):
        sim_status, sim_data = make_request(
            "/simulation/run",
            method="POST",
            body={"scenario_type": "TRAFFIC_PLUS_20", "target_date": "2026-09-10"},
        )
        self.assertEqual(sim_status, 200)
        self.assertIn("simulation_id", sim_data)
        self.assertEqual(sim_data["scenario_type"], "TRAFFIC_PLUS_20")

    def test_12_ai_predict(self):
        ai_status, ai_data = make_request("/ai/predict", method="POST", body={"request_id": "MR0001"})
        self.assertEqual(ai_status, 200)
        self.assertEqual(ai_data["request_id"], "MR0001")
        self.assertIn("priority_score", ai_data)

if __name__ == "__main__":
    unittest.main()
