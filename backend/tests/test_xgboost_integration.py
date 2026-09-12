"""
PlanRail XGBoost Model & AI Integration Unit Tests
==================================================

Validates:
  1. XGBoost model artifact loading & metadata
  2. 11-feature contract ordering and data types
  3. Real maintenance request prediction with SHAP explainability
  4. Nonexistent request 404 validation
  5. Corridor AI insights aggregation and distributions
"""

import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.maintenance import MaintenanceRequest
from app.ai.risk_model import RiskModel, RISK_FEATURE_COLUMNS
from app.ai.features import extract_features
from app.services.ai_service import AIService


class TestXGBoostAIIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_model_loading_and_attributes(self):
        loaded = RiskModel.load_model()
        self.assertTrue(loaded, "XGBoost model should load successfully from joblib artifact.")
        self.assertIsNotNone(RiskModel._model)
        self.assertEqual(RiskModel.MODEL_STATUS, "XGBOOST_TRAINED_MODEL")
        self.assertEqual(len(RiskModel._feature_columns), 11)
        self.assertGreater(RiskModel._threshold, 0.0)

    def test_02_feature_contract_ordering(self):
        expected_features = [
            "condition_score",
            "severity",
            "criticality",
            "overdue_days",
            "historical_failures",
            "train_density",
            "freight_train_density",
            "freight_share_percent",
            "asset_age",
            "maintenance_frequency",
            "previous_defects",
        ]
        self.assertEqual(RISK_FEATURE_COLUMNS, expected_features)
        req = self.db.query(MaintenanceRequest).first()
        self.assertIsNotNone(req)
        features = extract_features(self.db, req)
        for col in expected_features:
            self.assertIn(col, features, f"Feature {col} missing from extract_features.")
            self.assertIsInstance(features[col], (int, float), f"Feature {col} must be numeric.")

    def test_03_prediction_with_real_request(self):
        req = self.db.query(MaintenanceRequest).first()
        self.assertIsNotNone(req)
        res = self.client.post("/api/v1/ai/predict", json={"request_id": req.request_id})
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["request_id"], req.request_id)
        self.assertGreaterEqual(data["risk_probability"], 0.0)
        self.assertLessEqual(data["risk_probability"], 1.0)
        self.assertGreaterEqual(data["risk_score"], 0.0)
        self.assertLessEqual(data["risk_score"], 100.0)
        self.assertIn(data["risk_category"], ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        self.assertIn(data["priority_category"], ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        self.assertEqual(data["model_status"], "XGBOOST_TRAINED_MODEL")
        self.assertIsInstance(data["risk_contributing_factors"], list)
        self.assertTrue(len(data["explanation"]) > 20)

    def test_04_prediction_with_nonexistent_request(self):
        res = self.client.post("/api/v1/ai/predict", json={"request_id": "MR_NONEXISTENT_99999"})
        self.assertEqual(res.status_code, 404)

    def test_05_ai_insights_endpoint(self):
        res = self.client.get("/api/v1/ai/insights")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertGreaterEqual(data["total_requests_analyzed"], 150)
        self.assertEqual(data["model_status"], "XGBOOST_TRAINED_MODEL")
        self.assertIn("risk_distribution", data)
        self.assertIn("priority_distribution", data)
        self.assertIn("department_distribution", data)
        self.assertIn("high_attention_tasks", data)
        self.assertIsInstance(data["corridor_ai_recommendation"], str)

        # Verify distributions sum up to total
        risk_total = sum(data["risk_distribution"].values())
        self.assertEqual(risk_total, data["total_requests_analyzed"])


if __name__ == "__main__":
    unittest.main()
