import asyncio
import sys
import os

# Add src to path so we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.layer1_anomaly.detector import Layer1AnomalyDetector

async def run_verdict(amount, volume, age):
    detector = Layer1AnomalyDetector(model_path="models/fixtures/layer1_anomaly_v1.json")
    
    claim = {
        "total_amount": amount,
        "provider_monthly_volume": volume,
        "patient_age": age,
        "provider_id": "P_AUTO_TEST"
    }

    result = await detector.predict(claim)
    
    print(f"\n--- Analysis for Claim (Amt: ${amount}, Vol: {volume}) ---")
    print(f"Score: {result['score']:.4f}")
    
    if result['is_anomaly']:
        print("VERDICT: [!] FRAUD DETECTED")
    else:
        print("VERDICT: [OK] LEGITIMATE")

async def main():
    # Scenario 1: Typical low-risk claim
    await run_verdict(amount=250.00, volume=40, age=35)
    
    # Scenario 2: Suspicious high-risk claim
    await run_verdict(amount=85000.00, volume=1200, age=92)

if __name__ == "__main__":
    asyncio.run(main())
