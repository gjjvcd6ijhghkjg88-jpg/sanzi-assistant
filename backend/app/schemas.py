"""作用：定义前后端交互的数据结构，作为 API 契约的代码版本。"""

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Platform(StrEnum):
    """终端类型，用于后端根据 PC 或移动端调整回答长度。"""

    pc = "pc"
    mobile = "mobile"


class AskRequest(BaseModel):
    """问答接口请求体。"""

    question: str = Field(..., min_length=1, max_length=500, description="用户输入的问题")
    platform: Platform = Field(default=Platform.pc, description="用户所在终端")
    session_id: str | None = Field(default=None, max_length=80, description="可选会话 ID")


class Source(BaseModel):
    """回答引用的资料来源。"""

    id: str
    title: str
    category: str
    excerpt: str


class AskResponse(BaseModel):
    """问答接口响应体。"""

    answer: str
    sources: list[Source]
    suggestions: list[str]
    trace_id: str
    mode: Literal["llm", "local_fallback"]


class ErrorCode(StrEnum):
    """统一错误码，前端可基于 code 做差异化处理。"""

    validation_error = "validation_error"
    not_found = "not_found"
    upstream_error = "upstream_error"
    internal_error = "internal_error"


class ErrorResponse(BaseModel):
    """统一错误响应体；所有非 2xx 返回都遵循这个结构。"""

    code: ErrorCode = Field(..., description="机器可读错误码")
    message: str = Field(..., description="面向用户的中文提示")
    trace_id: str = Field(..., description="链路 ID，用于排障")
    details: dict[str, Any] | None = Field(default=None, description="可选的附加字段，如校验错误明细")

