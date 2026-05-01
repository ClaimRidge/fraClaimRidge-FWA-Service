import asyncio
import sys
import os

# Add src to path so we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.layer1_anomaly.detector import Layer1AnomalyDetector

async def run_test():
    # Path to the trained model we just created
    model_path = r"models/fixtures/layer1_anomaly_v1.json"
    
    detector = Layer1AnomalyDetector(model_path=model_path)
    
    # 1. Test a "Normal" claim
    normal_claim = {
        "provider_id": "P0052",
        "patient_age": 37,
        "total_amount": 443.51,
        "approved_amount": 393.16,
        "diagnosis": "I25.10",
        "procedure": "36415",
        "specialty": "Cardiology",
        "state": "NY"
    }
    
    # 2. Test a "Fraudulent" claim (High amount, outlier specialty, etc.)
    fraud_claim = {
        "provider_id": "P9999",
        "patient_age": 82,
        "total_amount": 9500.00, # Large amount
        "approved_amount": 100.00, # Large discrepancy
        "diagnosis": "M54.5",
        "procedure": "99213",
        "specialty": "Pulmonology",
        "state": "IL",
        "prior_visits": 20 # High volume
    }
    
    print("\n--- Testing Normal Claim ---")
    result_normal = await detector.predict(normal_claim)
    print(f"Score: {result_normal['score']:.4f}")
    print(f"Is Anomaly: {result_normal['is_anomaly']}")

    print("\n--- Testing Fraudulent Claim ---")
    result_fraud = await detector.predict(fraud_claim)
    print(f"Score: {result_fraud['score']:.4f}")
    print(f"Is Anomaly: {result_fraud['is_anomaly']}")

if __name__ == "__main__":
    asyncio.run(run_test())
