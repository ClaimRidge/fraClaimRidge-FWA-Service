from typing import List
from src.models.database import Severity, FraudFlag

class SeverityCalculator:
    @staticmethod
    def calculate_composite_severity(flags: List[FraudFlag]) -> Severity:
        """
        Calculates the overall severity of a case based on its constituent flags.
        Uses a weighted points system.
        """
        weights = {
            Severity.LOW: 1,
            Severity.MEDIUM: 3,
            Severity.HIGH: 10,
            Severity.CRITICAL: 50
        }

        total_points = sum(weights.get(flag.severity, 0) for flag in flags)

        # Cross-layer boost: if multiple layers detected fraud, boost severity
        unique_layers = {flag.layer for flag in flags}
        if len(unique_layers) > 1:
            total_points *= (1 + (0.2 * (len(unique_layers) - 1)))

        if total_points >= 50:
            return Severity.CRITICAL
        elif total_points >= 20:
            return Severity.HIGH
        elif total_points >= 5:
            return Severity.MEDIUM
        else:
            return Severity.LOW

    @staticmethod
    def calculate_confidence_score(flags: List[FraudFlag]) -> float:
        """
        Calculates confidence as a weighted average of individual flag confidences.
        """
        if not flags:
            return 0.0
        
        # Give more weight to flags from Layer 1 and Layer 4
        layer_weights = {
            "L1": 1.5,
            "L2": 1.0,
            "L3": 0.8,
            "L4": 1.2
        }

        total_weighted_confidence = 0.0
        total_weight = 0.0

        for flag in flags:
            weight = layer_weights.get(flag.layer, 1.0)
            total_weighted_confidence += flag.confidence * weight
            total_weight += weight

        return min(1.0, total_weighted_confidence / total_weight)
