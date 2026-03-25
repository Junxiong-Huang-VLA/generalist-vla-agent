from __future__ import annotations

from statistics import mean

from generalist_vla_agent.utils.types import EncodedObservation, Observation


class MultimodalEncoder:
    """MVP encoder with deterministic aggregation for fast testing/integration."""

    def encode(self, obs: Observation) -> EncodedObservation:
        rgb_mean = mean(obs.rgb) if obs.rgb else 0.0
        depth_mean = mean(obs.depth) if obs.depth else 0.0
        text_len = float(len(obs.text.split()))

        feature_vector = [rgb_mean, depth_mean, text_len]
        metadata = {"rgb_size": len(obs.rgb), "depth_size": len(obs.depth)}
        return EncodedObservation(feature_vector=feature_vector, metadata=metadata)
