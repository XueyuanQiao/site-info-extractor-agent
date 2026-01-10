"""
Site Info Extractor Agent 主入口
提供命令行交互和测试功能
"""

import asyncio
import warnings
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# 抑制 Python 3.14 与 Pydantic V1 的兼容性警告
warnings.filterwarnings(
    "ignore",
    message=".*Core Pydantic V1 functionality.*",
    category=UserWarning
)

from config.settings import settings
from agents.extractor_agent import SiteExtractorAgent

console = Console()


def print_banner():
    """打印欢迎横幅"""
    banner = Panel.fit(
        "[bold blue]Site Info Extractor Agent[/bold blue]\n"
        "[dim]基于 LangChain 和 LangGraph 的网站信息提取系统[/dim]",
        border_style="blue"
    )
    console.print(banner)


def print_settings():
    """打印当前配置"""
    table = Table(title="当前配置", show_header=True, header_style="bold magenta")
    table.add_column("配置项", style="cyan", width=30)
    table.add_column("值", style="green")
    
    table.add_row("模型", settings.model_name)
    table.add_row("温度", str(settings.temperature))
    table.add_row("最大令牌", str(settings.max_tokens))
    table.add_row("浏览器模式", "无头" if settings.browser_headless else "有头")
    table.add_row("提取链接", "是" if settings.extract_links else "否")
    table.add_row("提取图片", "是" if settings.extract_images else "否")
    table.add_row("提取元数据", "是" if settings.extract_metadata else "否")
    table.add_row("提取联系信息", "是" if settings.extract_contact else "否")
    
    console.print(table)


async def test_agent():
    """测试 Agent 基本功能"""
    try:
        console.print("[yellow]正在初始化 Agent...[/yellow]")
        
        agent = SiteExtractorAgent({
            "model": settings.model_name,
            "openai_api_key": settings.openai_api_key
        })
        
        console.print("[green]✓ Agent 初始化成功[/green]")
        
        # TODO: 添加更多测试逻辑
        # result = await agent.extract("https://example.com")
        # console.print(result)
        
    except Exception as e:
        console.print(f"[red]✗ Agent 初始化失败: {e}[/red]")
        raise


async def interactive_mode():
    """交互式模式"""
    console.print("\n[bold]交互式模式[/bold]")
    console.print("输入 URL 进行提取，输入 'quit' 或 'exit' 退出\n")
    
    agent = SiteExtractorAgent({
        "model": settings.model_name,
        "openai_api_key": settings.openai_api_key
    })
    
    while True:
        try:
            url = console.input("[cyan]请输入 URL > [/cyan]").strip()
            
            if url.lower() in ['quit', 'exit', 'q']:
                console.print("[yellow]再见！[/yellow]")
                break
            
            if not url:
                continue
            
            console.print(f"[yellow]正在提取: {url}[/yellow]")
            # result = await agent.extract(url)
            # console.print(result)
            console.print("[dim]TODO: 实现提取逻辑[/dim]")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]再见！[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]错误: {e}[/red]")


async def main():
    """主函数"""
    try:
        print_banner()
        print_settings()

        # 检查 API Key
        if not settings.openai_api_key and not settings.anthropic_api_key:
            console.print("[red]警告: 未检测到 API Key，请在 .env 文件中配置[/red]")
            console.print("[dim]可以使用 OPENAI_API_KEY 或 ANTHROPIC_API_KEY[/dim]\n")

        # 运行基本测试
        await test_agent()

        # 进入交互模式
        await interactive_mode()
    except (KeyboardInterrupt, asyncio.CancelledError):
        console.print("\n[yellow]再见！[/yellow]")
    except Exception as e:
        console.print(f"[red]发生错误: {e}[/red]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass

