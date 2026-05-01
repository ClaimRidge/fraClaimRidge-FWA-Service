import xgboost as xgb
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import joblib
import os
from datetime import datetime
from src.config import settings

class Layer1AnomalyDetector:
    def __init__(self, model_path: Optional[str] = None):
        self.model = self._load_model(model_path)
        self.encoders = self._load_encoders()
        self.threshold = settings.L1_ANOMALY_THRESHOLD

    def _load_model(self, model_path: Optional[str]):
        # Default to the .xgb champion model
        path = model_path or "models/fixtures/layer1_anomaly_v1.xgb"
        if os.path.exists(path):
            model = xgb.XGBClassifier()
            model.load_model(path)
            return model
        return None

    def _load_encoders(self):
        path = "models/fixtures/label_encoders.pkl"
        if os.path.exists(path):
            return joblib.load(path)
        return {}

    async def predict(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs inference on a single claim using the trained XGBoost model.
        """
        features_df = self._extract_features(claim_data)
        
        if self.model:
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
        Extracts the 6 core features and encodes them using saved LabelEncoders.
        """
        raw_data = {
            "Provider_ID": str(claim_data.get("provider_id", "Unknown")),
            "Claim_Amount": float(claim_data.get("total_amount", 0.0)),
            "Procedure_Code": str(claim_data.get("procedure", "Unknown")),
            "Diagnosis_Code": str(claim_data.get("diagnosis", "Unknown")),
            "Patient_Age": float(claim_data.get("patient_age", 45.0)),
            "Patient_Gender": str(claim_data.get("gender", "U")),
        }

        # Apply Encoders
        encoded_data = {}
        categorical_cols = ['Provider_ID', 'Procedure_Code', 'Diagnosis_Code', 'Patient_Gender']
        
        for col in categorical_cols:
            val = raw_data[col]
            if col in self.encoders:
                le = self.encoders[col]
                # Handle unseen labels by falling back to 'Unknown'
                if val not in le.classes_:
                    val = 'Unknown' if 'Unknown' in le.classes_ else le.classes_[0]
                encoded_data[col] = le.transform([val])[0]
            else:
                encoded_data[col] = 0 # Fallback if encoder missing
        
        # Merge all features
        data = {
            "Provider_ID": encoded_data["Provider_ID"],
            "Claim_Amount": raw_data["Claim_Amount"],
            "Procedure_Code": encoded_data["Procedure_Code"],
            "Diagnosis_Code": encoded_data["Diagnosis_Code"],
            "Patient_Age": raw_data["Patient_Age"],
            "Patient_Gender": encoded_data["Patient_Gender"],
        }
        
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
