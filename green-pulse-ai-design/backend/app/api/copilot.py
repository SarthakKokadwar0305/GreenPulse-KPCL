"""
GreenPulse AI Copilot - API Router
FastAPI endpoints for AI Copilot chat, document ingestion, vector collections, and session memory.
Fully authenticated and role-aware under Enterprise RBAC.
"""
import shutil
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.copilot.copilot_service import CopilotService
from app.copilot.session_memory import session_memory
from app.copilot.vector_store import VectorStoreService, COLLECTIONS

router = APIRouter(prefix="/copilot", tags=["AI Copilot"])


# Schemas
class CopilotChatRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1500, description="Natural language question or command")
    session_id: Optional[str] = Field(None, description="Client session identifier for multi-turn conversation memory")


class CitationItem(BaseModel):
    document: str
    page: int
    section: Optional[str] = None
    collection: str
    relevance_score: float


class CopilotChatResponse(BaseModel):
    query: str
    session_id: str
    intent: str
    is_live_data: bool
    role_applied: str
    response: str
    citations: List[CitationItem] = []
    model_used: str


class CollectionInfo(BaseModel):
    name: str
    title: str
    vectors_count: int
    status: str


class IngestionResponse(BaseModel):
    filename: str
    collection: str
    chunks_indexed: int
    status: str


@router.post(
    "/chat",
    response_model=ApiResponse[CopilotChatResponse],
    summary="Chat with Industrial AI Copilot",
    description="Ask questions combining live SCADA telemetry, RAG documents (SOPs, OEM manuals), and industrial AI knowledge."
)
async def chat_with_copilot(
    payload: CopilotChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[CopilotChatResponse]:
    session_id = payload.session_id or str(uuid.uuid4())
    copilot_service = CopilotService(db=db, user=current_user)

    result = await copilot_service.answer_query(
        query=payload.query,
        session_id=session_id
    )

    data = CopilotChatResponse(
        query=result["query"],
        session_id=result["session_id"],
        intent=result["intent"],
        is_live_data=result["is_live_data"],
        role_applied=result["role_applied"],
        response=result["response"],
        citations=[CitationItem(**c) for c in result["citations"]],
        model_used=result["model_used"]
    )

    return ApiResponse.ok(data=data, message="Copilot response generated successfully.")


@router.get(
    "/collections",
    response_model=ApiResponse[List[CollectionInfo]],
    summary="List Knowledge Collections in Vector Database",
    description="Returns list of partitioned knowledge bases in Qdrant with indexed chunk counts."
)
async def list_collections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[List[CollectionInfo]]:
    copilot_service = CopilotService(db=db, user=current_user)
    collections = copilot_service.vector_store.get_collections_summary()
    return ApiResponse.ok(
        data=[CollectionInfo(**c) for c in collections],
        message="Knowledge collections fetched successfully."
    )


@router.post(
    "/upload",
    response_model=ApiResponse[IngestionResponse],
    summary="Ingest Document into Vector Database",
    description="Uploads and splits PDF, DOCX, TXT, or MD files, generates embeddings, and stores in Qdrant."
)
async def upload_and_ingest_document(
    file: UploadFile = File(...),
    collection: str = Form("uploaded_pdfs"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[IngestionResponse]:
    # Operators are restricted from uploading general knowledge documents
    if current_user.role == "OPERATOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Document ingestion requires Engineering or Plant Management role."
        )

    target_collection = collection if collection in COLLECTIONS else "uploaded_pdfs"
    upload_dir = Path("./uploaded_documents") / target_collection
    upload_dir.mkdir(parents=True, exist_ok=True)

    dest_file = upload_dir / file.filename
    with open(dest_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    copilot_service = CopilotService(db=db, user=current_user)
    chunks_count = copilot_service.ingestion_pipeline.ingest_document(
        file_path=dest_file,
        collection_name=target_collection,
        doc_name=file.filename
    )

    data = IngestionResponse(
        filename=file.filename,
        collection=target_collection,
        chunks_indexed=chunks_count,
        status="indexed" if chunks_count > 0 else "skipped_or_empty"
    )

    return ApiResponse.ok(data=data, message=f"Document '{file.filename}' processed: {chunks_count} chunks indexed.")


@router.get(
    "/history/{session_id}",
    response_model=ApiResponse[List[Dict[str, Any]]],
    summary="Get Multi-Turn Session Memory",
    description="Returns previous conversation history for the specified session ID."
)
async def get_session_history(
    session_id: str,
    current_user: User = Depends(get_current_user)
) -> ApiResponse[List[Dict[str, Any]]]:
    history = session_memory.get_history(session_id)
    return ApiResponse.ok(data=history, message="Session history retrieved.")


@router.delete(
    "/history/{session_id}",
    response_model=ApiResponse[Dict[str, bool]],
    summary="Clear Session Memory",
    description="Flushes in-memory dialogue turns for the specified session ID."
)
async def clear_session_history(
    session_id: str,
    current_user: User = Depends(get_current_user)
) -> ApiResponse[Dict[str, bool]]:
    session_memory.clear_session(session_id)
    return ApiResponse.ok(data={"cleared": True}, message=f"Session '{session_id}' cleared.")


@router.post(
    "/reindex",
    response_model=ApiResponse[Dict[str, int]],
    summary="Re-index Knowledge Seed Documents",
    description="Scans the knowledge_documents directory and incrementally updates all Qdrant collections."
)
async def reindex_knowledge_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[Dict[str, int]]:
    copilot_service = CopilotService(db=db, user=current_user)
    knowledge_dir = Path(settings.DOCUMENTS_DIR)
    results = copilot_service.ingestion_pipeline.ingest_knowledge_directory(knowledge_dir)
    return ApiResponse.ok(data=results, message="Knowledge seed documents successfully indexed.")
