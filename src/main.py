"""
Site Info Extractor Agent 主入口
提供命令行交互功能
"""

import json
import sys
import os
import signal
import traceback

# 将项目根目录添加到模块搜索路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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
from src.agents.extractor_agent import SiteExtractorAgent

console = Console()


def print_banner():
    """打印欢迎横幅"""
    banner = Panel.fit(
        "[bold blue]Site Info Extractor Agent[/bold blue]\n[dim]基于 LangChain 和 LangGraph 的网站信息提取系统[/dim]",
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

    console.print(table)


async def interactive_mode():
    """交互式模式"""
    console.print("\n[bold]交互式模式[/bold]")
    console.print("输入 URL 进行提取，输入 'quit' 或 'exit' 退出\n")

    # 构建配置字典
    config = {
        "model_name": settings.model_name,
        "temperature": settings.temperature,
        "max_tokens": settings.max_tokens,
    }

    # 添加可用的 API Key
    if settings.google_api_key:
        config["google_api_key"] = settings.google_api_key
    elif settings.openai_api_key:
        config["openai_api_key"] = settings.openai_api_key
    elif settings.anthropic_api_key:
        config["anthropic_api_key"] = settings.anthropic_api_key
    else:
        console.print("[red]未找到可用的 API Key，无法启动交互模式[/red]")
        return

    agent = SiteExtractorAgent(config)

    # 设置退出标志（使用可变对象）
    exit_flag = {'value': False}

    def signal_handler(_sig: int, _frame: object) -> None:
        exit_flag['value'] = True
        console.print("\n[yellow]正在退出...[/yellow]")

    # 注册信号处理器
    _ = signal.signal(signal.SIGINT, signal_handler)

    while not exit_flag['value']:
        try:
            url = console.input("[cyan]请输入 URL > [/cyan]").strip()

            if url.lower() in ['quit', 'exit', 'q']:
                console.print("[yellow]再见！[/yellow]")
                break

            if not url:
                continue

            console.print(f"[yellow]正在提取: {url}[/yellow]")
            result = await agent.extract(url)
            console.print("[green]✓ 提取完成[/green]")
            console.print_json(json.dumps(result, ensure_ascii=False, indent=2))

        except KeyboardInterrupt:
            console.print("\n[yellow]再见！[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]错误: {e}[/red]")
            console.print(f"[red]{traceback.format_exc()}[/red]")


async def main():
    """主函数"""
    try:
        print_banner()
        print_settings()

        # 检查 API Key
        if not settings.google_api_key and not settings.openai_api_key and not settings.anthropic_api_key:
            console.print("[red]警告: 未检测到 API Key，请在 .env 文件中配置[/red]")
            console.print("[dim]可以使用 GOOGLE_API_KEY、OPENAI_API_KEY 或 ANTHROPIC_API_KEY[/dim]\n")

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

