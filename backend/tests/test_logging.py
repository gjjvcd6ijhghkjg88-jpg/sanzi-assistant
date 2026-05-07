"""作用：验证 JSON 日志格式、trace_id 注入和响应头回写。"""

from __future__ import annotations

import json
import logging

from fastapi.testclient import TestClient

from app.core.logging import TRACE_HEADER, JsonFormatter, configure_logging, get_trace_id
from app.main import app


def test_json_formatter_outputs_trace_id() -> None:
    """JsonFormatter 应输出单行 JSON 且包含 trace_id 字段。"""
    configure_logging()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )
    record.trace_id = "abc123"
    line = JsonFormatter().format(record)
    payload = json.loads(line)
    assert payload["message"] == "hello world"
    assert payload["trace_id"] == "abc123"
    assert payload["level"] == "INFO"


def test_trace_id_middleware_echoes_header() -> None:
    """请求带 X-Trace-Id 时，响应头与业务 body 的 trace_id 一致。"""
    client = TestClient(app)
    sent = "trace-fixed-001"
    response = client.post(
        "/chat",
        json={"question": "村集体资金支出怎么审批？", "platform": "pc"},
        headers={TRACE_HEADER: sent},
    )
    assert response.status_code == 200
    assert response.headers.get(TRACE_HEADER) == sent
    assert response.json()["trace_id"] == sent


def test_get_trace_id_default_outside_request() -> None:
    """非请求上下文读取 trace_id 返回占位符。"""
    assert get_trace_id() == "-"
