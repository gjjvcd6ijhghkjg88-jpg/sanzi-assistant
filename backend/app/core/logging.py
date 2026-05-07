"""作用：结构化 JSON 日志 + 请求级 trace_id 注入。

- JSON formatter 保证日志可被 ELK/Loki 等采集。
- ContextVar 保存当前请求的 trace_id，日志和异常处理器共享同一个值。
- TraceIdMiddleware 在每个请求进入时生成或读取 X-Trace-Id，并回写响应头。
"""

from __future__ import annotations

import json
import logging
import sys
import time
from contextvars import ContextVar
from typing import Any
from uuid import uuid4

from starlette.types import ASGIApp, Message, Receive, Scope, Send

_trace_id_var: ContextVar[str] = ContextVar("trace_id", default="-")

TRACE_HEADER = "x-trace-id"


def get_trace_id() -> str:
    """读取当前请求的 trace_id；非请求上下文返回占位符 '-'。"""
    return _trace_id_var.get()


def set_trace_id(trace_id: str) -> None:
    """显式设置当前 ContextVar 的 trace_id（仅测试或脚本使用）。"""
    _trace_id_var.set(trace_id)


class _TraceIdFilter(logging.Filter):
    """把当前 ContextVar 的 trace_id 注入到每条 LogRecord。"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = _trace_id_var.get()
        return True


class JsonFormatter(logging.Formatter):
    """把日志记录序列化成单行 JSON，便于日志采集。"""

    _RESERVED = {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "message",
        "module",
        "msecs",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
        "taskName",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", "-"),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)

        for key, value in record.__dict__.items():
            if key in self._RESERVED or key in payload or key.startswith("_"):
                continue
            try:
                json.dumps(value)
                payload[key] = value
            except TypeError:
                payload[key] = repr(value)

        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO") -> None:
    """为 root logger 装上 JSON handler 和 trace_id filter；多次调用幂等。"""
    root = logging.getLogger()
    root.setLevel(level)

    for handler in list(root.handlers):
        root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(_TraceIdFilter())
    root.addHandler(handler)

    # uvicorn 的默认 access/ error logger 单独配置了 handler，这里统一交给 root。
    for noisy in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(noisy)
        lg.handlers.clear()
        lg.propagate = True


class TraceIdMiddleware:
    """ASGI 中间件：生成/读取 trace_id，写入 ContextVar，并记录访问日志。"""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.logger = logging.getLogger("app.access")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope["headers"]}
        trace_id = headers.get(TRACE_HEADER) or uuid4().hex
        token = _trace_id_var.set(trace_id)
        start = time.perf_counter()
        status_code = 500

        async def send_with_trace(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers_list = list(message.get("headers", []))
                headers_list.append((TRACE_HEADER.encode("latin-1"), trace_id.encode("latin-1")))
                message = {**message, "headers": headers_list}
            await send(message)

        try:
            await self.app(scope, receive, send_with_trace)
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            self.logger.info(
                "request",
                extra={
                    "method": scope.get("method"),
                    "path": scope.get("path"),
                    "status": status_code,
                    "duration_ms": duration_ms,
                },
            )
            _trace_id_var.reset(token)
