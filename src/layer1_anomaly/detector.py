import xgboost as xgb
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import os
import json
from datetime import datetime
from src.config import settings

class Layer1AnomalyDetector:
    def __init__(self, model_path: Optional[str] = None):
        self.model = self._load_model(model_path)
        self.threshold = settings.L1_ANOMALY_THRESHOLD

    def _load_model(self, model_path: Optional[str]):
        # Default to the .xgb champion model if no path provided
        path = model_path or "models/fixtures/layer1_anomaly_v1.xgb"
        
        if os.path.exists(path):
            model = xgb.XGBClassifier()
            model.load_model(path)
            return model
        return None

    async def predict(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs inference on a single claim using the trained XGBoost model.
        """
        features_df = self._extract_features(claim_data)
        
        if self.model:
            # XGBoost expects a DMatrix or a DataFrame with specific column names
            # We use the DataFrame approach for convenience
            score = float(self.model.predict_proba(features_df)[0][1])
        else:
            score = self._run_heuristics(claim_data)

        confidence = self._calculate_confidence(score, claim_data)
        
        return {
            "score": score,
            "confidence": confidence,
            "is_anomaly": score > self.threshold,
            "features_used": list(features_df.columns)
        }

    def _extract_features(self, claim_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Extracts ONLY the 6 core features that the model was trained on.
        """
        data = {
            "Provider_ID": hash(str(claim_data.get("provider_id", "Unknown"))) % 1000,
            "Claim_Amount": float(claim_data.get("total_amount", 0.0)),
            "Procedure_Code": hash(str(claim_data.get("procedure", "Unknown"))) % 1000,
            "Diagnosis_Code": hash(str(claim_data.get("diagnosis", "Unknown"))) % 1000,
            "Patient_Age": float(claim_data.get("patient_age", 45.0)),
            "Patient_Gender": hash(str(claim_data.get("gender", "U"))) % 2,
        }
        
        # Order MUST match the training feature set
        feature_order = ['Provider_ID', 'Claim_Amount', 'Procedure_Code', 'Diagnosis_Code', 'Patient_Age', 'Patient_Gender']
        df = pd.DataFrame([data])
        return df[feature_order]

    def _run_heuristics(self, claim_data: Dict[str, Any]) -> float:
        amount = float(claim_data.get("total_amount", 0))
        if amount > 50000:
            return 0.95
        return 0.1

    def _calculate_confidence(self, score: float, claim_data: Dict[str, Any]) -> float:
        """
        Confidence is based on the presence of the 6 core features.
        """
        core_fields = ["total_amount", "provider_id", "diagnosis", "procedure", "patient_age", "gender"]
        provided_core = sum(1 for field in core_fields if field in claim_data and claim_data[field] is not None)
        
        return round(0.98 * (provided_core / len(core_fields)), 2)
