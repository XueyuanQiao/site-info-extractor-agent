"""
配置模块
使用 Pydantic 管理应用配置
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用设置类"""
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    
    # LangChain 配置
    langchain_tracing_v2: bool = False
    langchain_api_key: Optional[str] = None
    langchain_project: str = "site-info-extractor"
    
    # 模型配置
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_tokens: int = 2000
    
    # 浏览器配置
    browser_headless: bool = True
    browser_timeout: int = 30000
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    
    # 提取配置
    extract_links: bool = True
    extract_images: bool = True
    extract_metadata: bool = True
    extract_contact: bool = True
    
    # 日志配置
    log_level: str = "INFO"
    
    class Config:
        """配置类"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_llm_config(self) -> dict:
        """获取 LLM 配置
        
        Returns:
            LLM 配置字典
        """
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
    
    def get_browser_config(self) -> dict:
        """获取浏览器配置
        
        Returns:
            浏览器配置字典
        """
        return {
            "headless": self.browser_headless,
            "timeout": self.browser_timeout,
            "user_agent": self.user_agent
        }


# 创建全局设置实例
settings = Settings()
