"""作用：加载示例三资管理知识库，并提供轻量关键词检索能力。"""

from __future__ import annotations

import json
from pathlib import Path

from app.schemas import Source


class KnowledgeBase:
    """简单文件型知识库，后续可替换为向量数据库或知识图谱。"""

    def __init__(self, data_path: Path) -> None:
        self.data_path = data_path
        self._items = self._load_items()

    def _load_items(self) -> list[dict[str, str]]:
        """从 JSON 文件加载知识条目。"""
        if not self.data_path.exists():
            return []
        with self.data_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        return payload.get("items", [])

    def search(self, question: str, limit: int = 3) -> list[Source]:
        """按关键词命中数排序，返回最相关的资料片段。"""
        normalized_question = question.lower()
        scored: list[tuple[int, dict[str, str]]] = []

        for item in self._items:
            keywords = item.get("keywords", [])
            text = f"{item.get('title', '')} {item.get('content', '')}".lower()
            keyword_score = sum(1 for word in keywords if word.lower() in normalized_question)
            text_score = sum(1 for token in normalized_question.split() if token and token in text)
            score = keyword_score * 3 + text_score
            if score > 0:
                scored.append((score, item))

        if not scored:
            scored = [(1, item) for item in self._items[:limit]]

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            Source(
                id=item["id"],
                title=item["title"],
                category=item["category"],
                excerpt=item["content"][:180],
            )
            for _, item in scored[:limit]
        ]


knowledge_base = KnowledgeBase(Path(__file__).resolve().parents[2] / "data" / "knowledge_base.json")
