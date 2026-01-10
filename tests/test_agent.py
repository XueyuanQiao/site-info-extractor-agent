"""
测试文件
包含 Agent 功能的单元测试
"""

import warnings
import pytest
import asyncio
from unittest.mock import Mock, patch

from src.agents.extractor_agent import SiteExtractorAgent
from src.tools.browser_tool import BrowserTool
from src.tools.extractors import ContentExtractor

# 抑制 Python 3.14 与 Pydantic V1 的兼容性警告
warnings.filterwarnings(
    "ignore",
    message=".*Core Pydantic V1 functionality.*",
    category=UserWarning
)


class TestContentExtractor:
    """内容提取器测试"""
    
    def test_extract_links(self):
        """测试链接提取"""
        html = '<a href="https://example.com">Example</a>'
        links = ContentExtractor.extract_links(html)
        assert len(links) == 1
        assert links[0]['text'] == 'Example'
        assert links[0]['href'] == 'https://example.com'
    
    def test_extract_emails(self):
        """测试邮箱提取"""
        text = "联系我们: support@example.com 或 sales@test.com"
        emails = ContentExtractor.extract_emails(text)
        assert len(emails) == 2
        assert 'support@example.com' in emails
    
    def test_clean_text(self):
        """测试文本清理"""
        text = "  Hello   World  "
        cleaned = ContentExtractor.clean_text(text)
        assert cleaned == "Hello World"


class TestBrowserTool:
    """浏览器工具测试"""
    
    @pytest.mark.asyncio
    async def test_browser_initialization(self):
        """测试浏览器初始化"""
        async with BrowserTool(headless=True) as browser:
            assert browser.browser is not None
            assert browser.playwright is not None


class TestSiteExtractorAgent:
    """SiteExtractorAgent 测试"""
    
    @pytest.fixture
    def agent(self):
        """创建 Agent 实例"""
        config = {
            "model": "gpt-4o-mini",
            "openai_api_key": "test-key"
        }
        return SiteExtractorAgent(config)
    
    def test_agent_initialization(self, agent):
        """测试 Agent 初始化"""
        assert agent is not None
        assert agent.config["model"] == "gpt-4o-mini"
    
    @pytest.mark.asyncio
    async def test_extract_todo(self, agent):
        """测试提取功能（TODO 阶段）"""
        result = await agent.extract("https://example.com")
        assert result["status"] == "todo"
        assert result["url"] == "https://example.com"


# TODO: 添加更多集成测试
# class TestIntegration:
#     """集成测试"""
#     
#     @pytest.mark.asyncio
#     async def test_full_extraction_flow(self):
#         """测试完整提取流程"""
#         pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
