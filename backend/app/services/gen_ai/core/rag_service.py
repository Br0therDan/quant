"""ChromaDB-backed Retrieval-Augmented Generation helper service.

Retrieval-Augmented Generation helper utilities.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import chromadb

from app.core.config import settings
from app.models.trading.backtest import Backtest, BacktestResult
from app.schemas.gen_ai.rag import RAGAugmentedPrompt, RAGContext
from app.services.gen_ai.core.openai_client_manager import OpenAIClientManager

logger = logging.getLogger(__name__)


class RAGService:
    """Service that manages vector indexing and retrieval for GenAI workflows."""

    _instance: Optional["RAGService"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "RAGService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, openai_manager: Optional[OpenAIClientManager] = None) -> None:
        if getattr(self, "_initialised", False):
            return

        self.service_name = "rag_service"
        self.openai_manager = openai_manager or OpenAIClientManager()
        self._openai_client: Any | None = None
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL

        persist_dir = Path(settings.CHROMADB_PATH)
        persist_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Try new ChromaDB API first (recommended)
            self._client = chromadb.PersistentClient(path=str(persist_dir))
        except Exception as e:
            logger.warning(
                f"Failed to initialize ChromaDB with new API: {e}. "
                "RAGService will be disabled."
            )
            self._client = None
            self._backtests_collection = None
            self._strategies_collection = None
            self._embedding_cache: Dict[str, List[float]] = {}
            self._lock = asyncio.Lock()
            self._initialised = True
            return

        self._backtests_collection = self._client.get_or_create_collection(
            name="user_backtests",
            metadata={"description": "User backtest summaries for GenAI RAG"},
        )
        self._strategies_collection = self._client.get_or_create_collection(
            name="user_strategies",
            metadata={"description": "User generated strategies and insights"},
        )

        self._embedding_cache: Dict[str, List[float]] = {}
        self._lock = asyncio.Lock()
        self._initialised = True

        logger.info(
            "RAGService initialised",
            extra={
                "persist_directory": str(persist_dir),
                "embedding_model": self.embedding_model,
            },
        )

    async def index_backtest_result(
        self,
        backtest: Backtest,
        result: BacktestResult,
    ) -> None:
        """Index a freshly completed backtest into the vector store."""

        # Skip if ChromaDB is not available
        if self._client is None or self._backtests_collection is None:
            logger.debug(
                "Skipping RAG indexing because ChromaDB is not available",
                extra={"backtest_id": str(backtest.id)},
            )
            return

        user_id = backtest.user_id or backtest.created_by
        if not user_id:
            logger.debug(
                "Skipping RAG indexing because user_id is missing",
                extra={"backtest_id": str(backtest.id)},
            )
            return

        content = self._format_backtest_as_text(backtest, result)
        if not content.strip():
            logger.debug(
                "Skipping RAG indexing because formatted content is empty",
                extra={"backtest_id": str(backtest.id)},
            )
            return

        embedding = await self._generate_embedding(content)
        if embedding is None:
            logger.warning(
                "Embedding generation failed, skipping RAG indexing",
                extra={"backtest_id": str(backtest.id)},
            )
            return

        metadata = {
            "user_id": user_id,
            "backtest_id": result.backtest_id,
            "backtest_result_id": str(result.id),
            "strategy_id": backtest.strategy_id,
            "strategy_name": backtest.name,
            "symbols": backtest.config.symbols,
            "start_date": backtest.config.start_date.isoformat(),
            "end_date": backtest.config.end_date.isoformat(),
            "total_return": result.performance.total_return,
            "sharpe_ratio": result.performance.sharpe_ratio,
            "max_drawdown": result.performance.max_drawdown,
            "win_rate": result.performance.win_rate,
            "total_trades": result.performance.total_trades,
            "indexed_at": datetime.utcnow().isoformat(),
            "content_hash": self._hash_text(content),
        }

        await self._upsert(
            self._backtests_collection,
            document_id=str(result.id),
            document=content,
            embedding=embedding,
            metadata=metadata,
        )

    async def search_similar_backtests(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
    ) -> List[RAGContext]:
        """Retrieve similar backtests for the user based on the query."""

        # Skip if ChromaDB is not available
        if self._client is None or self._backtests_collection is None:
            logger.debug("Skipping RAG search because ChromaDB is not available")
            return []

        if not query.strip():
            return []

        embedding = await self._generate_embedding(query)
        if embedding is None:
            logger.warning(
                "Embedding generation failed for query; returning empty results"
            )
            return []

        try:
            results = await asyncio.to_thread(
                self._backtests_collection.query,
                query_embeddings=[embedding],
                n_results=top_k,
                where={"user_id": user_id},
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error(
                "ChromaDB query failed",
                exc_info=True,
                extra={"error": str(exc)},
            )
            return []

        ids = results.get("ids", [[]])
        documents = results.get("documents", [[]])
        metadatas = results.get("metadatas", [[]])
        distances = results.get("distances", [[]])

        if not ids or not ids[0]:
            return []

        contexts: List[RAGContext] = []
        for idx, document_id in enumerate(ids[0]):
            content = documents[0][idx] if documents and documents[0] else ""
            raw_metadata = metadatas[0][idx] if metadatas and metadatas[0] else {}
            # Ensure metadata is a plain Dict[str, Any] for pydantic/typing compatibility
            try:
                if isinstance(raw_metadata, dict):
                    metadata: Dict[str, Any] = raw_metadata
                else:
                    metadata = dict(raw_metadata)
            except Exception:
                # Fallback to empty dict if conversion fails
                metadata = {}

            distance = distances[0][idx] if distances and distances[0] else 0.0
            indexed_at = metadata.get("indexed_at")
            parsed_indexed_at: Optional[datetime] = None
            if indexed_at:
                try:
                    if isinstance(indexed_at, datetime):
                        parsed_indexed_at = indexed_at
                    elif isinstance(indexed_at, str):
                        parsed_indexed_at = datetime.fromisoformat(indexed_at)
                    else:
                        # Unsupported type for parsing; skip
                        parsed_indexed_at = None
                except ValueError:
                    parsed_indexed_at = None

            contexts.append(
                RAGContext(
                    document_id=document_id,
                    content=content,
                    similarity_score=float(distance),
                    metadata=metadata,
                    indexed_at=parsed_indexed_at,
                )
            )

        return contexts

    def build_augmented_prompt(
        self, user_query: str, contexts: Sequence[RAGContext]
    ) -> RAGAugmentedPrompt:
        """Create a consolidated prompt that includes retrieved contexts."""

        if not contexts:
            return RAGAugmentedPrompt(prompt=user_query, contexts=[])

        lines: List[str] = []
        for idx, context in enumerate(contexts, start=1):
            metadata = context.metadata or {}
            strategy_name = metadata.get("strategy_name", "전략")
            total_return = metadata.get("total_return")
            sharpe_ratio = metadata.get("sharpe_ratio")
            max_drawdown = metadata.get("max_drawdown")
            win_rate = metadata.get("win_rate")
            period = (
                f"{metadata.get('start_date', '?')} ~ {metadata.get('end_date', '?')}"
            )

            metrics: List[str] = []
            if isinstance(total_return, (int, float)):
                metrics.append(f"총 수익률 {total_return:.2%}")
            if isinstance(sharpe_ratio, (int, float)):
                metrics.append(f"샤프 {sharpe_ratio:.2f}")
            if isinstance(max_drawdown, (int, float)):
                metrics.append(f"최대 낙폭 {max_drawdown:.2%}")
            if isinstance(win_rate, (int, float)):
                metrics.append(f"승률 {win_rate:.2%}")

            metrics_text = ", ".join(metrics)
            snippet = context.content.strip().splitlines()
            snippet_text = snippet[0] if snippet else context.content
            lines.append(
                f"[참고 {idx}] {strategy_name} ({period}) — {metrics_text}\n{snippet_text}"
            )

        prompt = (
            "다음은 사용자의 이전 백테스트 요약입니다:\n"
            + "\n\n".join(lines)
            + "\n\n사용자 요청: "
            + user_query
            + "\n과거 데이터를 참고하여 보다 개인화된 답변을 제공하세요."
        )

        return RAGAugmentedPrompt(prompt=prompt, contexts=list(contexts))

    @staticmethod
    def serialise_contexts(contexts: Sequence[RAGContext]) -> List[Dict[str, Any]]:
        """Convert RAG contexts into plain dictionaries for downstream use."""

        serialised: List[Dict[str, Any]] = []
        for context in contexts:
            serialised.append(
                {
                    "document_id": context.document_id,
                    "content": context.content,
                    "similarity_score": context.similarity_score,
                    "metadata": context.metadata,
                    "indexed_at": (
                        context.indexed_at.isoformat() if context.indexed_at else None
                    ),
                }
            )
        return serialised

    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        if not text.strip():
            return None

        text_hash = self._hash_text(text)
        cached = self._embedding_cache.get(text_hash)
        if cached is not None:
            return cached

        try:
            client = self._get_openai_client()
            response = await client.embeddings.create(
                model=self.embedding_model,
                input=[text],
            )
        except Exception as exc:  # pragma: no cover - network interaction
            logger.error(
                "OpenAI embedding request failed",
                exc_info=True,
                extra={"error": str(exc)},
            )
            return None

        embedding = response.data[0].embedding
        self._embedding_cache[text_hash] = embedding
        self.openai_manager.track_usage(
            service_name=self.service_name,
            model_id=self.embedding_model,
            usage=getattr(response, "usage", None),
        )
        return embedding

    async def _upsert(
        self,
        collection: Any,
        document_id: str,
        document: str,
        embedding: Sequence[float],
        metadata: Dict[str, Any],
    ) -> None:
        async with self._lock:
            await asyncio.to_thread(
                self._upsert_sync,
                collection,
                document_id,
                document,
                embedding,
                metadata,
            )

    @staticmethod
    def _upsert_sync(
        collection: Any,
        document_id: str,
        document: str,
        embedding: Sequence[float],
        metadata: Dict[str, Any],
    ) -> None:
        try:
            collection.delete(ids=[document_id])
        except Exception:  # pragma: no cover - best effort cleanup
            pass

        collection.add(
            ids=[document_id],
            documents=[document],
            embeddings=[list(embedding)],
            metadatas=[metadata],
        )

    def _get_openai_client(self) -> Any:
        if self._openai_client is None:
            self._openai_client = self.openai_manager.get_client()
        return self._openai_client

    @staticmethod
    def _format_backtest_as_text(backtest: Backtest, result: BacktestResult) -> str:
        performance = result.performance
        lines = [
            f"전략명: {backtest.name}",
            f"기간: {backtest.config.start_date.date()} ~ {backtest.config.end_date.date()}",
            f"대상 심볼: {', '.join(backtest.config.symbols)}",
            f"총 수익률: {performance.total_return:.2%}",
            f"연환산 수익률: {performance.annualized_return:.2%}",
            f"샤프 비율: {performance.sharpe_ratio:.2f}",
            f"최대 낙폭: {performance.max_drawdown:.2%}",
            f"승률: {performance.win_rate:.2%} (총 {performance.total_trades}회)",
        ]
        if backtest.config.tags:
            lines.append(f"태그: {', '.join(backtest.config.tags)}")
        return "\n".join(lines)

    @staticmethod
    def _hash_text(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


__all__ = ["RAGService"]
