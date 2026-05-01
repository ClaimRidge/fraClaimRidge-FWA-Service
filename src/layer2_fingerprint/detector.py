from typing import Dict, Any, List
import numpy as np
from src.core.cache import RedisCache

class Layer2FingerprintDetector:
    def __init__(self, cache: RedisCache):
        self.cache = cache

    async def detect_drift(self, provider_id: str, tenant_id: str, current_features: Dict[str, float]) -> Dict[str, Any]:
        """
        Detects if a provider's behavior has drifted from their baseline using PSI.
        """
        # 1. Fetch baseline from Redis (populated nightly/on demand)
        baseline = await self.cache.get_provider_baseline(tenant_id, provider_id)
        
        if not baseline:
            # No baseline yet - mark as "COLD_START"
            return {
                "drift_score": 0.0, 
                "is_drifting": False,
                "status": "COLD_START",
                "evidence": {}
            }

        # 2. Calculate Drift per Feature
        drift_breakdown = {}
        total_drift = 0.0
        feature_count = 0

        for feat, b_val in baseline.items():
            if feat in current_features and feat != "updated_at":
                c_val = current_features[feat]
                # Calculate absolute relative change
                # (Current - Baseline) / (Baseline + small constant)
                feat_drift = abs(c_val - b_val) / (abs(b_val) + 1.0)
                drift_breakdown[feat] = float(feat_drift)
                total_drift += feat_drift
                feature_count += 1
        
        avg_drift = total_drift / feature_count if feature_count > 0 else 0.0

        return {
            "drift_score": avg_drift,
            "is_drifting": avg_drift > settings.L2_DRIFT_THRESHOLD,
            "baseline_date": baseline.get("updated_at"),
            "status": "STABLE" if avg_drift <= settings.L2_DRIFT_THRESHOLD else "DRIFTING",
            "evidence": drift_breakdown
        }
