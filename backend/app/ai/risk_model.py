"""
PlanRail Asset Predictive Failure Risk Model
===========================================

Executes trained XGBoost ML failure risk prediction with SHAP explainability.
Trained artifact: backend/app/ai/models/cleaned_risk_model_xgb.joblib
Calibrated threshold: 0.5684 (optimized for high critical recall).
Categorizes risk into LOW, MEDIUM, HIGH, and CRITICAL bands.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Canonical 11-feature contract expected by the trained XGBoost model
RISK_FEATURE_COLUMNS = [
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

DEFAULT_THRESHOLD = 0.5684
CALIBRATED_RISK_THRESHOLD = DEFAULT_THRESHOLD

FEATURE_METADATA: Dict[str, Dict[str, str]] = {
    "condition_score": {"name": "Structural Condition", "unit": "/100"},
    "severity": {"name": "Defect Severity Rating", "unit": "/10"},
    "criticality": {"name": "Asset Operational Criticality", "unit": "/10"},
    "overdue_days": {"name": "Inspection Overdue Days", "unit": "days"},
    "historical_failures": {"name": "Historical Failure Frequency", "unit": "incidents"},
    "train_density": {"name": "Passenger Train Density", "unit": "trains/day"},
    "freight_train_density": {"name": "Freight Movement Volume", "unit": "freight/day"},
    "freight_share_percent": {"name": "Freight Traffic Share", "unit": "%"},
    "asset_age": {"name": "Asset Operating Age", "unit": "years"},
    "maintenance_frequency": {"name": "Maintenance Frequency", "unit": "months"},
    "previous_defects": {"name": "Past Defect Frequency", "unit": "defects"},
}


class RiskModel:
    """
    XGBoost ML Risk Prediction Model with lazy singleton loading and SHAP explainability.
    """

    _model: Any = None
    _threshold: float = DEFAULT_THRESHOLD
    _feature_columns: List[str] = RISK_FEATURE_COLUMNS
    _metrics: Dict[str, Any] = {}
    _explainer: Any = None
    _is_loaded: bool = False
    _load_error: Optional[str] = None

    MODEL_TYPE = "XGBOOST_GRADIENT_BOOSTING_CLASSIFIER"
    MODEL_STATUS = "XGBOOST_TRAINED_MODEL"
    CALIBRATED_THRESHOLD = DEFAULT_THRESHOLD

    @classmethod
    def _resolve_model_path(cls) -> Path:
        """Resolves model path relative to project root or current module."""
        current_dir = Path(__file__).resolve().parent
        candidate_paths = [
            current_dir / "models" / "cleaned_risk_model_xgb.joblib",
            current_dir.parent.parent / "app" / "ai" / "models" / "cleaned_risk_model_xgb.joblib",
            Path("/Users/arpitbhardwaj/Desktop/PlanRail/backend/app/ai/models/cleaned_risk_model_xgb.joblib"),
        ]
        for p in candidate_paths:
            if p.exists():
                return p
        return candidate_paths[0]

    @classmethod
    def load_model(cls) -> bool:
        """Loads trained XGBoost model and threshold from joblib artifact."""
        if cls._is_loaded and cls._model is not None:
            return True

        model_path = cls._resolve_model_path()
        if not model_path.exists():
            cls._load_error = f"Model artifact not found at: {model_path}"
            logger.warning(cls._load_error)
            return False

        try:
            import joblib
            saved_bundle = joblib.load(str(model_path))

            if isinstance(saved_bundle, dict):
                cls._model = saved_bundle.get("model")
                cls._threshold = float(saved_bundle.get("optimal_threshold", DEFAULT_THRESHOLD))
                cls._feature_columns = saved_bundle.get("feature_columns", RISK_FEATURE_COLUMNS)
                cls._metrics = saved_bundle.get("metrics", {})
            else:
                cls._model = saved_bundle
                cls._threshold = DEFAULT_THRESHOLD
                cls._feature_columns = RISK_FEATURE_COLUMNS

            cls._is_loaded = True
            cls._load_error = None
            logger.info(
                f"[RiskModel] Successfully loaded XGBoost model from {model_path.name} "
                f"(features={len(cls._feature_columns)}, threshold={cls._threshold:.4f})"
            )
            return True
        except Exception as err:
            cls._load_error = f"Failed to load XGBoost model: {err}"
            logger.error(cls._load_error, exc_info=True)
            return False

    @classmethod
    def _build_feature_dataframe(cls, features: Dict[str, Any]) -> pd.DataFrame:
        """Constructs a single-row DataFrame matching the 11 feature columns in exact order."""
        # Condition score
        cond = features.get("condition_score", features.get("raw_condition_score"))
        if cond is None and "condition_risk" in features:
            cond = 100.0 - float(features["condition_risk"])
        if cond is None:
            cond = 75.0

        # Severity (1-10)
        sev = features.get("severity", features.get("raw_severity"))
        if sev is None and "severity_norm" in features:
            sev = float(features["severity_norm"]) / 10.0
        if sev is None:
            sev = 5.0
        if sev > 10.0:
            sev = sev / 10.0

        # Criticality (1-10)
        crit = features.get("criticality", features.get("raw_criticality"))
        if crit is None and "criticality_norm" in features:
            crit = float(features["criticality_norm"]) / 10.0
        if crit is None:
            crit = 5.0
        if crit > 10.0:
            crit = crit / 10.0

        # Overdue days (0-60)
        ovd = features.get("overdue_days", features.get("raw_overdue_days"))
        if ovd is None and "overdue_norm" in features:
            ovd = float(features["overdue_norm"]) * 0.6
        if ovd is None:
            ovd = 0.0

        # Historical failures
        hf = features.get("historical_failures", features.get("historical_event_count"))
        if hf is None and "failure_rate" in features:
            hf = float(features["failure_rate"]) / 12.0
        if hf is None:
            hf = 0.0

        # Asset age
        age = features.get("asset_age", features.get("asset_age_years"))
        if age is None and "asset_age_norm" in features:
            age = float(features["asset_age_norm"]) * 0.3
        if age is None:
            age = 10.0

        row_dict = {
            "condition_score": max(10.0, min(100.0, float(cond))),
            "severity": max(1.0, min(10.0, float(sev))),
            "criticality": max(1.0, min(10.0, float(crit))),
            "overdue_days": max(0.0, float(ovd)),
            "historical_failures": max(0.0, float(hf)),
            "train_density": float(features.get("train_density", 55.0)),
            "freight_train_density": float(features.get("freight_train_density", 50.0)),
            "freight_share_percent": float(features.get("freight_share_percent", 48.0)),
            "asset_age": max(1.0, float(age)),
            "maintenance_frequency": float(features.get("maintenance_frequency", 6.0)),
            "previous_defects": float(features.get("previous_defects", hf)),
        }
        return pd.DataFrame([row_dict])[cls._feature_columns]

    @classmethod
    def compute_risk_probability(cls, features: Dict[str, Any]) -> float:
        """
        Runs XGBoost inference or calibrated domain fallback.
        """
        if cls.load_model() and cls._model is not None:
            try:
                df = cls._build_feature_dataframe(features)
                prob = float(cls._model.predict_proba(df)[0, 1])
                return round(prob, 4)
            except Exception as err:
                logger.warning(f"[RiskModel] Inference error, falling back to calibration: {err}")

        # Domain-calibrated fallback if ML runtime is unavailable
        condition_risk = features.get("condition_risk", 25.0)
        failure_rate = features.get("failure_rate", 10.0)
        severity_norm = features.get("severity_norm", 50.0)
        overdue_ratio = features.get("overdue_ratio", 20.0)
        asset_age_norm = features.get("asset_age_norm", 30.0)

        raw_score = (
            0.35 * condition_risk
            + 0.25 * failure_rate
            + 0.20 * severity_norm
            + 0.12 * overdue_ratio
            + 0.08 * asset_age_norm
        )
        p = max(0.01, min(0.99, raw_score / 100.0))
        return round(p, 4)

    @classmethod
    def categorize_risk(cls, probability: float, severity_norm: float = 50.0) -> str:
        """
        Assigns risk category based on trained optimal threshold and domain boundaries:
          - P >= 0.80 or (P >= 0.70 and severity >= 80): CRITICAL
          - P >= 0.70 or (P >= threshold and severity >= 65): HIGH
          - 0.30 <= P < 0.70: MEDIUM
          - P < 0.30: LOW
        """
        threshold = cls._threshold
        if probability >= 0.80 or (probability >= 0.70 and severity_norm >= 80.0):
            return "CRITICAL"
        elif probability >= 0.70 or (probability >= threshold and severity_norm >= 65.0):
            return "HIGH"
        elif probability >= 0.30:
            return "MEDIUM"
        else:
            return "LOW"

    @classmethod
    def compute_shap_importances(cls, features: Dict[str, Any]) -> Dict[str, float]:
        """Computes real TreeExplainer SHAP values for the given feature vector."""
        if not cls.load_model() or cls._model is None:
            return {}

        try:
            import shap
            if cls._explainer is None:
                cls._explainer = shap.TreeExplainer(cls._model)

            df = cls._build_feature_dataframe(features)
            shap_vals = cls._explainer.shap_values(df)
            if isinstance(shap_vals, list):
                shap_vals = shap_vals[1] if len(shap_vals) > 1 else shap_vals[0]
            if len(shap_vals.shape) > 1:
                vals = shap_vals[0]
            else:
                vals = shap_vals

            return {col: round(float(val), 4) for col, val in zip(cls._feature_columns, vals)}
        except Exception as err:
            logger.debug(f"[RiskModel] SHAP computation fallback: {err}")
            return {}

    @classmethod
    def get_feature_contributions(
        cls, features: Dict[str, Any], shap_dict: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Builds structured feature contributions for each of the 11 features with SHAP impact.
        """
        contributions: List[Dict[str, Any]] = []
        feature_df = cls._build_feature_dataframe(features)

        for col in cls._feature_columns:
            val = float(feature_df[col].iloc[0])
            shap_val = float(shap_dict.get(col, 0.0))
            meta = FEATURE_METADATA.get(col, {"name": col.replace("_", " ").title(), "unit": ""})
            f_name = meta["name"]

            if shap_val > 0.005:
                impact = "INCREASES_RISK"
                direction_str = "Increases risk"
            elif shap_val < -0.005:
                impact = "DECREASES_RISK"
                direction_str = "Decreases risk"
            else:
                impact = "NEUTRAL"
                direction_str = "Neutral"

            contributions.append({
                "feature": col,
                "feature_name": f_name,
                "feature_value": round(val, 2),
                "contribution": round(shap_val, 4),
                "impact": impact,
                "display_text": f"{shap_val:+.3f} ({direction_str})",
            })

        contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
        return contributions

    @classmethod
    def get_risk_drivers(
        cls, features: Dict[str, Any], shap_dict: Optional[Dict[str, float]] = None
    ) -> List[str]:
        """Identifies top contributing risk factors based on SHAP importances and feature values."""
        drivers: List[str] = []

        if shap_dict:
            sorted_shap = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)
            feature_df = cls._build_feature_dataframe(features)

            for feat, val in sorted_shap:
                if abs(val) < 0.005:
                    continue
                meta = FEATURE_METADATA.get(feat, {"name": feat.replace("_", " ").title(), "unit": ""})
                f_name = meta["name"]
                f_val = float(feature_df[feat].iloc[0])
                unit = meta.get("unit", "")
                val_str = f"{f_val:.1f}{unit}" if unit else f"{f_val:.1f}"

                if val > 0:
                    drivers.append(f"{f_name} ({val_str}, SHAP +{val:.3f} — increases risk)")
                else:
                    drivers.append(f"{f_name} ({val_str}, SHAP {val:.3f} — decreases risk)")

                if len(drivers) >= 4:
                    break

        if not drivers:
            # Domain-based driver extraction fallback
            condition_risk = features.get("condition_risk", 0.0)
            raw_cond = features.get("raw_condition_score", 100.0)
            if condition_risk >= 30.0:
                drivers.append(f"Structural condition degradation (score: {raw_cond:.1f}/100 — increases risk)")

            historical_count = features.get("historical_event_count", 0)
            if historical_count > 0:
                drivers.append(f"Elevated historical failure frequency ({historical_count} past incident{'s' if historical_count != 1 else ''} — increases risk)")

            severity = features.get("raw_severity", 50.0)
            if severity >= 70.0:
                drivers.append(f"High defect severity rating ({severity:.1f}/100 — increases risk)")

            overdue_days = features.get("raw_overdue_days", 0)
            if overdue_days > 0:
                drivers.append(f"Overdue inspection maintenance ({overdue_days} days past schedule — increases risk)")

        if not drivers:
            return ["Asset operating within nominal risk boundaries."]

        return drivers[:4]

    @classmethod
    def predict(cls, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs full inference on extracted features.
        """
        prob = cls.compute_risk_probability(features)
        score = round(prob * 100.0, 2)
        severity_norm = features.get("severity_norm", 50.0)
        category = cls.categorize_risk(prob, severity_norm)
        shap_dict = cls.compute_shap_importances(features)
        drivers = cls.get_risk_drivers(features, shap_dict)
        contributions = cls.get_feature_contributions(features, shap_dict)

        status_str = cls.MODEL_STATUS if cls._is_loaded else "DOMAIN_CALIBRATED_MODEL"

        return {
            "risk_probability": prob,
            "risk_score": score,
            "risk_category": category,
            "risk_contributing_factors": drivers,
            "feature_contributions": contributions,
            "shap_values": shap_dict,
            "model_status": status_str,
            "calibrated_threshold": cls._threshold,
            "model_metrics": cls._metrics,
        }

