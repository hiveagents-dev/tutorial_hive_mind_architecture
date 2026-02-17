"""
ReasoningBank - Reasoning pattern storage and retrieval.

Stores and retrieves reasoning patterns (task type, approach, success rate)
using semantic embeddings. Agents can query for the best reasoning approach
for a given task type based on historical success.

Ported from the TypeScript AgentDB's ReasoningBank controller.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from ..storage import Storage
from ..embeddings import EmbeddingService
from ..vector_search import VectorSearchEngine, SearchResult

logger = logging.getLogger(__name__)


@dataclass
class ReasoningPattern:
    """A reasoning pattern."""
    id: int
    task_type: str
    approach: str
    context: str
    outcome: str
    success: bool
    reward: float
    usage_count: int
    success_count: int
    namespace: str
    metadata: Dict[str, Any]
    created_at: str

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.usage_count == 0:
            return 0.0
        return self.success_count / self.usage_count


class ReasoningBank:
    """
    Bank of reasoning patterns for decision-making.

    Provides:
    - Pattern storage with task type, approach, and outcome
    - Semantic search for applicable patterns
    - Success tracking and reward signals
    - Pattern pruning based on performance
    """

    def __init__(
        self,
        storage: Storage,
        embeddings: EmbeddingService,
        vector_engine: VectorSearchEngine,
        namespace: str = "default",
    ):
        self._storage = storage
        self._embeddings = embeddings
        self._vectors = vector_engine
        self._namespace = namespace
        self._index_name = f"patterns_{namespace}"
        logger.info(f"ReasoningBank initialized (namespace={namespace})")

    def _build_index(self) -> None:
        """Rebuild vector index from stored pattern embeddings."""
        idx = self._vectors.get_index(self._index_name)
        if idx.size > 0:
            return

        rows = self._storage.get_all_embeddings("pattern_embeddings")
        for emb_id, pattern_id, emb_bytes in rows:
            pattern = self._storage.get_pattern(pattern_id)
            if pattern and pattern["namespace"] == self._namespace:
                vec = self._embeddings.from_bytes(emb_bytes)
                self._vectors.insert(
                    self._index_name,
                    f"pat_{pattern_id}",
                    pattern_id,
                    vec,
                    {
                        "task_type": pattern["task_type"],
                        "success": pattern["success"],
                        "reward": pattern["reward"],
                    },
                )

    def store_pattern(
        self,
        task_type: str,
        approach: str,
        context: str = "",
        outcome: str = "",
        success: bool = False,
        reward: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Store a reasoning pattern.

        Args:
            task_type: Type of task (e.g., "analysis", "synthesis", "evaluation").
            approach: The reasoning approach used.
            context: Context in which the approach was applied.
            outcome: What happened as a result.
            success: Whether the approach was successful.
            reward: Reward signal.
            metadata: Additional metadata.

        Returns:
            Pattern ID.
        """
        pattern_id = self._storage.insert_pattern(
            task_type=task_type,
            approach=approach,
            context=context,
            outcome=outcome,
            success=success,
            reward=reward,
            namespace=self._namespace,
            metadata=metadata,
        )

        # Generate and store embedding
        embed_text = f"{task_type} {approach} {context}"
        embedding = self._embeddings.embed(embed_text)
        emb_bytes = self._embeddings.to_bytes(embedding)
        self._storage.store_embedding(
            "pattern_embeddings", pattern_id, emb_bytes,
            dimensions=self._embeddings.dimensions,
        )

        # Add to vector index
        self._vectors.insert(
            self._index_name,
            f"pat_{pattern_id}",
            pattern_id,
            embedding,
            {"task_type": task_type, "success": int(success), "reward": reward},
        )

        self._storage.log_event(
            agent_name="ReasoningBank",
            event_type="learning",
            content=f"Stored pattern for '{task_type}': {approach[:100]}",
            phase="store",
            namespace=self._namespace,
        )

        logger.info(f"Stored reasoning pattern {pattern_id} (type={task_type})")
        return pattern_id

    def search_patterns(
        self,
        query: str,
        k: int = 5,
        threshold: float = 0.1,
        task_type: Optional[str] = None,
        success_only: bool = False,
    ) -> List[ReasoningPattern]:
        """
        Search for relevant reasoning patterns.

        Args:
            query: Search query describing the task.
            k: Maximum results.
            threshold: Minimum similarity.
            task_type: Filter by task type.
            success_only: Only return successful patterns.

        Returns:
            List of matching reasoning patterns.
        """
        self._build_index()

        query_embedding = self._embeddings.embed(query)

        def filter_fn(meta):
            if success_only and meta.get("success", 0) != 1:
                return False
            if task_type and meta.get("task_type") != task_type:
                return False
            return True

        results: List[SearchResult] = self._vectors.get_index(self._index_name).search(
            query_embedding, k=k, threshold=threshold, filter_fn=filter_fn,
        )

        patterns = []
        for result in results:
            pat_data = self._storage.get_pattern(result.ref_id)
            if pat_data:
                patterns.append(ReasoningPattern(
                    id=pat_data["id"],
                    task_type=pat_data["task_type"],
                    approach=pat_data["approach"],
                    context=pat_data.get("context", ""),
                    outcome=pat_data.get("outcome", ""),
                    success=bool(pat_data["success"]),
                    reward=pat_data["reward"],
                    usage_count=pat_data["usage_count"],
                    success_count=pat_data["success_count"],
                    namespace=pat_data["namespace"],
                    metadata=pat_data.get("metadata_json", {}),
                    created_at=pat_data["created_at"],
                ))

                # Log access
                self._storage.log_memory_access(
                    "pattern", pat_data["id"], "search",
                    metadata={"query": query[:200], "similarity": result.similarity},
                )

        return patterns

    def record_outcome(
        self,
        pattern_id: int,
        success: bool,
        reward: float = 0.0,
    ) -> None:
        """
        Record the outcome of using a pattern.

        Args:
            pattern_id: Pattern ID.
            success: Whether the usage was successful.
            reward: Reward signal.
        """
        self._storage.update_pattern_stats(pattern_id, success, reward)
        logger.debug(f"Recorded outcome for pattern {pattern_id} (success={success})")

    def get_best_approach(
        self,
        task_type: str,
        context: str = "",
    ) -> Optional[ReasoningPattern]:
        """
        Get the best known reasoning approach for a task type.

        Combines semantic similarity with success rate to find
        the optimal approach.

        Args:
            task_type: Type of task.
            context: Current context.

        Returns:
            Best matching pattern, or None.
        """
        query = f"{task_type} {context}"
        patterns = self.search_patterns(
            query, k=10, task_type=task_type, success_only=True,
        )

        if not patterns:
            # Fall back to any pattern for this task type
            patterns = self.search_patterns(query, k=5, task_type=task_type)

        if not patterns:
            return None

        # Score by: success_rate * 0.6 + reward * 0.4
        best = max(
            patterns,
            key=lambda p: p.success_rate * 0.6 + p.reward * 0.4,
        )
        return best

    def delete_pattern(self, pattern_id: int) -> bool:
        """Delete a reasoning pattern."""
        conn = self._storage.connection
        cursor = conn.execute(
            "DELETE FROM reasoning_patterns WHERE id = ?", (pattern_id,)
        )
        conn.commit()
        self._vectors.remove(self._index_name, f"pat_{pattern_id}")
        return cursor.rowcount > 0

    def get_stats(self) -> Dict[str, Any]:
        """Get reasoning bank statistics."""
        patterns = self._storage.get_patterns(namespace=self._namespace, limit=10000)
        if not patterns:
            return {
                "total_patterns": 0,
                "task_types": [],
                "avg_reward": 0.0,
                "namespace": self._namespace,
            }

        task_types = list(set(p["task_type"] for p in patterns))
        return {
            "total_patterns": len(patterns),
            "task_types": task_types,
            "avg_reward": sum(p["reward"] for p in patterns) / len(patterns),
            "total_usage": sum(p["usage_count"] for p in patterns),
            "namespace": self._namespace,
            "vector_index_size": self._vectors.get_index(self._index_name).size,
        }
