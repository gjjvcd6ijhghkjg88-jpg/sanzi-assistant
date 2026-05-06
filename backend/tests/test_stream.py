"""作用：冒烟测试 /chat/stream SSE 事件协议，验证顺序与格式。"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _parse_sse(raw: str) -> list[tuple[str, str]]:
    events: list[tuple[str, str]] = []
    event_name = ""
    for line in raw.splitlines():
        if line.startswith("event: "):
            event_name = line[len("event: "):].strip()
        elif line.startswith("data: "):
            events.append((event_name, line[len("data: "):]))
    return events


def test_chat_stream_event_order() -> None:
    """SSE 必须先 meta → sources → delta+ → suggestions → done。"""
    with client.stream(
        "POST",
        "/chat/stream",
        json={"question": "村集体资金支出怎么审批？", "platform": "pc"},
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        body = response.read().decode("utf-8")

    events = _parse_sse(body)
    names = [name for name, _ in events]
    assert names[0] == "meta"
    assert names[1] == "sources"
    assert "delta" in names
    assert names[-1] == "done"


def test_chat_stream_validation_error() -> None:
    """空 question 应返回统一的 ErrorResponse（code/message/trace_id）。"""
    response = client.post("/chat/stream", json={"question": "", "platform": "pc"})
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "validation_error"
    assert body["trace_id"]
    assert body["message"]
