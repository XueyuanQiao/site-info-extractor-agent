"""
配置模块
使用 Pydantic 管理应用配置
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用设置类"""

    # API Keys
    google_api_key: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    # 模型配置
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.0
    max_tokens: int = 2000

    # 浏览器配置
    browser_headless: bool = True

    class Config:
        """配置类"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 创建全局设置实例
settings = Settings()
