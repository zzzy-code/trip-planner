"""Application configuration."""

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

helloagents_env = Path(__file__).parent.parent.parent.parent / "HelloAgents" / ".env"
if helloagents_env.exists():
    load_dotenv(helloagents_env, override=False)


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "HelloAgents\u667a\u80fd\u65c5\u884c\u52a9\u624b"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8000

    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"

    database_url: str = "sqlite+aiosqlite:///./trip_planner.db"
    environment: str = "development"
    secret_key: str = "change-me-in-production"
    auto_create_tables: bool = True

    amap_api_key: str = ""

    unsplash_access_key: str = ""
    unsplash_secret_key: str = ""

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4"

    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    def get_cors_origins_list(self) -> List[str]:
        """Return normalized CORS origins."""
        origins = {origin.strip().rstrip("/") for origin in self.cors_origins.split(",") if origin.strip()}
        for origin in list(origins):
            if "localhost" in origin:
                origins.add(origin.replace("localhost", "127.0.0.1"))
            if "127.0.0.1" in origin:
                origins.add(origin.replace("127.0.0.1", "localhost"))
        origins.update(
            {
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            }
        )
        return sorted(origins)


settings = Settings()


def get_settings() -> Settings:
    """Return global settings."""
    return settings


def validate_config():
    """Validate required settings."""
    errors = []
    warnings = []

    if not settings.amap_api_key:
        errors.append("AMAP_API_KEY\u672a\u914d\u7f6e")

    llm_api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not llm_api_key:
        warnings.append("LLM_API_KEY\u6216OPENAI_API_KEY\u672a\u914d\u7f6e\uff0cLLM\u529f\u80fd\u53ef\u80fd\u65e0\u6cd5\u4f7f\u7528")

    if errors:
        error_msg = "\u914d\u7f6e\u9519\u8bef:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)

    if warnings:
        print("\n\u914d\u7f6e\u8b66\u544a:")
        for warning in warnings:
            print(f"  - {warning}")

    return True


def print_config():
    """Print current configuration with sensitive values hidden."""
    amap_status = "已配置" if settings.amap_api_key else "未配置"
    llm_api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    llm_status = "已配置" if llm_api_key else "未配置"
    llm_base_url = os.getenv("LLM_BASE_URL") or settings.openai_base_url
    llm_model = os.getenv("LLM_MODEL_ID") or settings.openai_model

    print(f"应用名称: {settings.app_name}")
    print(f"服务器: {settings.host}:{settings.port}")
    print(f"高德地图API Key: {amap_status}")
    print(f"LLM API Key: {llm_status}")
    print(f"LLM Base URL: {llm_base_url}")
    print(f"LLM Model: {llm_model}")
    print(f"日志级别: {settings.log_level}")
