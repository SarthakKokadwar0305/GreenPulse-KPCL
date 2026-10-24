"""
GreenPulse AI Copilot - Qdrant Vector Store Service
Manages local embedded or remote Qdrant vector database across partitioned collections.
Enables incremental indexing, chunk similarity search, and source provenance.
"""
import logging
import os
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

logger = logging.getLogger("greenpulse.copilot.vector_store")

COLLECTIONS = [
    "company_sops",
    "machine_manuals",
    "government_schemes",
    "iso_50001",
    "maintenance_docs",
    "energy_policies",
    "industrial_standards",
    "uploaded_pdfs",
]


_SHARED_QDRANT_CLIENT = None

def get_shared_qdrant_client(storage_path: Path) -> QdrantClient:
    global _SHARED_QDRANT_CLIENT
    if _SHARED_QDRANT_CLIENT is None:
        qdrant_url = os.getenv("QDRANT_URL")
        if qdrant_url:
            api_key = os.getenv("QDRANT_API_KEY")
            try:
                _SHARED_QDRANT_CLIENT = QdrantClient(url=qdrant_url, api_key=api_key)
                logger.info(f"Qdrant client connected to remote instance at: {qdrant_url}")
            except Exception as e:
                logger.warning(f"Could not connect to Qdrant at {qdrant_url}: {e}. Falling back to disk storage.")
                _SHARED_QDRANT_CLIENT = None
        if _SHARED_QDRANT_CLIENT is None:
            try:
                storage_path.mkdir(parents=True, exist_ok=True)
                _SHARED_QDRANT_CLIENT = QdrantClient(path=str(storage_path))
                logger.info(f"Qdrant client initialized with local disk storage at: {storage_path.resolve()}")
            except Exception as e:
                logger.warning(f"Could not initialize local disk Qdrant storage: {e}. Using in-memory Qdrant instance.")
                _SHARED_QDRANT_CLIENT = QdrantClient(location=":memory:")
    return _SHARED_QDRANT_CLIENT


class VectorStoreService:
    """Encapsulates Qdrant client, collections management, and vector similarity search."""

    def __init__(self, storage_path: str = "./qdrant_storage", vector_dim: int = 384):
        self.storage_path = Path(storage_path)
        self.vector_dim = vector_dim
        self.client = get_shared_qdrant_client(self.storage_path)
        self._ensure_collections()

    def update_vector_dim(self, new_dim: int):
        """Updates vector dimension if embedding model changes."""
        if self.vector_dim != new_dim:
            self.vector_dim = new_dim
            self._ensure_collections()

    def _ensure_collections(self):
        """Ensures all required industrial knowledge collections exist with proper distance metric."""
        try:
            existing = {c.name for c in self.client.get_collections().collections}
        except Exception:
            existing = set()

        for col in COLLECTIONS:
            if col not in existing:
                try:
                    self.client.create_collection(
                        collection_name=col,
                        vectors_config=qmodels.VectorParams(
                            size=self.vector_dim,
                            distance=qmodels.Distance.COSINE
                        )
                    )
                    logger.info(f"Created Qdrant collection: {col} (dim={self.vector_dim})")
                except Exception as e:
                    logger.error(f"Failed to create collection '{col}': {e}")

    def insert_chunks(
        self,
        collection_name: str,
        chunks: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        batch_size: int = 64
    ) -> int:
        """Inserts vector points with document metadata into the specified collection."""
        if collection_name not in COLLECTIONS:
            # Dynamically create if needed
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=qmodels.VectorParams(
                    size=self.vector_dim,
                    distance=qmodels.Distance.COSINE
                )
            )

        total_inserted = 0
        points = []

        for i, (chunk, emb, meta) in enumerate(zip(chunks, embeddings, metadatas)):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{meta.get('doc_id', 'doc')}_{meta.get('chunk_id', i)}"))
            payload = {
                "text": chunk,
                "collection": collection_name,
                **meta
            }
            points.append(
                qmodels.PointStruct(
                    id=point_id,
                    vector=emb,
                    payload=payload
                )
            )

            if len(points) >= batch_size:
                self.client.upsert(collection_name=collection_name, points=points)
                total_inserted += len(points)
                points = []

        if points:
            self.client.upsert(collection_name=collection_name, points=points)
            total_inserted += len(points)

        logger.info(f"Inserted {total_inserted} chunks into collection '{collection_name}'")
        return total_inserted

    def search(
        self,
        query_vector: List[float],
        collection_name: Optional[str] = None,
        top_k: int = 4,
        min_score: float = 0.35
    ) -> List[Dict[str, Any]]:
        """
        Performs vector similarity search.
        If collection_name is provided, queries that collection.
        If None, queries across all active collections and returns aggregated top results.
        """
        targets = [collection_name] if collection_name and collection_name in COLLECTIONS else COLLECTIONS
        all_results = []

        for col in targets:
            try:
                hits = self.client.query_points(
                    collection_name=col,
                    query=query_vector,
                    limit=top_k,
                    score_threshold=min_score
                ).points
                for hit in hits:
                    all_results.append({
                        "id": hit.id,
                        "score": hit.score,
                        "text": hit.payload.get("text", ""),
                        "document": hit.payload.get("document_name", "Unknown Document"),
                        "page": hit.payload.get("page", 1),
                        "collection": col,
                        "doc_id": hit.payload.get("doc_id", ""),
                        "section": hit.payload.get("section", ""),
                    })
            except Exception as e:
                logger.debug(f"Search in '{col}' skipped: {e}")

        # Sort aggregated results by similarity score descending
        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:top_k]

    def get_collections_summary(self) -> List[Dict[str, Any]]:
        """Returns statistics on all collections and indexed document count."""
        summary = []
        for col in COLLECTIONS:
            try:
                info = self.client.get_collection(collection_name=col)
                summary.append({
                    "name": col,
                    "title": col.replace("_", " ").title(),
                    "vectors_count": info.points_count or 0,
                    "status": "ready"
                })
            except Exception:
                summary.append({
                    "name": col,
                    "title": col.replace("_", " ").title(),
                    "vectors_count": 0,
                    "status": "empty"
                })
        return summary
