"""Schemas for Retrieval-Augmented Generation (RAG) workflows."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RAGContext(BaseModel):
    """Context snippet retrieved from the vector store."""

    document_id: str = Field(..., description="Vector store document identifier")
    content: str = Field(..., min_length=1, description="Stored human readable summary text")
    similarity_score: float = Field(
        ..., ge=0.0, description="Distance or similarity metric returned by the retriever"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata captured during indexing",
    )
    indexed_at: Optional[datetime] = Field(
        None, description="Timestamp when the document was indexed"
    )


class RAGAugmentedPrompt(BaseModel):
    """Prompt generated after augmenting with retrieved contexts."""

    prompt: str = Field(..., description="Fully rendered prompt delivered to the LLM")
    contexts: List[RAGContext] = Field(
        default_factory=list, description="Contexts that were embedded into the prompt"
    )


__all__ = ["RAGContext", "RAGAugmentedPrompt"]
