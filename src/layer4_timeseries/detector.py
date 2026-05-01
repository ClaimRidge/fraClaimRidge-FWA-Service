import pandas as pd
import numpy as np
from typing import List, Dict, Any
from src.config import settings

class Layer4TimeSeriesDetector:
    def __init__(self):
        pass

    async def detect_trends(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes billing history to find slow-burn inflation or sudden volume spikes.
        """
        if len(history) < 3:
            return {"status": "INSUFFICIENT_DATA", "is_suspicious": False}

        # 1. Prepare Data
        df = pd.DataFrame(history)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Monthly Aggregation
        monthly = df.set_index('date').resample('M')['amount'].sum().fillna(0)
        
        if len(monthly) < 2:
             return {"status": "INSUFFICIENT_HISTORY", "is_suspicious": False}

        # 2. Z-Score Calculation (Volume Spikes)
        mean_val = monthly.mean()
        std_val = monthly.std()
        
        latest_val = monthly.iloc[-1]
        z_score = (latest_val - mean_val) / (std_val + 1e-6)

        # 3. Trend Analysis (Slope of Inflation)
        y = monthly.values
        x = np.arange(len(y))
        slope, _ = np.polyfit(x, y, 1) if len(y) > 1 else (0, 0)
        
        rel_slope = slope / (mean_val + 1.0)

        # 4. Final Verdict
        # Flag if z-score > 3 (spike) or relative slope > 0.3 (30% monthly growth)
        is_suspicious = z_score > 3.0 or rel_slope > 0.3
        
        return {
            "layer": "L4",
            "z_score": float(z_score),
            "trend_slope": float(rel_slope),
            "is_suspicious": is_suspicious,
            "monthly_averages": monthly.to_dict(),
            "status": "ANOMALY_DETECTED" if is_suspicious else "STABLE"
        }
