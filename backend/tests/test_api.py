"""作用：验证后端基础接口可用，保证项目初始化后具备最小回归测试。"""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check() -> None:
    """健康检查应返回 ok。"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ask_question_local_fallback() -> None:
    """无 API Key 时问答接口应使用本地兜底回答并返回资料来源。"""
    response = client.post(
        "/api/qa/ask",
        json={"question": "村集体资金支出怎么审批？", "platform": "pc"},
    )
    payload = response.json()
    assert response.status_code == 200
    assert payload["answer"]
    assert payload["sources"]
    assert payload["mode"] in {"llm", "local_fallback"}

