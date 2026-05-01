import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import joblib
import os
import json

# Paths
DATA_PATH = r"C:\Users\dell\.cache\kagglehub\datasets\nudratabbas\healthcare-fraud-detection-dataset\versions\1\healthcare_fraud_detection.csv"
MODEL_OUTPUT_PATH = r"c:\Users\dell\OneDrive\Bureau\claimbridge\services\fwa-svc\models\fixtures\layer1_anomaly_v1.xgb"
ENCODER_OUTPUT_PATH = r"c:\Users\dell\OneDrive\Bureau\claimbridge\services\fwa-svc\models\fixtures\label_encoders.pkl"
METRICS_OUTPUT_PATH = r"c:\Users\dell\OneDrive\Bureau\claimbridge\services\fwa-svc\models\fixtures\layer1_metrics.json"

def train_model():
    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # 1. Feature Selection (THE CRITICAL 6)
    features = [
        'Provider_ID', 'Claim_Amount', 'Procedure_Code', 
        'Diagnosis_Code', 'Patient_Age', 'Patient_Gender'
    ]
    
    X = df[features].copy()
    y = df['Is_Fraud']

    # 2. Label Encoding (User Requested)
    print("Encoding categorical features with LabelEncoder...")
    categorical_cols = ['Provider_ID', 'Procedure_Code', 'Diagnosis_Code', 'Patient_Gender']
    encoders = {}
    
    for col in categorical_cols:
        X[col] = X[col].fillna('Unknown')
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le
        
    # Save the encoders alongside the model
    print(f"Saving encoders to {ENCODER_OUTPUT_PATH}...")
    joblib.dump(encoders, ENCODER_OUTPUT_PATH)
    
    X = X.fillna(0)
    
    # 3. Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 4. Train XGBoost
    print(f"Training XGBoost model on {len(X_train)} samples...")
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.05,
        objective='binary:logistic',
        random_state=42,
        eval_metric='logloss'
    )
    
    model.fit(X_train, y_train)
    
    # 5. Evaluation
    print("Evaluating model...")
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    print(classification_report(y_test, y_pred))
    
    # 6. Save Model and Metrics
    print(f"Saving model to {MODEL_OUTPUT_PATH}...")
    model.save_model(MODEL_OUTPUT_PATH)
    
    with open(METRICS_OUTPUT_PATH, 'w') as f:
        json.dump({
            "classification_report": report,
            "features": list(X.columns),
            "training_samples": len(X_train),
            "test_samples": len(X_test)
        }, f, indent=4)
    
    print("Training complete! Encoders and Model are synchronized.")

if __name__ == "__main__":
    train_model()
