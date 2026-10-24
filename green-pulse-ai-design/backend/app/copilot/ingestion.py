"""
GreenPulse AI Copilot - Document Ingestion Pipeline
Supports PDF (PyMuPDF), DOCX (python-docx), TXT, and Markdown.
Implements text chunking, page-level citation metadata, and incremental indexing.
"""
import hashlib
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    class RecursiveCharacterTextSplitter:  # type: ignore
        def __init__(self, chunk_size: int = 650, chunk_overlap: int = 100, separators: Optional[List[str]] = None):
            self.chunk_size = chunk_size
            self.chunk_overlap = chunk_overlap

        def split_text(self, text: str) -> List[str]:
            chunks = []
            start = 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                chunks.append(text[start:end])
                if end == len(text):
                    break
                start += max(1, self.chunk_size - self.chunk_overlap)
            return chunks

from app.copilot.embeddings import EmbeddingService
from app.copilot.vector_store import VectorStoreService, COLLECTIONS

logger = logging.getLogger("greenpulse.copilot.ingestion")


class DocumentIngestionPipeline:
    """Manages document extraction, chunking, embedding generation, and indexing into Qdrant."""

    def __init__(
        self,
        vector_store: VectorStoreService,
        embedding_service: EmbeddingService,
        chunk_size: int = 650,
        chunk_overlap: int = 100
    ):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "]
        )
        self._indexed_hashes: Dict[str, str] = {}

    def extract_text_from_file(self, file_path: Path) -> List[Tuple[str, int, str]]:
        """
        Extracts content from PDF, DOCX, TXT, or Markdown.
        Returns list of (text_content, page_number, section_hint).
        """
        suffix = file_path.suffix.lower()
        extracted: List[Tuple[str, int, str]] = []

        if suffix == ".pdf":
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(str(file_path))
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text()
                    if text.strip():
                        extracted.append((text, page_num + 1, f"Page {page_num + 1}"))
                doc.close()
            except Exception as e:
                logger.error(f"Failed to extract PDF '{file_path.name}': {e}")

        elif suffix == ".docx":
            try:
                import docx
                doc = docx.Document(str(file_path))
                current_text = []
                current_heading = "General"
                page_est = 1
                for para in doc.paragraphs:
                    if para.style.name.startswith("Heading"):
                        current_heading = para.text
                    if para.text.strip():
                        current_text.append(para.text)
                    if len(" ".join(current_text)) > 2500:
                        extracted.append(("\n".join(current_text), page_est, current_heading))
                        current_text = []
                        page_est += 1
                if current_text:
                    extracted.append(("\n".join(current_text), page_est, current_heading))
            except Exception as e:
                logger.error(f"Failed to extract DOCX '{file_path.name}': {e}")

        elif suffix in [".txt", ".md", ".markdown"]:
            try:
                content = file_path.read_text(encoding="utf-8")
                # Parse markdown pseudo-pages or split by level-2 headers
                sections = content.split("\n## ")
                for i, sec in enumerate(sections):
                    page_num = i + 1
                    section_title = sec.split("\n")[0] if i > 0 else "Introduction"
                    full_sec_text = f"## {sec}" if i > 0 else sec
                    if full_sec_text.strip():
                        extracted.append((full_sec_text, page_num, section_title))
            except Exception as e:
                logger.error(f"Failed to extract text from '{file_path.name}': {e}")

        else:
            logger.warning(f"Unsupported file type: {suffix} for file {file_path.name}")

        return extracted

    def compute_file_hash(self, file_path: Path) -> str:
        """Computes SHA-256 hash of file contents for incremental indexing."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def ingest_document(
        self,
        file_path: Path,
        collection_name: str,
        doc_name: Optional[str] = None
    ) -> int:
        """Ingests a single document into the designated Qdrant collection."""
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return 0

        file_hash = self.compute_file_hash(file_path)
        cache_key = f"{collection_name}:{file_path.name}"

        # Incremental indexing check: skip if file hash matches previous indexing
        if self._indexed_hashes.get(cache_key) == file_hash:
            logger.info(f"Skipping unmodified document: {file_path.name}")
            return 0

        pages_data = self.extract_text_from_file(file_path)
        if not pages_data:
            logger.warning(f"No text extracted from: {file_path.name}")
            return 0

        document_title = doc_name or file_path.stem.replace("_", " ").title()
        doc_id = hashlib.md5(file_path.name.encode()).hexdigest()[:12]

        all_chunks: List[str] = []
        all_metas: List[Dict[str, Any]] = []

        chunk_counter = 0
        for page_text, page_num, section in pages_data:
            sub_chunks = self.text_splitter.split_text(page_text)
            for sub_chunk in sub_chunks:
                if len(sub_chunk.strip()) > 30:
                    all_chunks.append(sub_chunk)
                    all_metas.append({
                        "doc_id": doc_id,
                        "chunk_id": chunk_counter,
                        "document_name": document_title,
                        "filename": file_path.name,
                        "page": page_num,
                        "section": section,
                        "collection": collection_name,
                        "hash": file_hash[:16],
                    })
                    chunk_counter += 1

        if not all_chunks:
            return 0

        # Generate dense embeddings
        embeddings = self.embedding_service.embed_batch(all_chunks)

        # Upsert to Qdrant
        inserted = self.vector_store.insert_chunks(
            collection_name=collection_name,
            chunks=all_chunks,
            embeddings=embeddings,
            metadatas=all_metas
        )

        self._indexed_hashes[cache_key] = file_hash
        logger.info(f"Successfully indexed '{file_path.name}' -> {inserted} chunks into collection '{collection_name}'")
        return inserted

    def ingest_knowledge_directory(self, base_dir: Path) -> Dict[str, int]:
        """Scans knowledge_documents directory and indexes all seed collections."""
        results = {}
        if not base_dir.exists():
            logger.warning(f"Directory {base_dir} does not exist. Creating...")
            base_dir.mkdir(parents=True, exist_ok=True)
            return results

        logger.info(f"Scanning and indexing knowledge directory: {base_dir.resolve()}...")

        # Walk through subdirectories mapping to collection names
        for item in base_dir.iterdir():
            if item.is_dir():
                collection_name = item.name.lower()
                if collection_name in COLLECTIONS:
                    count = 0
                    for doc_file in item.iterdir():
                        if doc_file.is_file() and doc_file.suffix.lower() in [".pdf", ".docx", ".txt", ".md", ".markdown"]:
                            count += self.ingest_document(doc_file, collection_name)
                    results[collection_name] = count

        return results
