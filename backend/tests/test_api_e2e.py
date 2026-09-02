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
        self.assertTrue(data["postgis"])

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

        # Single station
        st_status, st_data = make_request("/stations/ST001")
        self.assertEqual(st_status, 200)
        self.assertEqual(st_data["station_id"], "ST001")
        self.assertEqual(st_data["station_code"], "NDLS")

        # Invalid station
        inv_status, inv_data = make_request("/stations/ST99999")
        self.assertEqual(inv_status, 404)
        self.assertEqual(inv_data["detail"]["code"], "RESOURCE_NOT_FOUND")

    def test_05_sections(self):
        status, data = make_request("/sections")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(data["total"], 17)

    def test_06_assets(self):
        status, data = make_request("/assets?department=Engineering")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(data["total"], 1)

    def test_07_maintenance(self):
        status, data = make_request("/maintenance?status=PENDING")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(data["total"], 1)

        mr_status, mr_data = make_request("/maintenance/MR0001")
        self.assertEqual(mr_status, 200)
        self.assertEqual(mr_data["request_id"], "MR0001")
        self.assertIn("history", mr_data)

    def test_08_trains(self):
        status, data = make_request("/trains")
        self.assertEqual(status, 200)
        self.assertEqual(data["total"], 24)

        # Schedule for valid train number 12050
        sch_status, sch_data = make_request("/trains/12050/schedule")
        self.assertEqual(sch_status, 200)
        self.assertIsInstance(sch_data, list)
        self.assertGreater(len(sch_data), 0)

    def test_09_windows(self):
        maint_status, maint_data = make_request("/maintenance-windows?is_feasible=true")
        self.assertEqual(maint_status, 200)
        self.assertGreaterEqual(maint_data["total"], 1)

        traf_status, traf_data = make_request("/traffic-windows")
        self.assertEqual(traf_status, 200)
        self.assertEqual(traf_data["total"], 408)

    def test_10_unimplemented_contracts(self):
        opt_status, opt_data = make_request("/optimization/generate", method="POST", body={"target_date": "2026-09-10"})
        self.assertEqual(opt_status, 501)
        self.assertEqual(opt_data["detail"]["code"], "NOT_IMPLEMENTED")

        sim_status, sim_data = make_request("/simulation/run", method="POST", body={"selected_request_ids": ["MR0001"]})
        self.assertEqual(sim_status, 501)
        self.assertEqual(sim_data["detail"]["code"], "NOT_IMPLEMENTED")

    def test_11_ai_predict(self):
        ai_status, ai_data = make_request("/ai/predict", method="POST", body={"request_id": "MR0001"})
        self.assertEqual(ai_status, 200)
        self.assertEqual(ai_data["request_id"], "MR0001")
        self.assertIn("priority_score", ai_data)

if __name__ == "__main__":
    unittest.main()
