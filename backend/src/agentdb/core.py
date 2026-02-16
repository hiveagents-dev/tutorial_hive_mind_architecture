"""
AgentDB Core - Main orchestrator class.

Central entry point that initializes and coordinates all AgentDB subsystems:
storage, embeddings, vector search, and cognitive memory controllers.

Ported from the TypeScript AgentDB's core/AgentDB.ts.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .storage import Storage
from .embeddings import EmbeddingService
from .vector_search import VectorSearchEngine
from .memory.reflexion import ReflexionMemory
from .memory.skills import SkillLibrary
from .memory.causal import CausalMemoryGraph
from .memory.reasoning import ReasoningBank

logger = logging.getLogger(__name__)


@dataclass
class AgentDBConfig:
    """Configuration for AgentDB."""
    path: str = "agentdb.sqlite"
    namespace: str = "default"
    embedding_provider: str = "auto"
    embedding_model: str = "all-MiniLM-L6-v2"
    dimensions: int = 384


class AgentDB:
    """
    Main AgentDB orchestrator.

    Provides a unified interface to all cognitive memory subsystems.
    Initialize once and access controllers via properties.

    Usage:
        db = AgentDB(AgentDBConfig(path="my_agents.sqlite"))
        db.initialize()

        # Store an episode
        db.reflexion.store_episode(task="analyze data", ...)

        # Search skills
        skills = db.skills.search_skills("data analysis")

        # Track causality
        db.causal.add_causal_edge("data_cleaning", "better_accuracy")

        # Store reasoning patterns
        db.reasoning.store_pattern(task_type="analysis", approach="...")

        db.close()
    """

    def __init__(self, config: Optional[AgentDBConfig] = None):
        """
        Initialize AgentDB.

        Args:
            config: Configuration. Uses defaults if not provided.
        """
        self._config = config or AgentDBConfig()
        self._storage: Optional[Storage] = None
        self._embeddings: Optional[EmbeddingService] = None
        self._vector_engine: Optional[VectorSearchEngine] = None
        self._reflexion: Optional[ReflexionMemory] = None
        self._skills: Optional[SkillLibrary] = None
        self._causal: Optional[CausalMemoryGraph] = None
        self._reasoning: Optional[ReasoningBank] = None
        self._initialized = False

    def initialize(self) -> "AgentDB":
        """
        Initialize all subsystems. Must be called before using controllers.

        Returns:
            self (for chaining).
        """
        if self._initialized:
            return self

        logger.info(f"Initializing AgentDB (path={self._config.path}, namespace={self._config.namespace})")

        # Initialize storage
        self._storage = Storage(self._config.path)
        self._storage.initialize()

        # Initialize embeddings
        self._embeddings = EmbeddingService(
            provider=self._config.embedding_provider,
            model_name=self._config.embedding_model,
            dimensions=self._config.dimensions,
        )

        # Initialize vector search
        self._vector_engine = VectorSearchEngine(self._config.dimensions)

        # Initialize controllers
        self._reflexion = ReflexionMemory(
            self._storage, self._embeddings, self._vector_engine,
            namespace=self._config.namespace,
        )
        self._skills = SkillLibrary(
            self._storage, self._embeddings, self._vector_engine,
            namespace=self._config.namespace,
        )
        self._causal = CausalMemoryGraph(
            self._storage, namespace=self._config.namespace,
        )
        self._reasoning = ReasoningBank(
            self._storage, self._embeddings, self._vector_engine,
            namespace=self._config.namespace,
        )

        self._initialized = True
        logger.info("AgentDB initialized successfully")
        return self

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            raise RuntimeError("AgentDB not initialized. Call initialize() first.")

    @property
    def reflexion(self) -> ReflexionMemory:
        """Access the ReflexionMemory controller."""
        self._ensure_initialized()
        return self._reflexion

    @property
    def skills(self) -> SkillLibrary:
        """Access the SkillLibrary controller."""
        self._ensure_initialized()
        return self._skills

    @property
    def causal(self) -> CausalMemoryGraph:
        """Access the CausalMemoryGraph controller."""
        self._ensure_initialized()
        return self._causal

    @property
    def reasoning(self) -> ReasoningBank:
        """Access the ReasoningBank controller."""
        self._ensure_initialized()
        return self._reasoning

    @property
    def storage(self) -> Storage:
        """Access the raw storage layer."""
        self._ensure_initialized()
        return self._storage

    @property
    def embeddings(self) -> EmbeddingService:
        """Access the embedding service."""
        self._ensure_initialized()
        return self._embeddings

    def get_namespace(self) -> str:
        """Get the current namespace."""
        return self._config.namespace

    def create_namespaced(self, namespace: str) -> "AgentDB":
        """
        Create a new AgentDB instance sharing storage but with a different namespace.

        Useful for giving each agent its own isolated memory space
        while sharing the same database file.

        Args:
            namespace: New namespace name.

        Returns:
            New AgentDB instance.
        """
        self._ensure_initialized()

        namespaced = AgentDB.__new__(AgentDB)
        namespaced._config = AgentDBConfig(
            path=self._config.path,
            namespace=namespace,
            embedding_provider=self._config.embedding_provider,
            embedding_model=self._config.embedding_model,
            dimensions=self._config.dimensions,
        )
        namespaced._storage = self._storage  # Share storage
        namespaced._embeddings = self._embeddings  # Share embeddings
        namespaced._vector_engine = self._vector_engine  # Share vector engine

        # Create controllers with new namespace
        namespaced._reflexion = ReflexionMemory(
            self._storage, self._embeddings, self._vector_engine,
            namespace=namespace,
        )
        namespaced._skills = SkillLibrary(
            self._storage, self._embeddings, self._vector_engine,
            namespace=namespace,
        )
        namespaced._causal = CausalMemoryGraph(
            self._storage, namespace=namespace,
        )
        namespaced._reasoning = ReasoningBank(
            self._storage, self._embeddings, self._vector_engine,
            namespace=namespace,
        )
        namespaced._initialized = True

        logger.info(f"Created namespaced AgentDB (namespace={namespace})")
        return namespaced

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics across all subsystems."""
        self._ensure_initialized()
        return {
            "config": {
                "path": self._config.path,
                "namespace": self._config.namespace,
                "dimensions": self._config.dimensions,
            },
            "storage": self._storage.get_stats(),
            "reflexion": self._reflexion.get_stats(),
            "skills": self._skills.get_stats(),
            "causal": self._causal.get_stats(),
            "reasoning": self._reasoning.get_stats(),
            "vector_engine": self._vector_engine.get_stats(),
        }

    def optimize(self) -> None:
        """Run storage optimization (ANALYZE + VACUUM)."""
        self._ensure_initialized()
        self._storage.optimize()

    def close(self) -> None:
        """Close all connections and clean up."""
        if self._storage:
            self._storage.close()
        self._initialized = False
        logger.info("AgentDB closed")

    def __enter__(self) -> "AgentDB":
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __repr__(self) -> str:
        status = "initialized" if self._initialized else "not initialized"
        return f"AgentDB(path={self._config.path!r}, namespace={self._config.namespace!r}, {status})"
