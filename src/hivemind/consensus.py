"""Consensus mechanisms for HiveMind architecture."""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from enum import Enum
import logging
from pydantic import BaseModel

from agents.base_agent import AgentResponse

logger = logging.getLogger(__name__)


class ConsensusStrategy(str, Enum):
    """Available consensus strategies."""
    WEIGHTED_VOTING = "weighted_voting"
    UNANIMOUS = "unanimous"
    MAJORITY = "majority"
    CONFIDENCE_THRESHOLD = "confidence_threshold"
    ITERATIVE_REFINEMENT = "iterative_refinement"


class ConsensusResult(BaseModel):
    """
    Result of consensus mechanism.

    Attributes:
        achieved: Whether consensus was achieved.
        strategy_used: Consensus strategy applied.
        consensus_level: Numerical consensus level (0.0-1.0).
        selected_responses: Responses that achieved consensus.
        conflicting_responses: Responses that conflicted.
        justification: Explanation of consensus decision.
        metadata: Additional metadata.
    """
    achieved: bool
    strategy_used: ConsensusStrategy
    consensus_level: float
    selected_responses: List[AgentResponse] = []
    conflicting_responses: List[AgentResponse] = []
    justification: str
    metadata: Dict[str, Any] = {}


class ConsensusEngine(ABC):
    """Abstract base class for consensus engines."""

    def __init__(self, name: str):
        """Initialize consensus engine."""
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

    @abstractmethod
    def achieve_consensus(
        self,
        responses: List[AgentResponse],
        context: Optional[Dict[str, Any]] = None
    ) -> ConsensusResult:
        """
        Achieve consensus from multiple agent responses.

        Args:
            responses: List of agent responses.
            context: Optional context.

        Returns:
            ConsensusResult: Result of consensus mechanism.
        """
        pass


class WeightedVotingConsensus(ConsensusEngine):
    """
    Weighted voting consensus mechanism.

    Agents have different weights based on their expertise.
    Consensus is achieved when weighted average exceeds threshold.
    """

    def __init__(
        self,
        agent_weights: Optional[Dict[str, float]] = None,
        threshold: float = 0.7
    ):
        """
        Initialize weighted voting consensus.

        Args:
            agent_weights: Weights for each agent (default: equal weights).
            threshold: Consensus threshold (0.0-1.0).
        """
        super().__init__("WeightedVoting")
        self.agent_weights = agent_weights or {}
        self.threshold = threshold

    def achieve_consensus(
        self,
        responses: List[AgentResponse],
        context: Optional[Dict[str, Any]] = None
    ) -> ConsensusResult:
        """Achieve consensus using weighted voting."""
        self.logger.info(f"Applying weighted voting consensus with {len(responses)} responses")

        if not responses:
            return ConsensusResult(
                achieved=False,
                strategy_used=ConsensusStrategy.WEIGHTED_VOTING,
                consensus_level=0.0,
                justification="No responses to evaluate"
            )

        # Calculate weights
        total_weight = 0
        weighted_confidence = 0

        for response in responses:
            weight = self.agent_weights.get(response.agent_name, 1.0)
            total_weight += weight
            weighted_confidence += response.confidence * weight

        # Calculate weighted average
        avg_confidence = weighted_confidence / total_weight if total_weight > 0 else 0

        # Determine if consensus achieved
        achieved = avg_confidence >= self.threshold

        # Classify responses
        selected = [r for r in responses if r.confidence >= self.threshold]
        conflicting = [r for r in responses if r.confidence < self.threshold]

        justification = (
            f"Weighted voting consensus {'achieved' if achieved else 'not achieved'}. "
            f"Average weighted confidence: {avg_confidence:.2f}, "
            f"Threshold: {self.threshold:.2f}. "
            f"{len(selected)} agents above threshold, {len(conflicting)} below."
        )

        return ConsensusResult(
            achieved=achieved,
            strategy_used=ConsensusStrategy.WEIGHTED_VOTING,
            consensus_level=avg_confidence,
            selected_responses=selected,
            conflicting_responses=conflicting,
            justification=justification,
            metadata={
                "total_weight": total_weight,
                "weighted_confidence": weighted_confidence,
                "threshold": self.threshold
            }
        )


class MajorityConsensus(ConsensusEngine):
    """
    Simple majority consensus mechanism.

    Consensus achieved when majority of agents agree (confidence > threshold).
    """

    def __init__(self, confidence_threshold: float = 0.6):
        """
        Initialize majority consensus.

        Args:
            confidence_threshold: Minimum confidence to count as agreement.
        """
        super().__init__("Majority")
        self.confidence_threshold = confidence_threshold

    def achieve_consensus(
        self,
        responses: List[AgentResponse],
        context: Optional[Dict[str, Any]] = None
    ) -> ConsensusResult:
        """Achieve consensus using simple majority."""
        self.logger.info(f"Applying majority consensus with {len(responses)} responses")

        if not responses:
            return ConsensusResult(
                achieved=False,
                strategy_used=ConsensusStrategy.MAJORITY,
                consensus_level=0.0,
                justification="No responses to evaluate"
            )

        # Count agreeing agents
        agreeing = [r for r in responses if r.confidence >= self.confidence_threshold]
        disagreeing = [r for r in responses if r.confidence < self.confidence_threshold]

        majority_ratio = len(agreeing) / len(responses)
        achieved = majority_ratio > 0.5

        avg_confidence = sum(r.confidence for r in responses) / len(responses)

        justification = (
            f"Majority consensus {'achieved' if achieved else 'not achieved'}. "
            f"{len(agreeing)}/{len(responses)} agents agree "
            f"(confidence >= {self.confidence_threshold:.2f}). "
            f"Majority ratio: {majority_ratio:.2f}"
        )

        return ConsensusResult(
            achieved=achieved,
            strategy_used=ConsensusStrategy.MAJORITY,
            consensus_level=avg_confidence,
            selected_responses=agreeing,
            conflicting_responses=disagreeing,
            justification=justification,
            metadata={
                "majority_ratio": majority_ratio,
                "confidence_threshold": self.confidence_threshold
            }
        )


class UnanimousConsensus(ConsensusEngine):
    """
    Unanimous consensus mechanism.

    All agents must agree (high confidence) for consensus.
    """

    def __init__(self, confidence_threshold: float = 0.8):
        """
        Initialize unanimous consensus.

        Args:
            confidence_threshold: Minimum confidence required from all agents.
        """
        super().__init__("Unanimous")
        self.confidence_threshold = confidence_threshold

    def achieve_consensus(
        self,
        responses: List[AgentResponse],
        context: Optional[Dict[str, Any]] = None
    ) -> ConsensusResult:
        """Achieve consensus requiring unanimity."""
        self.logger.info(f"Applying unanimous consensus with {len(responses)} responses")

        if not responses:
            return ConsensusResult(
                achieved=False,
                strategy_used=ConsensusStrategy.UNANIMOUS,
                consensus_level=0.0,
                justification="No responses to evaluate"
            )

        # Check if all agents agree
        agreeing = [r for r in responses if r.confidence >= self.confidence_threshold]
        disagreeing = [r for r in responses if r.confidence < self.confidence_threshold]

        achieved = len(agreeing) == len(responses)
        avg_confidence = sum(r.confidence for r in responses) / len(responses)

        justification = (
            f"Unanimous consensus {'achieved' if achieved else 'not achieved'}. "
            f"{len(agreeing)}/{len(responses)} agents have confidence >= {self.confidence_threshold:.2f}. "
        )

        if not achieved:
            justification += f"Blocking agents: {', '.join(r.agent_name for r in disagreeing)}"

        return ConsensusResult(
            achieved=achieved,
            strategy_used=ConsensusStrategy.UNANIMOUS,
            consensus_level=avg_confidence,
            selected_responses=agreeing if achieved else [],
            conflicting_responses=disagreeing,
            justification=justification,
            metadata={
                "confidence_threshold": self.confidence_threshold,
                "unanimity_achieved": achieved
            }
        )


class ConfidenceThresholdConsensus(ConsensusEngine):
    """
    Confidence threshold consensus.

    Consensus achieved when average confidence exceeds threshold.
    """

    def __init__(self, threshold: float = 0.75):
        """
        Initialize confidence threshold consensus.

        Args:
            threshold: Minimum average confidence required.
        """
        super().__init__("ConfidenceThreshold")
        self.threshold = threshold

    def achieve_consensus(
        self,
        responses: List[AgentResponse],
        context: Optional[Dict[str, Any]] = None
    ) -> ConsensusResult:
        """Achieve consensus based on confidence threshold."""
        self.logger.info(f"Applying confidence threshold consensus with {len(responses)} responses")

        if not responses:
            return ConsensusResult(
                achieved=False,
                strategy_used=ConsensusStrategy.CONFIDENCE_THRESHOLD,
                consensus_level=0.0,
                justification="No responses to evaluate"
            )

        # Calculate average confidence
        avg_confidence = sum(r.confidence for r in responses) / len(responses)
        achieved = avg_confidence >= self.threshold

        # Sort by confidence
        sorted_responses = sorted(responses, key=lambda r: r.confidence, reverse=True)
        high_confidence = [r for r in responses if r.confidence >= self.threshold]
        low_confidence = [r for r in responses if r.confidence < self.threshold]

        justification = (
            f"Confidence threshold consensus {'achieved' if achieved else 'not achieved'}. "
            f"Average confidence: {avg_confidence:.2f}, "
            f"Threshold: {self.threshold:.2f}. "
            f"{len(high_confidence)} agents above threshold."
        )

        return ConsensusResult(
            achieved=achieved,
            strategy_used=ConsensusStrategy.CONFIDENCE_THRESHOLD,
            consensus_level=avg_confidence,
            selected_responses=high_confidence if achieved else [],
            conflicting_responses=low_confidence,
            justification=justification,
            metadata={
                "average_confidence": avg_confidence,
                "threshold": self.threshold,
                "highest_confidence": sorted_responses[0].confidence if sorted_responses else 0,
                "lowest_confidence": sorted_responses[-1].confidence if sorted_responses else 0
            }
        )


class ConsensusManager:
    """
    Manager for applying different consensus strategies.

    This class provides a unified interface for applying various
    consensus mechanisms to agent responses.
    """

    def __init__(self):
        """Initialize consensus manager."""
        self.strategies: Dict[ConsensusStrategy, ConsensusEngine] = {
            ConsensusStrategy.WEIGHTED_VOTING: WeightedVotingConsensus(),
            ConsensusStrategy.MAJORITY: MajorityConsensus(),
            ConsensusStrategy.UNANIMOUS: UnanimousConsensus(),
            ConsensusStrategy.CONFIDENCE_THRESHOLD: ConfidenceThresholdConsensus()
        }
        self.logger = logging.getLogger(__name__)

    def apply_consensus(
        self,
        responses: List[AgentResponse],
        strategy: ConsensusStrategy = ConsensusStrategy.WEIGHTED_VOTING,
        context: Optional[Dict[str, Any]] = None
    ) -> ConsensusResult:
        """
        Apply consensus strategy to agent responses.

        Args:
            responses: List of agent responses.
            strategy: Consensus strategy to apply.
            context: Optional context.

        Returns:
            ConsensusResult: Result of consensus mechanism.
        """
        self.logger.info(f"Applying {strategy.value} consensus to {len(responses)} responses")

        if strategy not in self.strategies:
            raise ValueError(f"Unknown consensus strategy: {strategy}")

        engine = self.strategies[strategy]
        return engine.achieve_consensus(responses, context)

    def register_strategy(
        self,
        strategy: ConsensusStrategy,
        engine: ConsensusEngine
    ) -> None:
        """
        Register a custom consensus strategy.

        Args:
            strategy: Strategy identifier.
            engine: Consensus engine implementation.
        """
        self.strategies[strategy] = engine
        self.logger.info(f"Registered custom consensus strategy: {strategy.value}")

    def get_available_strategies(self) -> List[str]:
        """
        Get list of available consensus strategies.

        Returns:
            List of strategy names.
        """
        return [s.value for s in self.strategies.keys()]
