"""
Vector similarity search engine for AgentDB.

Provides brute-force cosine similarity search using numpy.
Ported from the TypeScript AgentDB's WASMVectorSearch / VectorBackend.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result from a vector similarity search."""
    id: str
    ref_id: int
    distance: float
    similarity: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class VectorIndex:
    """
    In-memory vector index with cosine similarity search.

    Stores vectors in a numpy matrix for efficient batch computation.
    Supports insert, search, remove, and batch operations.
    """

    def __init__(self, dimensions: int = 384):
        """
        Initialize vector index.

        Args:
            dimensions: Number of dimensions per vector.
        """
        self.dimensions = dimensions
        self._ids: List[str] = []
        self._ref_ids: List[int] = []
        self._vectors: Optional[np.ndarray] = None  # (N, D) matrix
        self._metadata: List[Dict[str, Any]] = []
        logger.info(f"VectorIndex initialized ({dimensions}d)")

    @property
    def size(self) -> int:
        """Number of vectors in the index."""
        return len(self._ids)

    def insert(
        self,
        id: str,
        ref_id: int,
        embedding: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Insert a vector into the index.

        Args:
            id: Unique identifier for this vector.
            ref_id: Reference ID to the source record.
            embedding: Vector embedding (normalized preferred).
            metadata: Optional metadata.
        """
        vec = embedding.astype(np.float32).reshape(1, -1)
        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        self._ids.append(id)
        self._ref_ids.append(ref_id)
        self._metadata.append(metadata or {})

        if self._vectors is None:
            self._vectors = vec
        else:
            self._vectors = np.vstack([self._vectors, vec])

    def insert_batch(
        self,
        items: List[Dict],
    ) -> None:
        """
        Insert multiple vectors at once.

        Args:
            items: List of dicts with keys: id, ref_id, embedding, metadata (optional).
        """
        for item in items:
            self.insert(
                id=item["id"],
                ref_id=item["ref_id"],
                embedding=item["embedding"],
                metadata=item.get("metadata"),
            )

    def search(
        self,
        query: np.ndarray,
        k: int = 10,
        threshold: float = 0.0,
        filter_fn: Optional[callable] = None,
    ) -> List[SearchResult]:
        """
        Search for the k most similar vectors.

        Args:
            query: Query vector.
            k: Number of results to return.
            threshold: Minimum similarity threshold (0.0 to 1.0).
            filter_fn: Optional function(metadata) -> bool to filter results.

        Returns:
            List of SearchResult sorted by similarity (descending).
        """
        if self._vectors is None or self.size == 0:
            return []

        # Normalize query
        q = query.astype(np.float32).reshape(1, -1)
        norm = np.linalg.norm(q)
        if norm > 0:
            q = q / norm

        # Cosine similarity = dot product (since vectors are normalized)
        similarities = (self._vectors @ q.T).flatten()

        # Get indices sorted by similarity (descending)
        sorted_indices = np.argsort(-similarities)

        results = []
        for idx in sorted_indices:
            sim = float(similarities[idx])
            if sim < threshold:
                break
            if filter_fn and not filter_fn(self._metadata[idx]):
                continue
            results.append(
                SearchResult(
                    id=self._ids[idx],
                    ref_id=self._ref_ids[idx],
                    distance=1.0 - sim,
                    similarity=sim,
                    metadata=self._metadata[idx],
                )
            )
            if len(results) >= k:
                break

        return results

    def remove(self, id: str) -> bool:
        """
        Remove a vector by ID.

        Args:
            id: The vector ID to remove.

        Returns:
            True if found and removed.
        """
        if id not in self._ids:
            return False
        idx = self._ids.index(id)
        self._ids.pop(idx)
        self._ref_ids.pop(idx)
        self._metadata.pop(idx)
        if self._vectors is not None:
            self._vectors = np.delete(self._vectors, idx, axis=0)
            if self._vectors.shape[0] == 0:
                self._vectors = None
        return True

    def clear(self) -> None:
        """Remove all vectors from the index."""
        self._ids.clear()
        self._ref_ids.clear()
        self._metadata.clear()
        self._vectors = None

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "total_vectors": self.size,
            "dimensions": self.dimensions,
            "memory_bytes": self._vectors.nbytes if self._vectors is not None else 0,
        }


class VectorSearchEngine:
    """
    Multi-namespace vector search engine.

    Manages separate VectorIndex instances per namespace, allowing
    isolated vector spaces for different agent contexts.
    """

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions
        self._indices: Dict[str, VectorIndex] = {}

    def get_index(self, namespace: str = "default") -> VectorIndex:
        """Get or create index for namespace."""
        if namespace not in self._indices:
            self._indices[namespace] = VectorIndex(self.dimensions)
        return self._indices[namespace]

    def insert(
        self,
        namespace: str,
        id: str,
        ref_id: int,
        embedding: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Insert vector into namespace index."""
        self.get_index(namespace).insert(id, ref_id, embedding, metadata)

    def search(
        self,
        namespace: str,
        query: np.ndarray,
        k: int = 10,
        threshold: float = 0.0,
    ) -> List[SearchResult]:
        """Search within a namespace."""
        return self.get_index(namespace).search(query, k, threshold)

    def remove(self, namespace: str, id: str) -> bool:
        """Remove vector from namespace."""
        if namespace in self._indices:
            return self._indices[namespace].remove(id)
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get stats across all namespaces."""
        return {
            ns: idx.get_stats() for ns, idx in self._indices.items()
        }
