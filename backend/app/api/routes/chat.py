"""作用：提供前端直接调用的 /chat 和 /chat/stream 接口。

SSE 事件协议（/chat/stream）：
  event: meta        data: {"trace_id": "..."}
  event: sources     data: [{id,title,category,excerpt}, ...]
  event: delta       data: {"text": "..."}         # 可多次
  event: suggestions data: ["...", "..."]
  event: done        data: {"mode": "llm|local_fallback"}
  event: error       data: {"code": "...", "message": "...", "trace_id": "..."}

所有 data 字段均为 JSON 字符串；前端按行解析 `event:` 和 `data:`。
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.routes.qa import create_ask_response
from app.core.logging import get_trace_id
from app.schemas import AskRequest, AskResponse, ErrorCode, ErrorResponse
from app.services.knowledge_base import knowledge_base
from app.services.llm_service import stream_answer

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

_ERROR_RESPONSES: dict[int | str, dict] = {
    422: {"model": ErrorResponse, "description": "参数校验失败"},
    500: {"model": ErrorResponse, "description": "服务内部错误"},
}


def _sse(event: str, data: object) -> bytes:
    """把事件名 + JSON 数据编码成 SSE 行。"""
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n".encode()


@router.post("/chat", response_model=AskResponse, responses=_ERROR_RESPONSES)
async def chat(payload: AskRequest) -> AskResponse:
    """接收 React 聊天问题，并返回回答、来源和推荐追问。"""
    return await create_ask_response(payload)


@router.post(
    "/chat/stream",
    responses={
        200: {
            "content": {"text/event-stream": {}},
            "description": "SSE 事件流：meta/sources/delta/suggestions/done/error",
        },
        **_ERROR_RESPONSES,
    },
)
async def chat_stream(payload: AskRequest) -> StreamingResponse:
    """以 SSE 方式流式返回回答，配合前端打字机效果。"""
    trace_id = get_trace_id()

    async def event_source() -> AsyncIterator[bytes]:
        try:
            yield _sse("meta", {"trace_id": trace_id})

            matched_sources = knowledge_base.search(payload.question, limit=3)
            yield _sse("sources", [s.model_dump() for s in matched_sources])

            mode = "local_fallback"
            suggestions: list[str] = []
            async for event_name, value in stream_answer(payload, matched_sources):
                if event_name == "delta":
                    yield _sse("delta", {"text": value})
                elif event_name == "suggestions":
                    suggestions = list(value)  # type: ignore[arg-type]
                elif event_name == "mode":
                    mode = str(value)

            if suggestions:
                yield _sse("suggestions", suggestions)
            yield _sse("done", {"mode": mode})
        except Exception as exc:
            logger.exception("chat_stream_error trace_id=%s", trace_id)
            yield _sse(
                "error",
                ErrorResponse(
                    code=ErrorCode.upstream_error,
                    message=f"流式回答失败：{exc}",
                    trace_id=trace_id,
                ).model_dump(),
            )

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
