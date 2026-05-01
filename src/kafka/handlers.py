from src.layer1_anomaly.detector import Layer1AnomalyDetector
from src.layer2_fingerprint.detector import Layer2FingerprintDetector
from src.repositories.flag_repo import FlagRepository
from src.repositories.base import BaseRepository # For FraudScore
from src.models.database import FraudFlag, FraudScore, Severity
from typing import Dict, Any
import uuid

class ClaimEventHandler:
    def __init__(
        self, 
        l1_detector: Layer1AnomalyDetector,
        l2_detector: Layer2FingerprintDetector,
        flag_repo: FlagRepository,
        score_repo: BaseRepository[FraudScore]
    ):
        self.l1_detector = l1_detector
        self.l2_detector = l2_detector
        self.flag_repo = flag_repo
        self.score_repo = score_repo

    async def handle_claim_submitted(self, tenant_id: str, claim_data: Dict[str, Any]):
        """
        Main orchestration logic for a new claim event.
        """
        claim_id = claim_data.get("id")
        provider_id = claim_data.get("provider_id")

        # 1. Run Layer 1 (Anomaly)
        l1_result = await self.l1_detector.predict(claim_data)
        
        # 2. Run Layer 2 (Provider Drift)
        l2_result = await self.l2_detector.detect_drift(provider_id, tenant_id, l1_result["features_used"])

        # 3. Store Scores
        score_record = FraudScore(
            claim_id=claim_id,
            tenant_id=tenant_id,
            l1_anomaly_score=l1_result["score"],
            l2_drift_score=l2_result.get("drift_score"),
            composite_score=(l1_result["score"] + l2_result.get("drift_score", 0)) / 2, # simple avg
            confidence=l1_result["confidence"]
        )
        await self.score_repo.create(score_record)

        # 4. Create Flags if thresholds met
        if l1_result["is_anomaly"]:
            flag = FraudFlag(
                tenant_id=tenant_id,
                layer="L1",
                severity=Severity.HIGH if l1_result["score"] > 0.9 else Severity.MEDIUM,
                confidence=l1_result["confidence"],
                entity_type="CLAIM",
                entity_id=claim_id,
                description=f"Anomaly detected in claim {claim_id}",
                evidence={"l1_score": l1_result["score"]}
            )
            await self.flag_repo.create(flag)

        if l2_result.get("is_drifting"):
            flag = FraudFlag(
                tenant_id=tenant_id,
                layer="L2",
                severity=Severity.MEDIUM,
                confidence=0.8,
                entity_type="PROVIDER",
                entity_id=provider_id,
                description=f"Provider {provider_id} behavior drift detected",
                evidence={"drift_score": l2_result["drift_score"]}
            )
            await self.flag_repo.create(flag)
