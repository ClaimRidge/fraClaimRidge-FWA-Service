import pandas as pd
import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.cache import RedisCache

DATA_PATH = r"C:\Users\dell\.cache\kagglehub\datasets\nudratabbas\healthcare-fraud-detection-dataset\versions\1\healthcare_fraud_detection.csv"

async def generate_baselines():
    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # Filter for non-fraudulent claims only for the baseline
    df_clean = df[df['Is_Fraud'] == 0]
    
    # Features to baseline
    features = [
        'Claim_Amount', 'Approved_Amount', 'Patient_Age', 
        'Days_Between_Service_and_Claim', 
        'Number_of_Claims_Per_Provider_Monthly', 
        'Length_of_Stay', 'Prior_Visits_12m'
    ]
    
    print("Calculating provider baselines...")
    # Group by Provider and calculate mean of numeric features
    baselines = df_clean.groupby('Provider_ID')[features].mean().to_dict('index')
    
    cache = RedisCache()
    
    count = 0
    tenant_id = "test_tenant" # Default for this exercise
    
    print(f"Writing {len(baselines)} fingerprints to Redis...")
    for provider_id, stats in baselines.items():
        # Add metadata
        stats['updated_at'] = datetime.utcnow().isoformat()
        
        await cache.set_provider_baseline(tenant_id, provider_id, stats)
        count += 1
        if count % 100 == 0:
            print(f"Processed {count} providers...")

    await cache.close()
    print("Baseline generation complete!")

if __name__ == "__main__":
    asyncio.run(generate_baselines())
