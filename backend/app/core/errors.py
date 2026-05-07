"""作用：注册 FastAPI 全局异常处理器，统一输出 ErrorResponse 结构。"""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import get_trace_id
from app.schemas import ErrorCode, ErrorResponse

logger = logging.getLogger(__name__)


def _build(code: ErrorCode, message: str, trace_id: str, details: dict | None = None) -> dict:
    """构造 ErrorResponse 的 JSON body。"""
    return ErrorResponse(
        code=code,
        message=message,
        trace_id=trace_id,
        details=details,
    ).model_dump()


def register_exception_handlers(app: FastAPI) -> None:
    """把所有异常收敛到 ErrorResponse 上。"""

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        trace_id = get_trace_id()
        logger.warning(
            "validation_error",
            extra={"errors": exc.errors(), "path": request.url.path},
        )
        return JSONResponse(
            status_code=422,
            content=_build(
                ErrorCode.validation_error,
                "请求参数不合法，请检查后重试。",
                trace_id,
                {"errors": exc.errors()},
            ),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        trace_id = get_trace_id()
        code = ErrorCode.not_found if exc.status_code == 404 else ErrorCode.internal_error
        message = str(exc.detail) if exc.detail else "请求处理失败。"
        return JSONResponse(
            status_code=exc.status_code,
            content=_build(code, message, trace_id),
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        trace_id = get_trace_id()
        logger.exception("unhandled_error", extra={"path": request.url.path})
        return JSONResponse(
            status_code=500,
            content=_build(
                ErrorCode.internal_error,
                "服务内部错误，请稍后重试。",
                trace_id,
            ),
        )
