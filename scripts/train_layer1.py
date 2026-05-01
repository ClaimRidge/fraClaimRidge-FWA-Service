import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import os
import json

# Paths
DATA_PATH = r"C:\Users\dell\.cache\kagglehub\datasets\nudratabbas\healthcare-fraud-detection-dataset\versions\1\healthcare_fraud_detection.csv"
MODEL_OUTPUT_PATH = r"c:\Users\dell\OneDrive\Bureau\claimbridge\services\fwa-svc\models\fixtures\layer1_anomaly_v1.json"
METRICS_OUTPUT_PATH = r"c:\Users\dell\OneDrive\Bureau\claimbridge\services\fwa-svc\models\fixtures\layer1_metrics.json"

def train_model():
    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # 1. Preprocessing
    print("Preprocessing data...")
    
    # Drop unique identifiers that don't help prediction
    df = df.drop(['Claim_ID'], axis=1)
    
    # Feature Engineering: Date features
    df['Claim_Submission_Date'] = pd.to_datetime(df['Claim_Submission_Date'])
    df['Submission_Month'] = df['Claim_Submission_Date'].dt.month
    df['Submission_DayOfWeek'] = df['Claim_Submission_Date'].dt.dayofweek
    df = df.drop(['Claim_Submission_Date'], axis=1)
    
    # Handle Categorical Features
    categorical_cols = [
        'Provider_ID', 'Patient_Gender', 'Diagnosis_Code', 'Procedure_Code', 
        'Insurance_Type', 'Provider_Specialty', 'Patient_State', 
        'Claim_Status', 'Visit_Type'
    ]
    
    encoders = {}
    for col in categorical_cols:
        # Fill missing values with 'Unknown'
        df[col] = df[col].fillna('Unknown')
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
    
    # Handle numeric missing values
    df = df.fillna(0)
    
    # 2. Split Data
    X = df.drop('Is_Fraud', axis=1)
    y = df['Is_Fraud']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 3. Train XGBoost
    print(f"Training XGBoost model on {len(X_train)} samples...")
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        objective='binary:logistic',
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    
    model.fit(X_train, y_train)
    
    # 4. Evaluation
    print("Evaluating model...")
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    print(classification_report(y_test, y_pred))
    
    # 5. Save Model and Metrics
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
    
    print("Training complete!")

if __name__ == "__main__":
    train_model()
