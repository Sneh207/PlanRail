"""
PlanRail Multi-Criteria Priority Intelligence Engine
====================================================

Harmonizes multi-source operational criteria into a transparent 0-100 priority score:
  - Severity (30%)
  - Criticality (25%)
  - Overdue (20%)
  - Risk (15%)
  - Traffic Disruption Impact (10%)
"""

from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class PriorityEngine:
    """
    Multi-Criteria Priority Engine for Railway Maintenance Decision Support.
    """

    # Authoritative weights from BACKEND_README.md
    WEIGHT_SEVERITY = 0.30
    WEIGHT_CRITICALITY = 0.25
    WEIGHT_OVERDUE = 0.20
    WEIGHT_RISK = 0.15
    WEIGHT_TRAFFIC = 0.10

    @classmethod
    def calculate_priority(
        cls,
        severity_norm: float,
        criticality_norm: float,
        overdue_norm: float,
        risk_score: float,
        traffic_impact_score: float,
    ) -> Dict[str, Any]:
        """
        Calculates normalized multi-criteria priority score and category.
        """
        # Clamp inputs to [0.0, 100.0]
        s = max(0.0, min(100.0, float(severity_norm)))
        c = max(0.0, min(100.0, float(criticality_norm)))
        o = max(0.0, min(100.0, float(overdue_norm)))
        r = max(0.0, min(100.0, float(risk_score)))
        t = max(0.0, min(100.0, float(traffic_impact_score)))

        priority_score = (
            cls.WEIGHT_SEVERITY * s
            + cls.WEIGHT_CRITICALITY * c
            + cls.WEIGHT_OVERDUE * o
            + cls.WEIGHT_RISK * r
            + cls.WEIGHT_TRAFFIC * t
        )
        priority_score = round(max(0.0, min(100.0, priority_score)), 2)

        # Categorization bands from BACKEND_README.md
        if priority_score >= 80.0:
            category = "CRITICAL"
        elif priority_score >= 60.0:
            category = "HIGH"
        elif priority_score >= 35.0:
            category = "MEDIUM"
        else:
            category = "LOW"

        return {
            "priority_score": priority_score,
            "priority_category": category,
            "priority_components": {
                "severity": round(s, 2),
                "criticality": round(c, 2),
                "overdue": round(o, 2),
                "risk": round(r, 2),
                "traffic_impact": round(t, 2),
            },
            "component_contributions": {
                "severity_weighted": round(cls.WEIGHT_SEVERITY * s, 2),
                "criticality_weighted": round(cls.WEIGHT_CRITICALITY * c, 2),
                "overdue_weighted": round(cls.WEIGHT_OVERDUE * o, 2),
                "risk_weighted": round(cls.WEIGHT_RISK * r, 2),
                "traffic_weighted": round(cls.WEIGHT_TRAFFIC * t, 2),
            },
        }
