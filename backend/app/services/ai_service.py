"""
PlanRail AI Service
===================

Orchestrates the end-to-end AI Decision-Support Pipeline:
  Maintenance Request -> Feature Extraction -> Risk Prediction -> Traffic Disruption -> Multi-Criteria Priority -> Explainability
Provides both single-request inference and corridor-level aggregated insights.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.explainability import DecisionExplainer
from app.ai.features import extract_features
from app.ai.priority_engine import PriorityEngine
from app.ai.risk_model import RiskModel
from app.ai.traffic_impact import TrafficImpactModel
from app.models.maintenance import MaintenanceRequest
from app.schemas.domain import AIPredictResponse

logger = logging.getLogger(__name__)


class AIService:
    @staticmethod
    def predict_request(db: Session, request_id: str) -> AIPredictResponse:
        """
        Executes full AI inference pipeline for a single maintenance request.
        """
        clean_id = str(request_id).strip()
        request = (
            db.query(MaintenanceRequest)
            .filter(MaintenanceRequest.request_id == clean_id)
            .first()
        )

        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Maintenance request '{clean_id}' not found in corridor database.",
            )

        # 1. Feature Engineering
        features = extract_features(db, request)

        # 2. Asset Failure Risk Prediction
        risk_result = RiskModel.predict(features)

        # 3. Traffic Disruption Impact
        traffic_result = TrafficImpactModel.calculate_traffic_impact(
            db=db,
            section_id=request.section_id,
            duration_hours=float(request.duration_hours or 2.0),
        )

        # 4. Multi-Criteria Priority Engine
        priority_result = PriorityEngine.calculate_priority(
            severity_norm=features["severity_norm"],
            criticality_norm=features["criticality_norm"],
            overdue_norm=features["overdue_norm"],
            risk_score=risk_result["risk_score"],
            traffic_impact_score=traffic_result["traffic_impact_score"],
        )

        # 5. Explainability & Controller Audit Briefing
        explanation = DecisionExplainer.generate_explanation(
            request_id=clean_id,
            features=features,
            risk_result=risk_result,
            traffic_result=traffic_result,
            priority_result=priority_result,
        )

        return AIPredictResponse(
            request_id=clean_id,
            risk_probability=risk_result["risk_probability"],
            risk_score=risk_result["risk_score"],
            risk_category=risk_result["risk_category"],
            traffic_impact_score=traffic_result["traffic_impact_score"],
            traffic_impact_category=traffic_result["traffic_impact_category"],
            priority_score=priority_result["priority_score"],
            priority_category=priority_result["priority_category"],
            priority_components=priority_result["priority_components"],
            risk_contributing_factors=risk_result["risk_contributing_factors"],
            explanation=explanation,
            model_status=risk_result["model_status"],
        )

    @staticmethod
    def get_corridor_insights(db: Session) -> Dict[str, Any]:
        """
        Aggregates corridor-wide AI analytics across all active maintenance requests.
        """
        requests = db.query(MaintenanceRequest).all()

        risk_distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        priority_distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        department_distribution: Dict[str, int] = defaultdict(int)

        high_attention_tasks: List[Dict[str, Any]] = []

        for req in requests:
            features = extract_features(db, req)
            risk_res = RiskModel.predict(features)
            traffic_res = TrafficImpactModel.calculate_traffic_impact(
                db=db,
                section_id=req.section_id,
                duration_hours=float(req.duration_hours or 2.0),
            )
            prio_res = PriorityEngine.calculate_priority(
                severity_norm=features["severity_norm"],
                criticality_norm=features["criticality_norm"],
                overdue_norm=features["overdue_norm"],
                risk_score=risk_res["risk_score"],
                traffic_impact_score=traffic_res["traffic_impact_score"],
            )

            # Record distributions
            risk_cat = risk_res["risk_category"]
            prio_cat = prio_res["priority_category"]

            risk_distribution[risk_cat] = risk_distribution.get(risk_cat, 0) + 1
            priority_distribution[prio_cat] = priority_distribution.get(prio_cat, 0) + 1
            dept = req.department or "GENERAL"
            department_distribution[dept] += 1

            # High priority / High risk queue
            if prio_cat in ["CRITICAL", "HIGH"] or risk_cat in ["CRITICAL", "HIGH"]:
                high_attention_tasks.append({
                    "request_id": req.request_id,
                    "asset_id": req.asset_id,
                    "section_id": req.section_id,
                    "department": req.department,
                    "asset_type": req.asset_type or "ASSET",
                    "priority_score": prio_res["priority_score"],
                    "priority_category": prio_cat,
                    "risk_score": risk_res["risk_score"],
                    "risk_category": risk_cat,
                    "traffic_impact_score": traffic_res["traffic_impact_score"],
                    "traffic_impact_category": traffic_res["traffic_impact_category"],
                    "overdue_days": req.overdue_days,
                    "duration_hours": req.duration_hours,
                    "top_drivers": risk_res["risk_contributing_factors"][:2],
                })

        # Sort queue by priority score descending
        high_attention_tasks.sort(key=lambda x: x["priority_score"], reverse=True)

        # Dynamic AI Recommendation based on real data
        crit_count = priority_distribution["CRITICAL"]
        high_count = priority_distribution["HIGH"]
        total = len(requests)

        if crit_count > 0:
            ai_recommendation = (
                f"Urgent operational attention required: {crit_count} CRITICAL and {high_count} HIGH priority "
                f"maintenance requests identified across {len(department_distribution)} departments. "
                f"Prioritize bundling high-risk track possessions in low-traffic off-peak windows."
            )
        elif high_count > 0:
            ai_recommendation = (
                f"Proactive corridor maintenance alert: {high_count} HIGH priority maintenance tasks pending. "
                f"Coordinate multi-department work to minimize line closures during heavy freight and passenger movement windows."
            )
        else:
            ai_recommendation = (
                f"Corridor maintenance state is stable with {total} total requests operating within nominal thresholds. "
                f"Scheduled routine maintenance can proceed in standard maintenance windows."
            )

        return {
            "total_requests_analyzed": total,
            "risk_distribution": risk_distribution,
            "priority_distribution": priority_distribution,
            "department_distribution": dict(department_distribution),
            "high_attention_tasks": high_attention_tasks,
            "corridor_ai_recommendation": ai_recommendation,
            "model_status": RiskModel.MODEL_STATUS,
        }
