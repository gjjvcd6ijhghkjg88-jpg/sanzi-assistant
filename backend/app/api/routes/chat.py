"""作用：提供前端直接调用的 /chat 接口，保持聊天主链路简单可测。"""

from fastapi import APIRouter

from app.api.routes.qa import create_ask_response
from app.schemas import AskRequest, AskResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=AskResponse)
async def chat(payload: AskRequest) -> AskResponse:
    """接收 React 聊天问题，并返回回答、来源和推荐追问。"""
    return await create_ask_response(payload)
