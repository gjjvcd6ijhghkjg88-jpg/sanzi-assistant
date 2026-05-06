"""作用：离线导出 FastAPI 的 OpenAPI 规范到 docs/openapi.json，供前端生成类型。

用法：
    python -m scripts.export_openapi        # 写到默认 docs/openapi.json
    python -m scripts.export_openapi path   # 自定义输出路径
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from app.main import app


def main(argv: list[str]) -> int:
    default_output = Path(__file__).resolve().parents[2] / "docs" / "openapi.json"
    output = Path(argv[1]) if len(argv) > 1 else default_output
    output.parent.mkdir(parents=True, exist_ok=True)

    spec = app.openapi()
    output.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OpenAPI 已写入 {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
