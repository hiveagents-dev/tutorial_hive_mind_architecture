"""
CausalMemoryGraph - Cause-effect relationship tracking.

Tracks cause-and-effect relationships between agent actions and outcomes.
Supports A/B experiments, uplift calculation, confounder detection,
and multi-hop causal chain reasoning.

Ported from the TypeScript AgentDB's CausalMemoryGraph controller.
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ..storage import Storage

logger = logging.getLogger(__name__)


@dataclass
class CausalEdge:
    """A cause-effect relationship."""
    id: int
    cause: str
    effect: str
    uplift: float
    confidence: float
    confounder_score: float
    observation_count: int
    namespace: str
    metadata: Dict[str, Any]


@dataclass
class CausalChain:
    """A multi-hop causal chain."""
    edges: List[CausalEdge]
    total_confidence: float
    total_uplift: float
    path: List[str]


@dataclass
class ExperimentResult:
    """Result from a causal experiment."""
    experiment_id: int
    name: str
    uplift: float
    p_value: float
    significant: bool
    treatment_mean: float
    control_mean: float
    observations: int


class CausalMemoryGraph:
    """
    Causal memory graph for tracking cause-effect relationships.

    Provides:
    - Adding and querying causal edges
    - A/B experiment creation and analysis
    - Multi-hop causal chain discovery
    - Uplift calculation with significance testing
    - Edge pruning based on confidence
    """

    def __init__(
        self,
        storage: Storage,
        namespace: str = "default",
    ):
        self._storage = storage
        self._namespace = namespace
        logger.info(f"CausalMemoryGraph initialized (namespace={namespace})")

    def add_causal_edge(
        self,
        cause: str,
        effect: str,
        uplift: float = 0.0,
        confidence: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Add or update a causal edge.

        If an edge between cause and effect already exists, it updates
        the metrics using exponential moving average.

        Args:
            cause: The cause action/event.
            effect: The effect/outcome.
            uplift: Estimated causal uplift.
            confidence: Confidence in the causal relationship.
            metadata: Additional metadata.

        Returns:
            Edge ID.
        """
        # Check for existing edge
        existing = self._storage.get_causal_edges(
            cause=cause, effect=effect, namespace=self._namespace
        )

        if existing:
            edge = existing[0]
            # Exponential moving average
            alpha = 0.2
            new_uplift = alpha * uplift + (1 - alpha) * edge["uplift"]
            new_confidence = alpha * confidence + (1 - alpha) * edge["confidence"]
            self._storage.update_causal_edge(edge["id"], new_uplift, new_confidence)

            self._storage.log_event(
                agent_name="CausalMemoryGraph",
                event_type="learning",
                content=f"Updated causal edge: {cause} -> {effect} (uplift={new_uplift:.3f})",
                phase="update",
                namespace=self._namespace,
            )

            return edge["id"]
        else:
            edge_id = self._storage.insert_causal_edge(
                cause=cause,
                effect=effect,
                uplift=uplift,
                confidence=confidence,
                namespace=self._namespace,
                metadata=metadata,
            )

            self._storage.log_event(
                agent_name="CausalMemoryGraph",
                event_type="learning",
                content=f"Added causal edge: {cause} -> {effect} (uplift={uplift:.3f})",
                phase="create",
                namespace=self._namespace,
            )

            return edge_id

    def query_effects(self, cause: str) -> List[CausalEdge]:
        """
        Query all effects of a given cause.

        Args:
            cause: The cause to query.

        Returns:
            List of causal edges from this cause.
        """
        rows = self._storage.get_causal_edges(cause=cause, namespace=self._namespace)
        return [self._row_to_edge(r) for r in rows]

    def query_causes(self, effect: str) -> List[CausalEdge]:
        """
        Query all causes of a given effect.

        Args:
            effect: The effect to query.

        Returns:
            List of causal edges leading to this effect.
        """
        rows = self._storage.get_causal_edges(effect=effect, namespace=self._namespace)
        return [self._row_to_edge(r) for r in rows]

    def find_causal_chain(
        self,
        start: str,
        end: str,
        max_hops: int = 5,
    ) -> Optional[CausalChain]:
        """
        Find a causal chain between two nodes using BFS.

        Args:
            start: Starting cause.
            end: Target effect.
            max_hops: Maximum chain length.

        Returns:
            CausalChain if a path exists, None otherwise.
        """
        # BFS for shortest causal path
        visited = {start}
        queue: List[Tuple[str, List[CausalEdge]]] = [(start, [])]

        while queue:
            current, path = queue.pop(0)
            if len(path) >= max_hops:
                continue

            effects = self.query_effects(current)
            for edge in effects:
                if edge.effect == end:
                    chain = path + [edge]
                    return CausalChain(
                        edges=chain,
                        total_confidence=self._chain_confidence(chain),
                        total_uplift=sum(e.uplift for e in chain),
                        path=[start] + [e.effect for e in chain],
                    )
                if edge.effect not in visited:
                    visited.add(edge.effect)
                    queue.append((edge.effect, path + [edge]))

        return None

    def _chain_confidence(self, chain: List[CausalEdge]) -> float:
        """Calculate joint confidence of a causal chain."""
        if not chain:
            return 0.0
        confidence = 1.0
        for edge in chain:
            confidence *= edge.confidence
        return confidence

    # ── A/B Experiments ───────────────────────────────────────────────

    def create_experiment(
        self,
        name: str,
        hypothesis: str,
        cause: str,
        effect: str,
    ) -> int:
        """
        Create a new A/B experiment.

        Args:
            name: Experiment name.
            hypothesis: What you expect to happen.
            cause: The treatment variable.
            effect: The outcome variable.

        Returns:
            Experiment ID.
        """
        exp_id = self._storage.create_experiment(name, hypothesis, cause, effect)
        logger.info(f"Created experiment '{name}' (id={exp_id})")
        return exp_id

    def record_observation(
        self,
        experiment_id: int,
        group: str,
        outcome: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Record an observation for an experiment.

        Args:
            experiment_id: Experiment ID.
            group: "treatment" or "control".
            outcome: Observed outcome value.
            metadata: Additional observation metadata.

        Returns:
            Observation ID.
        """
        return self._storage.record_observation(experiment_id, group, outcome, metadata)

    def analyze_experiment(self, experiment_id: int) -> ExperimentResult:
        """
        Analyze an experiment's results with t-test.

        Args:
            experiment_id: Experiment ID.

        Returns:
            ExperimentResult with uplift and significance.
        """
        conn = self._storage.connection

        # Get experiment info
        exp = conn.execute(
            "SELECT * FROM causal_experiments WHERE id = ?", (experiment_id,)
        ).fetchone()
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get observations
        treatment = conn.execute(
            "SELECT outcome FROM causal_observations WHERE experiment_id = ? AND group_name = 'treatment'",
            (experiment_id,),
        ).fetchall()
        control = conn.execute(
            "SELECT outcome FROM causal_observations WHERE experiment_id = ? AND group_name = 'control'",
            (experiment_id,),
        ).fetchall()

        treatment_vals = [r[0] for r in treatment]
        control_vals = [r[0] for r in control]

        if not treatment_vals or not control_vals:
            return ExperimentResult(
                experiment_id=experiment_id,
                name=exp["name"],
                uplift=0.0,
                p_value=1.0,
                significant=False,
                treatment_mean=0.0,
                control_mean=0.0,
                observations=0,
            )

        # Calculate means
        t_mean = sum(treatment_vals) / len(treatment_vals)
        c_mean = sum(control_vals) / len(control_vals)
        uplift = t_mean - c_mean

        # Simple t-test (Welch's)
        p_value = self._welch_t_test(treatment_vals, control_vals)

        return ExperimentResult(
            experiment_id=experiment_id,
            name=exp["name"],
            uplift=uplift,
            p_value=p_value,
            significant=p_value < 0.05,
            treatment_mean=t_mean,
            control_mean=c_mean,
            observations=len(treatment_vals) + len(control_vals),
        )

    def _welch_t_test(self, a: List[float], b: List[float]) -> float:
        """Simple Welch's t-test returning approximate p-value."""
        n1, n2 = len(a), len(b)
        if n1 < 2 or n2 < 2:
            return 1.0

        mean1 = sum(a) / n1
        mean2 = sum(b) / n2
        var1 = sum((x - mean1) ** 2 for x in a) / (n1 - 1)
        var2 = sum((x - mean2) ** 2 for x in b) / (n2 - 1)

        se = math.sqrt(var1 / n1 + var2 / n2) if (var1 / n1 + var2 / n2) > 0 else 1.0
        t_stat = abs(mean1 - mean2) / se if se > 0 else 0.0

        # Approximate p-value using normal distribution for large samples
        # For small samples this is a rough approximation
        df = n1 + n2 - 2
        if df <= 0:
            return 1.0

        # Simple approximation: p ~ 2 * exp(-0.717 * t - 0.416 * t^2)
        # (rough approximation for two-tailed test)
        p_value = 2.0 * math.exp(-0.717 * t_stat - 0.416 * t_stat * t_stat)
        return min(max(p_value, 0.0), 1.0)

    # ── Edge Pruning ──────────────────────────────────────────────────

    def prune_edges(
        self,
        min_confidence: float = 0.1,
        min_observations: int = 3,
    ) -> int:
        """
        Prune low-confidence causal edges.

        Args:
            min_confidence: Minimum confidence to keep.
            min_observations: Minimum observations to keep.

        Returns:
            Number of edges pruned.
        """
        conn = self._storage.connection
        cursor = conn.execute(
            """DELETE FROM causal_edges
               WHERE namespace = ? AND (confidence < ? OR observation_count < ?)""",
            (self._namespace, min_confidence, min_observations),
        )
        conn.commit()
        pruned = cursor.rowcount
        if pruned:
            logger.info(f"Pruned {pruned} causal edges (min_confidence={min_confidence})")
        return pruned

    def _row_to_edge(self, row: Dict) -> CausalEdge:
        """Convert a DB row to CausalEdge."""
        return CausalEdge(
            id=row["id"],
            cause=row["cause"],
            effect=row["effect"],
            uplift=row["uplift"],
            confidence=row["confidence"],
            confounder_score=row.get("confounder_score", 0.0),
            observation_count=row.get("observation_count", 0),
            namespace=row["namespace"],
            metadata=row.get("metadata_json", {}),
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get causal graph statistics."""
        edges = self._storage.get_causal_edges(namespace=self._namespace)
        if not edges:
            return {
                "total_edges": 0,
                "avg_confidence": 0.0,
                "avg_uplift": 0.0,
                "namespace": self._namespace,
            }

        return {
            "total_edges": len(edges),
            "avg_confidence": sum(e["confidence"] for e in edges) / len(edges),
            "avg_uplift": sum(e["uplift"] for e in edges) / len(edges),
            "unique_causes": len(set(e["cause"] for e in edges)),
            "unique_effects": len(set(e["effect"] for e in edges)),
            "namespace": self._namespace,
        }
