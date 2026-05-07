"""作用：统一读取环境变量，避免业务代码散落读取配置。"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """后端运行配置，默认值保证本地不配置 .env 也能启动。"""

    app_name: str = "Sanzi Assistant API"
    app_env: str = "local"
    allowed_origins_raw: str = Field(
        default="http://127.0.0.1:5173,http://localhost:5173",
        alias="ALLOWED_ORIGINS",
    )
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )

    @property
    def allowed_origins(self) -> list[str]:
        """把逗号分隔的跨域配置转换成 FastAPI 需要的列表。"""
        return [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """缓存配置对象，避免每次请求都重复解析环境变量。"""
    return Settings()


settings = get_settings()
