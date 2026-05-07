"""作用：创建 FastAPI 应用实例，配置跨域，并挂载健康检查和问答路由。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, health, qa
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import TraceIdMiddleware, configure_logging


def create_app() -> FastAPI:
    """创建应用工厂，测试和生产启动都复用同一份配置。"""
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="三资管理智能问答助手后端 API",
    )

    app.add_middleware(TraceIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(health.router, prefix="/api")
    app.include_router(qa.router, prefix="/api")
    app.include_router(chat.router)
    return app


app = create_app()
