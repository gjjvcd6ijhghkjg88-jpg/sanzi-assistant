"""作用：提供智能问答接口，串联知识库检索和 LLM/本地兜底回答生成。"""

from uuid import uuid4

from fastapi import APIRouter

from app.schemas import AskRequest, AskResponse
from app.services.knowledge_base import knowledge_base
from app.services.llm_service import answer_question

router = APIRouter(prefix="/qa", tags=["qa"])


@router.post("/ask", response_model=AskResponse)
async def ask_question(payload: AskRequest) -> AskResponse:
    """根据用户问题返回简明、带来源和追问建议的业务回答。"""
    trace_id = uuid4().hex
    matched_sources = knowledge_base.search(payload.question, limit=3)
    answer, suggestions, mode = await answer_question(payload, matched_sources)

    return AskResponse(
        answer=answer,
        sources=matched_sources,
        suggestions=suggestions,
        trace_id=trace_id,
        mode=mode,
    )

