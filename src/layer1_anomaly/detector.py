import xgboost as xgb
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import os
import json
from src.config import settings

class Layer1AnomalyDetector:
    def __init__(self, model_path: Optional[str] = None):
        self.model = self._load_model(model_path)
        self.threshold = settings.L1_ANOMALY_THRESHOLD

    def _load_model(self, model_path: Optional[str]):
        # In a real production app, this would fetch from MLflow
        # For now, we load a local stub or initialize a dummy
        if model_path and os.path.exists(model_path):
            model = xgb.XGBClassifier()
            model.load_model(model_path)
            return model
        else:
            # Fallback/Dummy logic for demonstration
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
        Extracts and prepares features in the exact format the model was trained on.
        """
        # Mapping incoming ClaimBridge fields to Kaggle dataset fields
        # MUST MATCH TRAINING FEATURE ORDER EXACTLY:
        # ['Provider_ID', 'Patient_Age', 'Patient_Gender', 'Diagnosis_Code', 'Procedure_Code', 
        #  'Claim_Amount', 'Approved_Amount', 'Insurance_Type', 'Days_Between_Service_and_Claim', 
        #  'Number_of_Claims_Per_Provider_Monthly', 'Provider_Specialty', 'Patient_State', 
        #  'Claim_Status', 'Length_of_Stay', 'Visit_Type', 'Chronic_Condition_Flag', 
        #  'Prior_Visits_12m', 'Submission_Month', 'Submission_DayOfWeek']
        
        data = {
            "Provider_ID": hash(str(claim_data.get("provider_id", "P0000"))) % 1000,
            "Patient_Age": float(claim_data.get("patient_age", 45)),
            "Patient_Gender": hash(str(claim_data.get("gender", "M"))) % 2,
            "Diagnosis_Code": hash(str(claim_data.get("diagnosis", "Unknown"))) % 1000,
            "Procedure_Code": hash(str(claim_data.get("procedure", "Unknown"))) % 1000,
            "Claim_Amount": float(claim_data.get("total_amount", 0)),
            "Approved_Amount": float(claim_data.get("approved_amount", 0)),
            "Insurance_Type": hash(str(claim_data.get("insurance", "Private"))) % 4,
            "Days_Between_Service_and_Claim": int(claim_data.get("days_since_service", 10)),
            "Number_of_Claims_Per_Provider_Monthly": int(claim_data.get("provider_monthly_volume", 50)),
            "Provider_Specialty": hash(str(claim_data.get("specialty", "General"))) % 20,
            "Patient_State": hash(str(claim_data.get("state", "NY"))) % 50,
            "Claim_Status": 1, # Approved
            "Length_of_Stay": int(claim_data.get("stay_length", 0)),
            "Visit_Type": hash(str(claim_data.get("visit_type", "Outpatient"))) % 3,
            "Chronic_Condition_Flag": 1 if claim_data.get("has_chronic", False) else 0,
            "Prior_Visits_12m": int(claim_data.get("prior_visits", 0)),
            "Submission_Month": 5, # May
            "Submission_DayOfWeek": 1 # Monday
        }
        
        return pd.DataFrame([data])

    def _run_heuristics(self, claim_data: Dict[str, Any]) -> float:
        amount = float(claim_data.get("total_amount", 0))
        if amount > 50000:
            return 0.95
        return 0.1

    def _calculate_confidence(self, score: float, claim_data: Dict[str, Any]) -> float:
        # Confidence is high if we have a real model and enough data
        return 0.92 if self.model else 0.5
