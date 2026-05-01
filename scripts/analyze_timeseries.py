import pandas as pd
import asyncio
import sys
import os
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.layer4_timeseries.detector import Layer4TimeSeriesDetector

DATA_PATH = r"C:\Users\dell\.cache\kagglehub\datasets\nudratabbas\healthcare-fraud-detection-dataset\versions\1\healthcare_fraud_detection.csv"

async def run_timeseries_analysis():
    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # We need to simulate history for a few providers
    # Let's pick the Top 5 providers and analyze their "Monthly Volume"
    detector = Layer4TimeSeriesDetector()
    
    top_providers = df['Provider_ID'].unique()[:10]
    all_results = []

    print(f"Analyzing time-series trends for {len(top_providers)} providers...")

    for pid in top_providers:
        p_data = df[df['Provider_ID'] == pid].copy()
        
        # Prepare history format
        history = []
        for _, row in p_data.iterrows():
            history.append({
                "date": row['Claim_Submission_Date'],
                "amount": row['Claim_Amount']
            })
            
        result = await detector.detect_trends(history)
        result['provider_id'] = pid
        # Ensure JSON serializable types
        result['is_suspicious'] = bool(result['is_suspicious'])
        result['z_score'] = float(result['z_score'])
        result['trend_slope'] = float(result['trend_slope'])
        result['monthly_averages'] = {str(k): float(v) for k, v in result['monthly_averages'].items()}
        all_results.append(result)

    # Save to fixtures for the Dashboard
    output_path = r"models/fixtures/layer4_trends.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=4)
        
    print(f"Layer 4 analysis complete! Results saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(run_timeseries_analysis())
