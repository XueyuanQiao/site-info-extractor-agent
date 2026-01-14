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
    groq_api_key: str | None = None
    siliconflow_api_key: str | None = None
    xunfei_api_key: str | None = None
    cerebras_api_key: str | None = None

    # 模型配置
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.0
    max_tokens: int = 2000
    
    # 各提供商特定模型配置
    
    # 免费
    gemini_model_name: str = "gemini-2.5-flash"
    groq_model_name: str = "llama-3.3-70b-versatile"
    # siliconflow支持多种模型，可选（https://cloud.siliconflow.cn/me/models）
    #siliconflow_model_name: str = "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"
    siliconflow_model_name: str = "tencent/Hunyuan-MT-7B"
    # 讯飞模型可选（https://maas.xfyun.cn/account）
    xunfei_model_name: str = "Qwen3-1.7B"
    # cerebras模型可选（https://cloud.cerebras.ai/platform/org_xd58erkrmhtmnkwpdmrvyy8x/models）
    cerebras_model_name: str = "gpt-oss-120b"

    # 付费
    openai_model_name: str = "gpt-4o-mini"
    anthropic_model_name: str = "claude-3-5-sonnet-20241022"

    # 浏览器配置
    browser_headless: bool = True

    class Config:
        """配置类"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# 创建全局设置实例
settings = Settings()
