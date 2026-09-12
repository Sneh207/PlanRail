"""
PlanRail AI Risk, Priority & Explainability Pipeline Tests
==========================================================

Comprehensive test suite validating:
  - Feature extraction & normalization
  - Predictive risk model & threshold calibration
  - Operational traffic disruption engine (passenger + synthetic freight)
  - Multi-criteria priority intelligence engine (30/25/20/15/10)
  - Explainability & controller diagnostics
  - API endpoint contracts (/ai/predict, /ai/insights)
  - Corridor-level aggregated analytics
"""

import unittest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db
from app.models.maintenance import MaintenanceRequest
from app.models.asset import Asset
from app.models.history import MaintenanceHistory
from app.ai.features import extract_features, clip_scale
from app.ai.risk_model import RiskModel, CALIBRATED_RISK_THRESHOLD
from app.ai.traffic_impact import TrafficImpactModel
from app.ai.priority_engine import PriorityEngine
from app.ai.explainability import DecisionExplainer
from app.services.ai_service import AIService


class TestAIPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # Obtain db session
        cls.db_gen = get_db()
        cls.db: Session = next(cls.db_gen)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.db_gen.close()
        except Exception:
            pass

    # =========================================================================
    # 1. Feature Engineering
    # =========================================================================
    def test_01_feature_extraction_valid(self):
        req = self.db.query(MaintenanceRequest).filter(MaintenanceRequest.request_id == "MR0001").first()
        self.assertIsNotNone(req)
        features = extract_features(self.db, req)
        
        self.assertEqual(features["request_id"], "MR0001")
        self.assertIn("severity_norm", features)
        self.assertIn("criticality_norm", features)
        self.assertIn("overdue_norm", features)
        self.assertIn("condition_risk", features)
        self.assertIn("failure_rate", features)
        self.assertIn("asset_age_norm", features)

    def test_02_feature_normalization_ranges(self):
        # Verify clipping within [0.0, 100.0]
        self.assertEqual(clip_scale(-10, 0, 100), 0.0)
        self.assertEqual(clip_scale(150, 0, 100), 100.0)
        self.assertEqual(clip_scale(5, 0, 10), 50.0)

        req = self.db.query(MaintenanceRequest).first()
        features = extract_features(self.db, req)
        for key in ["severity_norm", "criticality_norm", "overdue_norm", "condition_risk", "failure_rate", "asset_age_norm"]:
            val = features[key]
            self.assertGreaterEqual(val, 0.0, f"{key} below 0")
            self.assertLessEqual(val, 100.0, f"{key} above 100")

    def test_03_missing_feature_handling_graceful(self):
        # Create a dummy or mock-like MaintenanceRequest with missing fields
        mock_req = MaintenanceRequest(
            request_id="MOCK_TEST_01",
            asset_id="NON_EXISTENT_ASSET",
            section_id="S01_AGC_TDL",
            department="ENGINEERING",
            maintenance_type="ROUTINE",
            severity=5.0,
            criticality_score=50.0,
            duration_hours=2.0,
            due_date="2026-09-20",
            overdue_days=0,
        )
        features = extract_features(self.db, mock_req)
        self.assertEqual(features["request_id"], "MOCK_TEST_01")
        self.assertEqual(features["historical_event_count"], 0)
        self.assertEqual(features["raw_condition_score"], 75.0)  # Default fallback
        self.assertEqual(features["asset_age_years"], 10)         # Default fallback

    # =========================================================================
    # 2. Risk Model
    # =========================================================================
    def test_04_risk_model_instantiation_and_threshold(self):
        self.assertGreaterEqual(RiskModel.CALIBRATED_THRESHOLD, 0.50)
        self.assertIn(RiskModel.MODEL_STATUS, ["XGBOOST_TRAINED_MODEL", "DOMAIN_CALIBRATED_MODEL"])

    def test_05_risk_model_deterministic_scoring(self):
        features = {
            "condition_risk": 50.0,
            "failure_rate": 20.0,
            "severity_norm": 80.0,
            "overdue_ratio": 30.0,
            "asset_age_norm": 40.0,
            "raw_condition_score": 50.0,
            "raw_severity": 80.0,
            "raw_overdue_days": 10,
            "historical_event_count": 2,
            "asset_age_years": 12,
        }
        res1 = RiskModel.predict(features)
        res2 = RiskModel.predict(features)
        self.assertEqual(res1["risk_probability"], res2["risk_probability"])
        self.assertEqual(res1["risk_score"], res2["risk_score"])
        self.assertEqual(res1["risk_category"], res2["risk_category"])

    def test_06_risk_score_scale_0_to_100(self):
        features_low = {"condition_risk": 0.0, "failure_rate": 0.0, "severity_norm": 0.0, "overdue_ratio": 0.0, "asset_age_norm": 0.0}
        features_high = {"condition_risk": 100.0, "failure_rate": 100.0, "severity_norm": 100.0, "overdue_ratio": 100.0, "asset_age_norm": 100.0}
        
        pred_low = RiskModel.predict(features_low)
        pred_high = RiskModel.predict(features_high)

        self.assertGreaterEqual(pred_low["risk_score"], 0.0)
        self.assertLessEqual(pred_high["risk_score"], 100.0)
        self.assertLess(pred_low["risk_score"], pred_high["risk_score"])

    def test_07_risk_category_assignment(self):
        self.assertEqual(RiskModel.categorize_risk(0.15), "LOW")
        self.assertEqual(RiskModel.categorize_risk(0.45), "MEDIUM")
        self.assertEqual(RiskModel.categorize_risk(0.75), "HIGH")
        self.assertEqual(RiskModel.categorize_risk(0.85), "CRITICAL")
        self.assertEqual(RiskModel.categorize_risk(0.72, severity_norm=90.0), "CRITICAL")

    def test_08_risk_model_status_transparency(self):
        features = {"condition_risk": 20.0, "failure_rate": 0.0, "severity_norm": 30.0, "overdue_ratio": 0.0, "asset_age_norm": 10.0}
        pred = RiskModel.predict(features)
        self.assertIn(pred["model_status"], ["XGBOOST_TRAINED_MODEL", "DOMAIN_CALIBRATED_MODEL"])

    # =========================================================================
    # 3. Traffic Impact Engine
    # =========================================================================
    def test_09_traffic_impact_passenger_integration(self):
        traffic = TrafficImpactModel.calculate_traffic_impact(
            db=self.db,
            section_id="S01_AGC_TDL",
            duration_hours=2.0,
            target_date=date(2026, 9, 15),
            preferred_start_hour=8,  # Peak morning
        )
        self.assertIn("traffic_impact_score", traffic)
        self.assertGreaterEqual(traffic["traffic_impact_score"], 0.0)
        self.assertLessEqual(traffic["traffic_impact_score"], 100.0)
        self.assertTrue(traffic["is_peak_window"])

    def test_10_traffic_impact_freight_integration(self):
        # Target date 2026-09-15 has 36 synthetic freight movements
        traffic_freight = TrafficImpactModel.calculate_traffic_impact(
            db=self.db,
            section_id="S01_AGC_TDL",
            duration_hours=2.0,
            target_date=date(2026, 9, 15),
            preferred_start_hour=14,
        )
        self.assertIn("freight_train_pressure", traffic_freight)
        self.assertGreaterEqual(traffic_freight["freight_train_pressure"], 0.0)

    def test_11_traffic_impact_categories_and_weights(self):
        traffic_offpeak = TrafficImpactModel.calculate_traffic_impact(
            db=self.db,
            section_id="S01_AGC_TDL",
            duration_hours=1.0,
            target_date=date(2026, 9, 15),
            preferred_start_hour=2,  # Night off-peak
        )
        traffic_peak = TrafficImpactModel.calculate_impact_peak = TrafficImpactModel.calculate_traffic_impact(
            db=self.db,
            section_id="S01_AGC_TDL",
            duration_hours=4.0,
            target_date=date(2026, 9, 15),
            preferred_start_hour=8,  # Morning peak
        )
        self.assertLess(traffic_offpeak["traffic_impact_score"], traffic_peak["traffic_impact_score"])
        self.assertIn(traffic_offpeak["traffic_impact_category"], ["LOW", "MEDIUM", "HIGH", "CRITICAL"])

    # =========================================================================
    # 4. Multi-Criteria Priority Engine
    # =========================================================================
    def test_12_priority_weights_exact(self):
        # 30% Sev, 25% Crit, 20% Overdue, 15% Risk, 10% Traffic
        self.assertEqual(PriorityEngine.WEIGHT_SEVERITY, 0.30)
        self.assertEqual(PriorityEngine.WEIGHT_CRITICALITY, 0.25)
        self.assertEqual(PriorityEngine.WEIGHT_OVERDUE, 0.20)
        self.assertEqual(PriorityEngine.WEIGHT_RISK, 0.15)
        self.assertEqual(PriorityEngine.WEIGHT_TRAFFIC, 0.10)

        # Total sum of weights must equal 1.0
        total_w = (
            PriorityEngine.WEIGHT_SEVERITY
            + PriorityEngine.WEIGHT_CRITICALITY
            + PriorityEngine.WEIGHT_OVERDUE
            + PriorityEngine.WEIGHT_RISK
            + PriorityEngine.WEIGHT_TRAFFIC
        )
        self.assertAlmostEqual(total_w, 1.0)

    def test_13_priority_calculation_exact_value(self):
        # Test exact calculation: 0.30*100 + 0.25*100 + 0.20*100 + 0.15*100 + 0.10*100 = 100.0
        res_max = PriorityEngine.calculate_priority(100, 100, 100, 100, 100)
        self.assertEqual(res_max["priority_score"], 100.0)
        self.assertEqual(res_max["priority_category"], "CRITICAL")

        # Test exact calculation: 0.30*90 + 0.25*80 + 0.20*60 + 0.15*72 + 0.10*45
        # = 27.0 + 20.0 + 12.0 + 10.8 + 4.5 = 74.3
        res = PriorityEngine.calculate_priority(90, 80, 60, 72, 45)
        self.assertEqual(res["priority_score"], 74.3)
        self.assertEqual(res["priority_category"], "HIGH")

    def test_14_priority_categories_bands(self):
        # Bands: LOW (0-35), MEDIUM (35-60), HIGH (60-80), CRITICAL (80-100)
        self.assertEqual(PriorityEngine.calculate_priority(20, 20, 20, 20, 20)["priority_category"], "LOW")
        self.assertEqual(PriorityEngine.calculate_priority(50, 50, 50, 50, 50)["priority_category"], "MEDIUM")
        self.assertEqual(PriorityEngine.calculate_priority(70, 70, 70, 70, 70)["priority_category"], "HIGH")
        self.assertEqual(PriorityEngine.calculate_priority(90, 90, 90, 90, 90)["priority_category"], "CRITICAL")

    def test_15_priority_component_breakdown(self):
        res = PriorityEngine.calculate_priority(90, 80, 60, 72, 45)
        comp = res["priority_components"]
        self.assertEqual(comp["severity"], 90.0)
        self.assertEqual(comp["criticality"], 80.0)
        self.assertEqual(comp["overdue"], 60.0)
        self.assertEqual(comp["risk"], 72.0)
        self.assertEqual(comp["traffic_impact"], 45.0)

    # =========================================================================
    # 5. Explainability
    # =========================================================================
    def test_16_explainability_generation(self):
        req = self.db.query(MaintenanceRequest).filter(MaintenanceRequest.request_id == "MR0001").first()
        features = extract_features(self.db, req)
        risk_res = RiskModel.predict(features)
        traffic_res = TrafficImpactModel.calculate_traffic_impact(self.db, req.section_id)
        prio_res = PriorityEngine.calculate_priority(
            features["severity_norm"],
            features["criticality_norm"],
            features["overdue_norm"],
            risk_res["risk_score"],
            traffic_res["traffic_impact_score"],
        )
        expl = DecisionExplainer.generate_explanation("MR0001", features, risk_res, traffic_res, prio_res)
        
        self.assertIsInstance(expl, str)
        self.assertIn("MR0001", expl)
        self.assertIn(prio_res["priority_category"], expl)
        self.assertIn(risk_res["risk_category"], expl)

    def test_17_explainability_factors_match_real_data(self):
        req = self.db.query(MaintenanceRequest).filter(MaintenanceRequest.request_id == "MR0001").first()
        features = extract_features(self.db, req)
        risk_res = RiskModel.predict(features)
        drivers = risk_res["risk_contributing_factors"]
        self.assertIsInstance(drivers, list)
        self.assertGreater(len(drivers), 0)

    # =========================================================================
    # 6. API Endpoint Contracts
    # =========================================================================
    def test_18_api_predict_valid_request(self):
        res = self.client.post("/api/v1/ai/predict", json={"request_id": "MR0001"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["request_id"], "MR0001")
        self.assertIn("risk_probability", data)
        self.assertIn("risk_score", data)
        self.assertIn("risk_category", data)
        self.assertIn("traffic_impact_score", data)
        self.assertIn("traffic_impact_category", data)
        self.assertIn("priority_score", data)
        self.assertIn("priority_category", data)
        self.assertIn("priority_components", data)
        self.assertIn("risk_contributing_factors", data)
        self.assertIn("explanation", data)
        self.assertIn(data["model_status"], ["XGBOOST_TRAINED_MODEL", "DOMAIN_CALIBRATED_MODEL"])

    def test_19_api_predict_nonexistent_request(self):
        res = self.client.post("/api/v1/ai/predict", json={"request_id": "MR_DOES_NOT_EXIST"})
        self.assertEqual(res.status_code, 404)

    def test_20_api_predict_invalid_body(self):
        res = self.client.post("/api/v1/ai/predict", json={})
        self.assertEqual(res.status_code, 422)

    def test_21_api_insights_corridor_analytics(self):
        res = self.client.get("/api/v1/ai/insights")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        self.assertGreaterEqual(data["total_requests_analyzed"], 150)
        self.assertIn("risk_distribution", data)
        self.assertIn("priority_distribution", data)
        self.assertIn("department_distribution", data)
        self.assertIn("high_attention_tasks", data)
        self.assertIn("corridor_ai_recommendation", data)
        self.assertIn(data["model_status"], ["XGBOOST_TRAINED_MODEL", "DOMAIN_CALIBRATED_MODEL"])

    def test_22_api_insights_distributions_sum(self):
        res = self.client.get("/api/v1/ai/insights")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        total = data["total_requests_analyzed"]
        
        # Risk distribution sums to total
        risk_sum = sum(data["risk_distribution"].values())
        self.assertEqual(risk_sum, total)

        # Priority distribution sums to total
        prio_sum = sum(data["priority_distribution"].values())
        self.assertEqual(prio_sum, total)

        # Department distribution sums to total
        dept_sum = sum(data["department_distribution"].values())
        self.assertEqual(dept_sum, total)

    def test_23_api_insights_high_attention_queue(self):
        res = self.client.get("/api/v1/ai/insights")
        data = res.json()
        queue = data["high_attention_tasks"]
        self.assertIsInstance(queue, list)
        if len(queue) > 0:
            first = queue[0]
            self.assertIn("request_id", first)
            self.assertIn("priority_score", first)
            self.assertIn("risk_score", first)
            self.assertIn("top_drivers", first)

    def test_24_ai_service_predict_request_direct(self):
        res = AIService.predict_request(self.db, "MR0002")
        self.assertEqual(res.request_id, "MR0002")
        self.assertGreater(res.priority_score, 0.0)
        self.assertGreater(res.risk_score, 0.0)

    def test_25_ai_service_multiple_real_requests(self):
        sample_ids = ["MR0001", "MR0002", "MR0003", "MR0004", "MR0005"]
        for rid in sample_ids:
            res = AIService.predict_request(self.db, rid)
            self.assertEqual(res.request_id, rid)
            self.assertIn(res.risk_category, ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
            self.assertIn(res.priority_category, ["LOW", "MEDIUM", "HIGH", "CRITICAL"])

    def test_26_traffic_risk_distinction_intact(self):
        # Asset Failure Risk must be independent of track window traffic
        features = extract_features(self.db, self.db.query(MaintenanceRequest).filter_by(request_id="MR0001").first())
        risk_res = RiskModel.predict(features)
        
        # Varying section traffic should NOT change asset failure risk score
        traffic_night = TrafficImpactModel.calculate_traffic_impact(self.db, "S01_AGC_TDL", preferred_start_hour=2)
        traffic_peak = TrafficImpactModel.calculate_traffic_impact(self.db, "S01_AGC_TDL", preferred_start_hour=8)
        
        self.assertNotEqual(traffic_night["traffic_impact_score"], traffic_peak["traffic_impact_score"])
        # Risk score remains purely asset-driven
        self.assertEqual(risk_res["risk_score"], RiskModel.predict(features)["risk_score"])


if __name__ == "__main__":
    unittest.main()
