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
        Extracts features prioritizing the 6 core signals: 
        Provider_ID, Claim_Amount, Procedure_Code, Diagnosis_Code, Patient_Age, Patient_Gender.
        """
        # Core 6 features (Critical)
        core_data = {
            "Provider_ID": hash(str(claim_data.get("provider_id", "Unknown"))) % 1000,
            "Claim_Amount": float(claim_data.get("total_amount", 0.0)),
            "Procedure_Code": hash(str(claim_data.get("procedure", "Unknown"))) % 1000,
            "Diagnosis_Code": hash(str(claim_data.get("diagnosis", "Unknown"))) % 1000,
            "Patient_Age": float(claim_data.get("patient_age", 45.0)),
            "Patient_Gender": hash(str(claim_data.get("gender", "U"))) % 2,
        }

        # Secondary 13 features (Imputed if missing)
        secondary_data = {
            "Approved_Amount": float(claim_data.get("approved_amount", core_data["Claim_Amount"] * 0.9)),
            "Insurance_Type": hash(str(claim_data.get("insurance", "Other"))) % 4,
            "Days_Between_Service_and_Claim": int(claim_data.get("days_since_service", 10)),
            "Number_of_Claims_Per_Provider_Monthly": int(claim_data.get("provider_monthly_volume", 50)),
            "Provider_Specialty": hash(str(claim_data.get("specialty", "Unknown"))) % 20,
            "Patient_State": hash(str(claim_data.get("state", "Unknown"))) % 50,
            "Claim_Status": 1,
            "Length_of_Stay": int(claim_data.get("stay_length", 0)),
            "Visit_Type": hash(str(claim_data.get("visit_type", "Unknown"))) % 3,
            "Chronic_Condition_Flag": 1 if claim_data.get("has_chronic", False) else 0,
            "Prior_Visits_12m": int(claim_data.get("prior_visits", 2)),
            "Submission_Month": datetime.now().month,
            "Submission_DayOfWeek": datetime.now().weekday()
        }
        
        # Merge into the exact 19-feature order expected by the model
        data = {
            "Provider_ID": core_data["Provider_ID"],
            "Patient_Age": core_data["Patient_Age"],
            "Patient_Gender": core_data["Patient_Gender"],
            "Diagnosis_Code": core_data["Diagnosis_Code"],
            "Procedure_Code": core_data["Procedure_Code"],
            "Claim_Amount": core_data["Claim_Amount"],
            "Approved_Amount": secondary_data["Approved_Amount"],
            "Insurance_Type": secondary_data["Insurance_Type"],
            "Days_Between_Service_and_Claim": secondary_data["Days_Between_Service_and_Claim"],
            "Number_of_Claims_Per_Provider_Monthly": secondary_data["Number_of_Claims_Per_Provider_Monthly"],
            "Provider_Specialty": secondary_data["Provider_Specialty"],
            "Patient_State": secondary_data["Patient_State"],
            "Claim_Status": secondary_data["Claim_Status"],
            "Length_of_Stay": secondary_data["Length_of_Stay"],
            "Visit_Type": secondary_data["Visit_Type"],
            "Chronic_Condition_Flag": secondary_data["Chronic_Condition_Flag"],
            "Prior_Visits_12m": secondary_data["Prior_Visits_12m"],
            "Submission_Month": secondary_data["Submission_Month"],
            "Submission_DayOfWeek": secondary_data["Submission_DayOfWeek"]
        }
        
        return pd.DataFrame([data])

    def _run_heuristics(self, claim_data: Dict[str, Any]) -> float:
        amount = float(claim_data.get("total_amount", 0))
        if amount > 50000:
            return 0.95
        return 0.1

    def _calculate_confidence(self, score: float, claim_data: Dict[str, Any]) -> float:
        """
        Confidence is weighted heavily towards the 6 core features.
        """
        core_fields = ["total_amount", "provider_id", "diagnosis", "procedure", "patient_age", "gender"]
        provided_core = sum(1 for field in core_fields if field in claim_data and claim_data[field] is not None)
        
        # If any core feature is missing, confidence drops sharply
        core_completeness = provided_core / len(core_fields)
        
        return round(0.95 * core_completeness, 2)
