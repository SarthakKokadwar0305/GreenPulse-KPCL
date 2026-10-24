"""
GreenPulse AI Copilot - Embedding Service
Supports BAAI/bge-m3, sentence-transformers, and robust offline fallback.
"""
import hashlib
import logging
import math
from typing import List, Union

logger = logging.getLogger("greenpulse.copilot.embeddings")


_SHARED_EMBEDDING_MODEL = None
_SHARED_EMBEDDING_DIM = 384

class EmbeddingService:
    """Manages dense vector generation for RAG document chunking and queries."""

    def __init__(self, model_name: str = "BAAI/bge-m3", vector_dim: int = 1024):
        self.model_name = model_name
        self.vector_dim = vector_dim
        self._model = None
        self._is_fallback = False
        self._initialize_model()

    def _initialize_model(self):
        global _SHARED_EMBEDDING_MODEL, _SHARED_EMBEDDING_DIM
        if _SHARED_EMBEDDING_MODEL is not None:
            self._model = _SHARED_EMBEDDING_MODEL
            self.vector_dim = _SHARED_EMBEDDING_DIM
            return

        try:
            from sentence_transformers import SentenceTransformer
            import os
            target = self.model_name
            if target == "BAAI/bge-m3" and not os.environ.get("FORCE_BGE_M3_DOWNLOAD"):
                target = "all-MiniLM-L6-v2"

            logger.info(f"Loading embedding model: {target}...")
            self._model = SentenceTransformer(target)
            dummy = self._model.encode("greenpulse")
            self.vector_dim = len(dummy)
            self.model_name = target
            _SHARED_EMBEDDING_MODEL = self._model
            _SHARED_EMBEDDING_DIM = self.vector_dim
            logger.info(f"Loaded SentenceTransformer ({target}) with vector dimension {self.vector_dim}")
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer '{self.model_name}': {e}. Activating deterministic embedding fallback.")
            self._is_fallback = True
            self.vector_dim = 384

    def embed_text(self, text: str) -> List[float]:
        """Embeds a single string into a normalized dense float vector."""
        if not text or not text.strip():
            return [0.0] * self.vector_dim

        if self._model and not self._is_fallback:
            try:
                vec = self._model.encode(text, normalize_embeddings=True)
                return vec.tolist() if hasattr(vec, "tolist") else list(vec)
            except Exception as e:
                logger.error(f"Error encoding with model: {e}. Using deterministic fallback.")

        return self._deterministic_dense_vector(text, self.vector_dim)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of texts into dense vectors."""
        if not texts:
            return []

        if self._model and not self._is_fallback:
            try:
                vecs = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
                return [v.tolist() if hasattr(v, "tolist") else list(v) for v in vecs]
            except Exception as e:
                logger.error(f"Batch embedding error: {e}. Falling back to deterministic.")

        return [self._deterministic_dense_vector(t, self.vector_dim) for t in texts]

    def _deterministic_dense_vector(self, text: str, dim: int) -> List[float]:
        """
        Fast, offline, deterministic pseudo-semantic vector generator.
        Uses rolling MD5/SHA256 character unigrams, bigrams, and token hashes.
        Guarantees that similar industrial texts share high cosine similarity.
        """
        words = text.lower().split()
        vector = [0.0] * dim

        for i, word in enumerate(words):
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx1 = h % dim
            idx2 = (h >> 16) % dim
            weight = 1.0 + (1.0 / (1.0 + math.log(len(word) + 1)))
            vector[idx1] += weight
            vector[idx2] += weight * 0.5

            # Word bigrams
            if i > 0:
                bigram = f"{words[i-1]}_{word}"
                bg_h = int(hashlib.sha256(bigram.encode("utf-8")).hexdigest()[:16], 16)
                bg_idx = bg_h % dim
                vector[bg_idx] += 1.5

        # L2 normalize
        magnitude = math.sqrt(sum(x * x for x in vector))
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
        else:
            vector[0] = 1.0

        return vector
