import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import os
import json

# Paths
DATA_PATH = r"C:\Users\dell\.cache\kagglehub\datasets\nudratabbas\healthcare-fraud-detection-dataset\versions\1\healthcare_fraud_detection.csv"
MODEL_OUTPUT_PATH = r"c:\Users\dell\OneDrive\Bureau\claimbridge\services\fwa-svc\models\fixtures\layer1_anomaly_v1.xgb"
METRICS_OUTPUT_PATH = r"c:\Users\dell\OneDrive\Bureau\claimbridge\services\fwa-svc\models\fixtures\layer1_metrics.json"

def train_model():
    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # 1. Feature Selection (THE CRITICAL 6)
    print("Selecting the 6 CORE features...")
    features = [
        'Provider_ID', 'Claim_Amount', 'Procedure_Code', 
        'Diagnosis_Code', 'Patient_Age', 'Patient_Gender'
    ]
    
    X = df[features].copy()
    y = df['Is_Fraud']

    # 2. Deterministic Encoding (Matching Detector logic)
    print("Encoding categorical features with hashing...")
    for col in ['Provider_ID', 'Procedure_Code', 'Diagnosis_Code', 'Patient_Gender']:
        X[col] = X[col].apply(lambda x: hash(str(x)) % 1000)
    
    X = X.fillna(0)
    
    # 3. Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 4. Train XGBoost
    print(f"Training XGBoost model on {len(X_train)} samples with {len(features)} features...")
    model = xgb.XGBClassifier(
        n_estimators=200, # Increased for better sensitivity
        max_depth=8,      # Deeper for interaction detection
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
    os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH), exist_ok=True)
    model.save_model(MODEL_OUTPUT_PATH)
    
    with open(METRICS_OUTPUT_PATH, 'w') as f:
        json.dump({
            "classification_report": report,
            "features": list(X.columns),
            "training_samples": len(X_train),
            "test_samples": len(X_test)
        }, f, indent=4)
    
    print("Training complete! Model is now optimized for the Critical 6 features.")

if __name__ == "__main__":
    train_model()
