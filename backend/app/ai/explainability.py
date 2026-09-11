"""
PlanRail Explainability & Controller Audit Engine
=================================================

Generates human-readable, auditable diagnostic explanations for railway controllers,
correlating risk factors, traffic impact, and multi-criteria priority weightings.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class DecisionExplainer:
    """
    Controller Explainability Engine generating transparent rationales.
    """

    @classmethod
    def generate_explanation(
        cls,
        request_id: str,
        features: Dict[str, Any],
        risk_result: Dict[str, Any],
        traffic_result: Dict[str, Any],
        priority_result: Dict[str, Any],
    ) -> str:
        """
        Creates a structured, controller-ready summary briefing for a maintenance request.
        """
        department = features.get("department", "ENGINEERING")
        asset_type = features.get("asset_type", "ASSET")
        section_id = features.get("section_id", "CORRIDOR")
        priority_cat = priority_result.get("priority_category", "MEDIUM")
        priority_score = priority_result.get("priority_score", 50.0)
        risk_cat = risk_result.get("risk_category", "MEDIUM")
        risk_score = risk_result.get("risk_score", 50.0)
        traffic_cat = traffic_result.get("traffic_impact_category", "LOW")

        # Top priority drivers
        components = priority_result.get("priority_components", {})
        top_components = sorted(components.items(), key=lambda x: x[1], reverse=True)
        top_driver_name, top_driver_val = top_components[0] if top_components else ("severity", 50.0)

        # Build concise audit summary
        risk_drivers = risk_result.get("risk_contributing_factors", [])
        risk_text = "; ".join(risk_drivers[:2]) if risk_drivers else "Nominal operational parameters."

        summary = (
            f"Maintenance {request_id} ({department} - {asset_type} on {section_id}) "
            f"evaluated as {priority_cat} priority (score {priority_score:.1f}/100) "
            f"with {risk_cat} asset failure risk ({risk_score:.1f}/100). "
            f"Primary priority driver is {top_driver_name.replace('_', ' ').title()} ({top_driver_val:.1f}/100). "
            f"Risk factors: {risk_text}. "
            f"Operational traffic impact is {traffic_cat} ({traffic_result.get('traffic_impact_score', 0.0):.1f}/100)."
        )

        return summary
