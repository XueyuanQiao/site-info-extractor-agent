"""
浏览器工具
封装 Playwright 进行网页访问和内容获取
"""

from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page
import asyncio


class BrowserTool:
    """浏览器工具类"""
    
    def __init__(self, headless: bool = True):
        """初始化浏览器工具
        
        Args:
            headless: 是否使用无头模式
        """
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def start(self):
        """启动浏览器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def fetch_page(self, url: str, wait_for: Optional[str] = None) -> Dict[str, Any]:
        """获取页面内容
        
        Args:
            url: 目标 URL
            wait_for: 等待的元素选择器（可选）
            
        Returns:
            包含页面信息的字典
        """
        if not self.browser:
            raise RuntimeError("Browser not started. Call start() or use async context manager.")
        
        page = await self.browser.new_page()
        try:
            await page.goto(url, wait_until="networkidle")
            
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=10000)
            
            # 获取页面基本信息
            title = await page.title()
            content = await page.content()
            text = await page.inner_text("body")
            
            # 获取元数据
            metadata = await self._get_metadata(page)
            
            return {
                "url": url,
                "title": title,
                "content": content,
                "text": text,
                "metadata": metadata
            }
        finally:
            await page.close()
    
    async def _get_metadata(self, page: Page) -> Dict[str, str]:
        """获取页面元数据
        
        Args:
            page: Playwright Page 对象
            
        Returns:
            元数据字典
        """
        metadata = {}
        
        # 获取各种 meta 标签
        selectors = {
            "description": 'meta[name="description"]',
            "keywords": 'meta[name="keywords"]',
            "og:title": 'meta[property="og:title"]',
            "og:description": 'meta[property="og:description"]',
            "og:image": 'meta[property="og:image"]'
        }
        
        for key, selector in selectors.items():
            element = await page.query_selector(selector)
            if element:
                metadata[key] = await element.get_attribute("content") or ""
        
        return metadata
    
    async def screenshot(self, url: str, output_path: str):
        """对页面进行截图
        
        Args:
            url: 目标 URL
            output_path: 截图保存路径
        """
        if not self.browser:
            raise RuntimeError("Browser not started. Call start() or use async context manager.")
        
        page = await self.browser.new_page()
        try:
            await page.goto(url, wait_until="networkidle")
            await page.screenshot(path=output_path, full_page=True)
        finally:
            await page.close()
