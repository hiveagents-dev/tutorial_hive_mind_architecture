"""
Embedding service for AgentDB.

Provides vector embeddings for text using multiple backends:
- sentence-transformers (local, high quality)
- Simple hash-based fallback (no dependencies, lower quality)

Ported from the TypeScript AgentDB's EmbeddingService.
"""

import hashlib
import logging
import struct
from abc import ABC, abstractmethod
from typing import List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base for embedding providers."""

    @abstractmethod
    def embed(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts."""
        pass

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Return the embedding dimensions."""
        pass


class SentenceTransformerProvider(EmbeddingProvider):
    """
    Embedding provider using sentence-transformers.

    Uses all-MiniLM-L6-v2 by default (384 dimensions),
    matching the original AgentDB TypeScript implementation.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self._model_name = model_name
        self._model = None
        self._dimensions = 384

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self._model_name)
                self._dimensions = self._model.get_sentence_embedding_dimension()
                logger.info(f"Loaded sentence-transformers model: {self._model_name} ({self._dimensions}d)")
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )

    def embed(self, text: str) -> np.ndarray:
        self._load_model()
        return self._model.encode(text, normalize_embeddings=True)

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        self._load_model()
        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return [embeddings[i] for i in range(len(texts))]

    @property
    def dimensions(self) -> int:
        return self._dimensions


class HashEmbeddingProvider(EmbeddingProvider):
    """
    Simple hash-based embedding provider.

    Uses SHA-256 hashing to generate deterministic pseudo-embeddings.
    Lower quality than ML models but requires zero dependencies.
    Useful for testing and lightweight deployments.
    """

    def __init__(self, dimensions: int = 384):
        self._dimensions = dimensions
        logger.info(f"Using HashEmbeddingProvider ({dimensions}d) - consider installing sentence-transformers for better quality")

    def _hash_to_vector(self, text: str) -> np.ndarray:
        """Generate a deterministic pseudo-embedding from text via n-gram hashing.

        Uses character-level n-grams (2,3,4-grams) to produce vectors
        where similar texts have higher cosine similarity.
        """
        vec = np.zeros(self._dimensions, dtype=np.float32)

        # Extract character n-grams (2, 3, 4-grams) for locality-sensitive hashing
        text_lower = text.lower().strip()
        ngrams = []
        for n in (2, 3, 4):
            for i in range(len(text_lower) - n + 1):
                ngrams.append(text_lower[i:i + n])

        # Also add individual words
        ngrams.extend(text_lower.split())

        # Hash each n-gram to a position in the vector
        for gram in ngrams:
            h = hashlib.sha256(gram.encode()).digest()
            # Use first 4 bytes as index, next byte for sign
            idx = int.from_bytes(h[:4], "big") % self._dimensions
            sign = 1.0 if h[4] % 2 == 0 else -1.0
            vec[idx] += sign

        # Normalize to unit vector
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        else:
            # Fallback for empty text
            h = hashlib.sha256(text.encode()).digest()
            for i in range(min(self._dimensions, 32)):
                vec[i] = (h[i % 32] - 128) / 128.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm

        return vec

    def embed(self, text: str) -> np.ndarray:
        return self._hash_to_vector(text)

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        return [self._hash_to_vector(t) for t in texts]

    @property
    def dimensions(self) -> int:
        return self._dimensions


class EmbeddingService:
    """
    Main embedding service with automatic provider selection.

    Tries to use sentence-transformers if available, falls back to
    hash-based embeddings.
    """

    def __init__(
        self,
        provider: Optional[str] = "auto",
        model_name: str = "all-MiniLM-L6-v2",
        dimensions: int = 384,
    ):
        """
        Initialize embedding service.

        Args:
            provider: "sentence-transformers", "hash", or "auto" (try ST, fallback to hash).
            model_name: Model name for sentence-transformers.
            dimensions: Vector dimensions (used for hash provider).
        """
        self._provider = self._create_provider(provider, model_name, dimensions)
        logger.info(f"EmbeddingService initialized with {self._provider.__class__.__name__}")

    def _create_provider(
        self, provider: str, model_name: str, dimensions: int
    ) -> EmbeddingProvider:
        if provider == "sentence-transformers":
            return SentenceTransformerProvider(model_name)
        elif provider == "hash":
            return HashEmbeddingProvider(dimensions)
        else:  # auto
            try:
                import sentence_transformers  # noqa: F401
                return SentenceTransformerProvider(model_name)
            except ImportError:
                logger.warning(
                    "sentence-transformers not available, using hash embeddings. "
                    "For better quality: pip install sentence-transformers"
                )
                return HashEmbeddingProvider(dimensions)

    def embed(self, text: str) -> np.ndarray:
        """Generate embedding for text."""
        return self._provider.embed(text)

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts."""
        return self._provider.embed_batch(texts)

    def to_bytes(self, embedding: np.ndarray) -> bytes:
        """Serialize embedding to bytes for storage."""
        return embedding.astype(np.float32).tobytes()

    def from_bytes(self, data: bytes, dimensions: Optional[int] = None) -> np.ndarray:
        """Deserialize embedding from bytes."""
        dims = dimensions or self.dimensions
        return np.frombuffer(data, dtype=np.float32)[:dims].copy()

    @property
    def dimensions(self) -> int:
        return self._provider.dimensions
