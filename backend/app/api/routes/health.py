"""作用：提供服务健康检查接口，便于前端联调和部署检查。"""

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """返回后端基础运行状态。"""
    return {
        "status": "ok",
        "service": settings.app_name,
        "env": settings.app_env,
    }

