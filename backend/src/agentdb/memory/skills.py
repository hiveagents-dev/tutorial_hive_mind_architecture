"""
SkillLibrary - Reusable learned skill patterns.

Successful episode patterns get consolidated into reusable, parameterized skills.
Skills have success rates, usage counts, and can be linked
(prerequisite, alternative, refinement, composition relationships).

Ported from the TypeScript AgentDB's SkillLibrary controller.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from ..storage import Storage
from ..embeddings import EmbeddingService
from ..vector_search import VectorSearchEngine, SearchResult

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """A reusable skill pattern."""
    id: int
    name: str
    description: str
    code: str
    signature: str
    success_rate: float
    usage_count: int
    namespace: str
    metadata: Dict[str, Any]
    created_at: str
    related_skills: List[Dict[str, Any]] = field(default_factory=list)


class SkillLibrary:
    """
    Library of reusable skill patterns learned from episodes.

    Provides:
    - Skill creation from successful task patterns
    - Semantic skill search
    - Skill linking (prerequisites, alternatives, refinements)
    - Automatic success rate tracking
    - Skill pruning based on usage and success
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
        self._index_name = f"skills_{namespace}"
        logger.info(f"SkillLibrary initialized (namespace={namespace})")

    def _build_index(self) -> None:
        """Rebuild vector index from stored skill embeddings."""
        idx = self._vectors.get_index(self._index_name)
        if idx.size > 0:
            return

        rows = self._storage.get_all_embeddings("skill_embeddings")
        for emb_id, skill_id, emb_bytes in rows:
            skill = self._storage.get_skill(skill_id)
            if skill and skill["namespace"] == self._namespace:
                vec = self._embeddings.from_bytes(emb_bytes)
                self._vectors.insert(
                    self._index_name,
                    f"sk_{skill_id}",
                    skill_id,
                    vec,
                    {"success_rate": skill["success_rate"], "usage_count": skill["usage_count"]},
                )

    def create_skill(
        self,
        name: str,
        description: str,
        code: str = "",
        signature: str = "",
        success_rate: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Create a new skill in the library.

        Args:
            name: Skill name.
            description: What the skill does.
            code: Skill implementation code or template.
            signature: Input/output signature.
            success_rate: Initial success rate.
            metadata: Additional metadata.

        Returns:
            Skill ID.
        """
        skill_id = self._storage.insert_skill(
            name=name,
            description=description,
            code=code,
            signature=signature,
            success_rate=success_rate,
            namespace=self._namespace,
            metadata=metadata,
        )

        # Generate and store embedding
        embed_text = f"{name} {description} {signature}"
        embedding = self._embeddings.embed(embed_text)
        emb_bytes = self._embeddings.to_bytes(embedding)
        self._storage.store_embedding(
            "skill_embeddings", skill_id, emb_bytes,
            dimensions=self._embeddings.dimensions,
        )

        # Add to vector index
        self._vectors.insert(
            self._index_name,
            f"sk_{skill_id}",
            skill_id,
            embedding,
            {"success_rate": success_rate, "usage_count": 0},
        )

        self._storage.log_event(
            agent_name="SkillLibrary",
            event_type="learning",
            content=f"Created skill '{name}' (id={skill_id})",
            phase="create",
            namespace=self._namespace,
        )

        logger.info(f"Created skill '{name}' (id={skill_id})")
        return skill_id

    def search_skills(
        self,
        query: str,
        k: int = 5,
        threshold: float = 0.1,
        min_success_rate: float = 0.0,
    ) -> List[Skill]:
        """
        Search skills by semantic similarity.

        Args:
            query: Search query.
            k: Max results.
            threshold: Minimum similarity.
            min_success_rate: Minimum skill success rate.

        Returns:
            List of matching skills.
        """
        self._build_index()

        query_embedding = self._embeddings.embed(query)

        filter_fn = None
        if min_success_rate > 0:
            filter_fn = lambda meta: meta.get("success_rate", 0) >= min_success_rate

        results: List[SearchResult] = self._vectors.get_index(self._index_name).search(
            query_embedding, k=k, threshold=threshold, filter_fn=filter_fn,
        )

        skills = []
        for result in results:
            skill_data = self._storage.get_skill(result.ref_id)
            if skill_data:
                # Get related skills
                related = self._get_related_skills(skill_data["id"])
                skills.append(Skill(
                    id=skill_data["id"],
                    name=skill_data["name"],
                    description=skill_data["description"] or "",
                    code=skill_data["code"] or "",
                    signature=skill_data["signature"] or "",
                    success_rate=skill_data["success_rate"],
                    usage_count=skill_data["usage_count"],
                    namespace=skill_data["namespace"],
                    metadata=skill_data.get("metadata_json", {}),
                    created_at=skill_data["created_at"],
                    related_skills=related,
                ))

        return skills

    def _get_related_skills(self, skill_id: int) -> List[Dict[str, Any]]:
        """Get skills related to a given skill."""
        rows = self._storage.connection.execute(
            """SELECT sl.*, s.name as target_name, s.description as target_description
               FROM skill_links sl
               JOIN skills s ON s.id = sl.target_skill_id
               WHERE sl.source_skill_id = ?""",
            (skill_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def link_skills(
        self,
        source_id: int,
        target_id: int,
        link_type: str,
        weight: float = 1.0,
    ) -> int:
        """
        Create a relationship between two skills.

        Args:
            source_id: Source skill ID.
            target_id: Target skill ID.
            link_type: One of 'prerequisite', 'alternative', 'refinement', 'composition'.
            weight: Relationship strength.

        Returns:
            Link ID.
        """
        return self._storage.insert_skill_link(source_id, target_id, link_type, weight)

    def record_usage(self, skill_id: int, success: bool) -> None:
        """Record a skill usage and update its success rate."""
        self._storage.update_skill_stats(skill_id, success)
        logger.debug(f"Recorded usage for skill {skill_id} (success={success})")

    def consolidate_from_episodes(
        self,
        episodes: List[Dict],
        min_success_rate: float = 0.7,
    ) -> List[int]:
        """
        Consolidate successful episodes into reusable skills.

        Examines a set of episodes and creates skills from patterns
        that appear in successful outcomes.

        Args:
            episodes: List of episode dicts.
            min_success_rate: Minimum success rate to create skill.

        Returns:
            List of created skill IDs.
        """
        successful = [ep for ep in episodes if ep.get("success")]
        if not successful:
            return []

        # Group by task similarity (simple prefix grouping)
        task_groups: Dict[str, List[Dict]] = {}
        for ep in successful:
            task_key = ep["task"][:50]  # Simple grouping by task prefix
            task_groups.setdefault(task_key, []).append(ep)

        created_ids = []
        for task_key, group in task_groups.items():
            success_rate = len(group) / max(
                len([e for e in episodes if e["task"][:50] == task_key]), 1
            )
            if success_rate >= min_success_rate and len(group) >= 2:
                # Create skill from the group
                best = max(group, key=lambda e: e.get("reward", 0))
                skill_id = self.create_skill(
                    name=f"Skill: {task_key}",
                    description=f"Learned from {len(group)} successful episodes",
                    code=best.get("output", ""),
                    signature=best.get("task", ""),
                    success_rate=success_rate,
                    metadata={"source_episodes": [e["id"] for e in group]},
                )
                created_ids.append(skill_id)

        logger.info(f"Consolidated {len(created_ids)} skills from {len(episodes)} episodes")
        return created_ids

    def prune_skills(
        self,
        min_usage: int = 0,
        min_success_rate: float = 0.0,
        max_skills: int = 500,
    ) -> int:
        """Prune underperforming or unused skills."""
        skills = self._storage.get_skills(namespace=self._namespace, limit=max_skills + 500)
        if len(skills) <= max_skills:
            return 0

        # Sort by quality score (success_rate * log(usage+1))
        import math
        skills.sort(key=lambda s: s["success_rate"] * math.log1p(s["usage_count"]))
        to_prune = skills[: len(skills) - max_skills]

        pruned = 0
        for sk in to_prune:
            if sk["usage_count"] <= min_usage or sk["success_rate"] <= min_success_rate:
                self._storage.connection.execute("DELETE FROM skills WHERE id = ?", (sk["id"],))
                self._vectors.remove(self._index_name, f"sk_{sk['id']}")
                pruned += 1

        if pruned:
            self._storage.connection.commit()

        logger.info(f"Pruned {pruned} skills from namespace {self._namespace}")
        return pruned

    def get_stats(self) -> Dict[str, Any]:
        """Get skill library statistics."""
        skills = self._storage.get_skills(namespace=self._namespace, limit=10000)
        if not skills:
            return {
                "total_skills": 0,
                "avg_success_rate": 0.0,
                "total_usage": 0,
                "namespace": self._namespace,
            }

        return {
            "total_skills": len(skills),
            "avg_success_rate": sum(s["success_rate"] for s in skills) / len(skills),
            "total_usage": sum(s["usage_count"] for s in skills),
            "namespace": self._namespace,
            "vector_index_size": self._vectors.get_index(self._index_name).size,
        }
