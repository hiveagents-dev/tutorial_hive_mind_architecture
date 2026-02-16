"""
ReflexionMemory - Episodic memory with self-critique.

Based on the paper "Reflexion: Language Agents with Verbal Reinforcement Learning."
Agents store task attempts with outcomes, critiques, and rewards. On new tasks,
they retrieve semantically similar past episodes to learn from both successes
and failures.

Ported from the TypeScript AgentDB's ReflexionMemory controller.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from ..storage import Storage
from ..embeddings import EmbeddingService
from ..vector_search import VectorSearchEngine, SearchResult

logger = logging.getLogger(__name__)


@dataclass
class Episode:
    """An episodic memory entry."""
    id: int
    task: str
    input: str
    output: str
    critique: str
    reward: float
    success: bool
    namespace: str
    metadata: Dict[str, Any]
    created_at: str


@dataclass
class ReflexionResult:
    """Result from reflexion retrieval."""
    episodes: List[Episode]
    insights: List[str]
    avg_reward: float
    success_rate: float


class ReflexionMemory:
    """
    Episodic memory system with reflexion-style self-critique.

    Stores task execution episodes and retrieves semantically similar
    past experiences for learning. Supports:
    - Storing episodes with critique and reward signals
    - Semantic retrieval of relevant past episodes
    - Episode pruning based on age and quality
    - Success/failure analysis
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
        self._index_name = f"episodes_{namespace}"
        logger.info(f"ReflexionMemory initialized (namespace={namespace})")

    def _build_index(self) -> None:
        """Rebuild vector index from stored embeddings."""
        idx = self._vectors.get_index(self._index_name)
        if idx.size > 0:
            return  # Already populated

        rows = self._storage.get_all_embeddings("episode_embeddings")
        for emb_id, episode_id, emb_bytes in rows:
            episode = self._storage.get_episode(episode_id)
            if episode and episode["namespace"] == self._namespace:
                vec = self._embeddings.from_bytes(emb_bytes)
                self._vectors.insert(
                    self._index_name,
                    f"ep_{episode_id}",
                    episode_id,
                    vec,
                    {"success": episode["success"], "reward": episode["reward"]},
                )

    def store_episode(
        self,
        task: str,
        input_data: str,
        output: str,
        critique: str = "",
        reward: float = 0.0,
        success: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Store an episode in memory.

        Args:
            task: Task description.
            input_data: Input provided to the agent.
            output: Agent's output/response.
            critique: Self-critique or external feedback.
            reward: Reward signal (-1.0 to 1.0).
            success: Whether the task was successful.
            metadata: Additional metadata.

        Returns:
            Episode ID.
        """
        episode_id = self._storage.insert_episode(
            task=task,
            input_data=input_data,
            output=output,
            critique=critique,
            reward=reward,
            success=success,
            namespace=self._namespace,
            metadata=metadata,
        )

        # Generate and store embedding
        embed_text = f"{task} {input_data} {output}"
        embedding = self._embeddings.embed(embed_text)
        emb_bytes = self._embeddings.to_bytes(embedding)
        self._storage.store_embedding(
            "episode_embeddings", episode_id, emb_bytes,
            dimensions=self._embeddings.dimensions,
        )

        # Add to vector index
        self._vectors.insert(
            self._index_name,
            f"ep_{episode_id}",
            episode_id,
            embedding,
            {"success": int(success), "reward": reward},
        )

        # Log event
        self._storage.log_event(
            agent_name="ReflexionMemory",
            event_type="learning",
            content=f"Stored episode {episode_id}: {task[:100]}",
            phase="store",
            namespace=self._namespace,
            metadata={"episode_id": episode_id, "success": success, "reward": reward},
        )

        logger.info(f"Stored episode {episode_id} (success={success}, reward={reward:.2f})")
        return episode_id

    def retrieve_relevant(
        self,
        query: str,
        k: int = 5,
        threshold: float = 0.1,
        success_only: bool = False,
    ) -> ReflexionResult:
        """
        Retrieve episodes relevant to a query.

        Args:
            query: Search query (task description or context).
            k: Maximum number of episodes to return.
            threshold: Minimum similarity threshold.
            success_only: Only return successful episodes.

        Returns:
            ReflexionResult with episodes and insights.
        """
        self._build_index()

        query_embedding = self._embeddings.embed(query)

        filter_fn = None
        if success_only:
            filter_fn = lambda meta: meta.get("success", 0) == 1

        results: List[SearchResult] = self._vectors.get_index(self._index_name).search(
            query_embedding, k=k, threshold=threshold, filter_fn=filter_fn,
        )

        episodes = []
        for result in results:
            ep_data = self._storage.get_episode(result.ref_id)
            if ep_data:
                episodes.append(Episode(
                    id=ep_data["id"],
                    task=ep_data["task"],
                    input=ep_data["input"] or "",
                    output=ep_data["output"] or "",
                    critique=ep_data["critique"] or "",
                    reward=ep_data["reward"],
                    success=bool(ep_data["success"]),
                    namespace=ep_data["namespace"],
                    metadata=ep_data.get("metadata_json", {}),
                    created_at=ep_data["created_at"],
                ))

                # Log access
                self._storage.log_memory_access(
                    "episode", ep_data["id"], "search",
                    metadata={"query": query[:200], "similarity": result.similarity},
                )

        # Generate insights
        insights = self._generate_insights(episodes)

        # Calculate stats
        avg_reward = (
            sum(ep.reward for ep in episodes) / len(episodes) if episodes else 0.0
        )
        success_rate = (
            sum(1 for ep in episodes if ep.success) / len(episodes) if episodes else 0.0
        )

        return ReflexionResult(
            episodes=episodes,
            insights=insights,
            avg_reward=avg_reward,
            success_rate=success_rate,
        )

    def _generate_insights(self, episodes: List[Episode]) -> List[str]:
        """Generate insights from retrieved episodes."""
        if not episodes:
            return ["No prior episodes found for this task."]

        insights = []

        successes = [ep for ep in episodes if ep.success]
        failures = [ep for ep in episodes if not ep.success]

        if successes:
            insights.append(
                f"Found {len(successes)} successful similar episodes "
                f"(avg reward: {sum(e.reward for e in successes)/len(successes):.2f})."
            )
        if failures:
            insights.append(
                f"Found {len(failures)} failed similar episodes. "
                f"Common critiques: {'; '.join(e.critique[:80] for e in failures[:3] if e.critique)}"
            )

        # Critique summary
        critiques = [ep.critique for ep in episodes if ep.critique]
        if critiques:
            insights.append(f"Key feedback from past attempts: {critiques[0][:200]}")

        return insights

    def prune_episodes(
        self,
        max_episodes: int = 1000,
        min_reward: float = -1.0,
    ) -> int:
        """
        Prune low-quality episodes to manage memory size.

        Args:
            max_episodes: Maximum episodes to keep.
            min_reward: Minimum reward to keep an episode.

        Returns:
            Number of episodes pruned.
        """
        episodes = self._storage.get_episodes(
            namespace=self._namespace, limit=max_episodes + 1000
        )

        if len(episodes) <= max_episodes:
            return 0

        # Sort by reward (keep highest) and creation date (keep newest)
        episodes.sort(key=lambda e: (e["reward"], e["created_at"]))
        to_prune = episodes[: len(episodes) - max_episodes]

        pruned = 0
        for ep in to_prune:
            if ep["reward"] < min_reward or pruned < len(to_prune):
                self._storage.delete_episode(ep["id"])
                self._vectors.remove(self._index_name, f"ep_{ep['id']}")
                pruned += 1

        logger.info(f"Pruned {pruned} episodes from namespace {self._namespace}")
        return pruned

    def get_stats(self) -> Dict[str, Any]:
        """Get reflexion memory statistics."""
        episodes = self._storage.get_episodes(namespace=self._namespace, limit=10000)
        if not episodes:
            return {
                "total_episodes": 0,
                "success_rate": 0.0,
                "avg_reward": 0.0,
                "namespace": self._namespace,
            }

        return {
            "total_episodes": len(episodes),
            "success_rate": sum(1 for e in episodes if e["success"]) / len(episodes),
            "avg_reward": sum(e["reward"] for e in episodes) / len(episodes),
            "namespace": self._namespace,
            "vector_index_size": self._vectors.get_index(self._index_name).size,
        }
