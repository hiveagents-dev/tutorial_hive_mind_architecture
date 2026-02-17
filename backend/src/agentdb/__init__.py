"""
AgentDB - Cognitive Memory System for AI Agents (Python Port)

A vector database and cognitive memory system designed for autonomous AI agents.
Provides persistent, self-improving memory that learns from every interaction.

Ported from: https://github.com/ruvnet/agentic-flow/tree/main/packages/agentdb

Core Components:
    - AgentDB: Main orchestrator class
    - Storage: SQLite persistence layer
    - EmbeddingService: Vector embedding generation
    - VectorSearchEngine: Cosine similarity search

Cognitive Memory Controllers:
    - ReflexionMemory: Episodic replay with self-critique
    - SkillLibrary: Reusable learned skill patterns
    - CausalMemoryGraph: Cause-effect relationship tracking
    - ReasoningBank: Reasoning pattern storage and retrieval

HiveMind Integration:
    - MemoryEnabledAgent: Wraps BaseAgent with memory capabilities
    - HiveMindMemoryManager: System-wide memory coordination
"""

from .core import AgentDB, AgentDBConfig
from .storage import Storage
from .embeddings import EmbeddingService
from .vector_search import VectorSearchEngine, VectorIndex, SearchResult
from .memory import ReflexionMemory, SkillLibrary, CausalMemoryGraph, ReasoningBank
from .integration import MemoryEnabledAgent, HiveMindMemoryManager

__version__ = "2.0.0-alpha.1"

__all__ = [
    # Core
    "AgentDB",
    "AgentDBConfig",
    # Storage
    "Storage",
    # Embeddings
    "EmbeddingService",
    # Vector Search
    "VectorSearchEngine",
    "VectorIndex",
    "SearchResult",
    # Memory Controllers
    "ReflexionMemory",
    "SkillLibrary",
    "CausalMemoryGraph",
    "ReasoningBank",
    # HiveMind Integration
    "MemoryEnabledAgent",
    "HiveMindMemoryManager",
]
