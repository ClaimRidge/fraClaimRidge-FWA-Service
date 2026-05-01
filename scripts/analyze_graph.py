import pandas as pd
import asyncio
import sys
import os
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.layer3_graph.detector import Layer3GraphDetector

DATA_PATH = r"C:\Users\dell\.cache\kagglehub\datasets\nudratabbas\healthcare-fraud-detection-dataset\versions\1\healthcare_fraud_detection.csv"

async def run_graph_analysis():
    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # Use a subset for faster processing if needed, 
    # but here we use the whole set to see real network effects.
    print(f"Building graph from {len(df)} claims...")
    
    detector = Layer3GraphDetector()
    flags = await detector.analyze_collusion(df)
    
    # Separate flags by type
    hubs = [f for f in flags if f['type'] == 'HUB_PROVIDER']
    rings = [f for f in flags if f['type'] == 'COLLUSION_RING']
    
    print("\n" + "="*40)
    print("LAYER 3 GRAPH ANALYSIS RESULTS")
    print("="*40)
    print(f"Total Hub Providers Found: {len(hubs)}")
    print(f"Total Collusion Rings Found: {len(rings)}")
    
    if hubs:
        print("\n--- Top 5 Hub Providers (By Centrality) ---")
        sorted_hubs = sorted(hubs, key=lambda x: x['score'], reverse=True)
        for hub in sorted_hubs[:5]:
            print(f"Provider ID: {hub['entity_id']} | Score: {hub['score']:.5f} | Severity: {hub['severity']}")

    if rings:
        print("\n--- Detected Collusion Rings (Samples) ---")
        for ring in rings[:3]:
            print(f"Ring Entities: {ring['entities']} | Density: {ring['score']:.2f}")

    # Save results to fixtures for use in the dashboard
    output_path = r"models/fixtures/layer3_graph_results.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(flags, f, indent=4)
        
    print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(run_graph_analysis())
