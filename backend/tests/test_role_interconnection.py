import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import SessionLocal, init_db
from app.models.maintenance import MaintenanceRequest
from app.models.block import OptimizedBlock, BlockStatus


class TestRoleInterconnection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_01_maintenance_status_lifecycle(self):
        """Crew updates maintenance task status: PENDING -> ACCEPTED -> IN_PROGRESS -> COMPLETED."""
        # Find a test request
        with SessionLocal() as db:
            req = db.query(MaintenanceRequest).filter(MaintenanceRequest.request_id == "MR0001").first()
            self.assertIsNotNone(req)
            orig_status = req.status

        try:
            # 1. Accept Task
            res = self.client.patch("/api/v1/maintenance/MR0001/status", json={"status": "ACCEPTED"})
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()["status"], "ACCEPTED")

            # 2. Start Work
            res = self.client.patch("/api/v1/maintenance/MR0001/status", json={"status": "IN_PROGRESS"})
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()["status"], "IN_PROGRESS")

            # 3. Complete Task
            res = self.client.patch("/api/v1/maintenance/MR0001/status", json={"status": "COMPLETED"})
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()["status"], "COMPLETED")
        finally:
            # Reset status
            with SessionLocal() as db:
                r = db.query(MaintenanceRequest).filter(MaintenanceRequest.request_id == "MR0001").first()
                if r:
                    r.status = orig_status
                    db.commit()

    def test_02_emergency_defect_reporting(self):
        """Crew reports emergency defect -> persists in DB and is queryable."""
        payload = {
            "section_id": "SEC001",
            "department": "Engineering",
            "maintenance_type": "Emergency Rail Fracture Rectification",
            "severity": 5.0,
            "criticality_score": 5.0,
            "duration_hours": 2.5,
            "description": "Critical fishplate crack reported by driver of 12002 Shatabdi",
        }
        res = self.client.post("/api/v1/maintenance/emergency", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        req_id = data["request_id"]
        self.assertTrue(req_id.startswith("EMG"))
        self.assertEqual(data["section_id"], "SEC001")
        self.assertEqual(data["severity"], 5.0)

        # Verify queryable in general maintenance queue
        get_res = self.client.get(f"/api/v1/maintenance/{req_id}")
        self.assertEqual(get_res.status_code, 200)

        # Clean up created emergency test record to keep test counts isolated
        with SessionLocal() as db:
            db.query(MaintenanceRequest).filter(MaintenanceRequest.request_id == req_id).delete()
            db.commit()


    def test_03_block_status_approval(self):
        """Controller approves/rejects a generated block plan."""
        # Find or create a block to test
        with SessionLocal() as db:
            block = db.query(OptimizedBlock).first()
            if block:
                block_id = block.block_code
                res = self.client.patch(f"/api/v1/blocks/{block_id}/status", json={"status": "APPROVED"})
                self.assertEqual(res.status_code, 200)
                self.assertEqual(res.json()["status"], "APPROVED")

    def test_04_admin_health_diagnostics(self):
        """Admin health endpoint returns live component and database status."""
        res = self.client.get("/api/v1/admin/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("status", data)
        self.assertEqual(data["backend"]["status"], "ONLINE")
        self.assertEqual(data["database"]["status"], "CONNECTED")
        self.assertEqual(data["ai_engine"]["status"], "XGBOOST_TRAINED_MODEL")
        self.assertGreaterEqual(data["data_counts"]["stations"], 18)
        self.assertGreaterEqual(data["data_counts"]["freight_movements"], 36)

    def test_05_admin_config_get_and_update(self):
        """Admin gets and updates persistent operational configuration."""
        res = self.client.get("/api/v1/admin/config")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("max_block_duration_hours", data)

        # Update config
        update_payload = {
            "max_block_duration_hours": 3.5,
            "emergency_priority_multiplier": 1.8,
            "auto_approval_threshold": 85.0,
        }
        post_res = self.client.post("/api/v1/admin/config", json=update_payload)
        self.assertEqual(post_res.status_code, 200)
        updated = post_res.json()
        self.assertEqual(updated["max_block_duration_hours"], 3.5)
        self.assertEqual(updated["emergency_priority_multiplier"], 1.8)
        self.assertEqual(updated["auto_approval_threshold"], 85.0)

    def test_06_dashboard_action_required(self):
        """Dashboard returns action_required items for Controller Attention."""
        res = self.client.get("/api/v1/dashboard")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("action_required", data)
        self.assertGreaterEqual(len(data["action_required"]), 1)
        self.assertGreaterEqual(data["critical_high_requests"], 1)


if __name__ == "__main__":
    unittest.main()
