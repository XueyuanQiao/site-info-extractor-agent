import json
import sys
import os
import signal
import traceback
import select

# 添加项目根目录到模块搜索路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
import warnings
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# 抑制 Pydantic 兼容性警告
warnings.filterwarnings("ignore", message=".*Core Pydantic V1 functionality.*", category=UserWarning)

from config.settings import settings
from src.agents.extractor_agent import SiteExtractorAgent

console = Console()


def print_banner():
    banner = Panel.fit(
        "[bold blue]Site Info Extractor Agent[/bold blue]\n[dim]基于 LangChain 和 LangGraph 的网站信息提取系统[/dim]",
        border_style="blue"
    )
    console.print(banner)


def print_settings():
    table = Table(title="当前配置", show_header=True, header_style="bold magenta")
    table.add_column("配置项", style="cyan", width=30)
    table.add_column("值", style="green")
    table.add_row("温度", str(settings.temperature))
    table.add_row("最大令牌", str(settings.max_tokens))
    table.add_row("浏览器模式", "无头" if settings.browser_headless else "有头")
    console.print(table)


async def interactive_mode():
    console.print("\n[bold]交互式模式[/bold]")
    console.print("输入 URL 进行提取，输入 'quit' 或 'exit' 退出\n")

    # 构建配置
    config = {
        "model_name": settings.model_name,
        "temperature": settings.temperature,
        "max_tokens": settings.max_tokens,
    }

    # 收集可用模型
    available_models = []
    if settings.google_api_key:
        available_models.append(("gemini", f"Google Gemini (默认: {settings.gemini_model_name})"))
    if settings.openai_api_key:
        available_models.append(("openai", f"OpenAI (默认: {settings.openai_model_name})"))
    if settings.anthropic_api_key:
        available_models.append(("anthropic", f"Anthropic (默认: {settings.anthropic_model_name})"))
    if settings.groq_api_key:
        available_models.append(("groq", f"Groq (默认: {settings.groq_model_name})"))
    if settings.siliconflow_api_key:
        available_models.append(("siliconflow", f"SiliconFlow (慢，默认: {settings.siliconflow_model_name})"))
    if settings.xunfei_api_key:
        available_models.append(("xunfei", f"讯飞 (不好用，默认: {settings.xunfei_model_name})"))

    if not available_models:
        console.print("[red]未找到可用的 API Key，无法启动交互模式[/red]")
        return

    # 退出标志和信号处理
    exit_flag = {'value': False}

    def signal_handler(_sig: int, _frame: object) -> None:
        exit_flag['value'] = True
        console.print("\n[yellow]正在退出...[/yellow]")
        # 立即退出程序，避免继续执行
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # 模型选择
    if len(available_models) > 1:
        console.print("[cyan]请选择要使用的模型:[/cyan]")
        for i, (_, model_name) in enumerate(available_models, 1):
            console.print(f"[cyan]{i}. {model_name}[/cyan]")

        console.print("[cyan]请输入选项编号: [/cyan]", end="")
        console.file.flush()

        while not exit_flag['value']:
            try:
                # 非阻塞输入
                try:
                    ready, _, _ = select.select([sys.stdin], [], [], 0.1)
                except ValueError:
                    break

                if ready:
                    try:
                        choice = sys.stdin.readline().strip()
                    except (OSError, IOError):
                        break

                    if choice.lower() in ['quit', 'exit', 'q']:
                        console.print("[yellow]再见！[/yellow]")
                        return

                    try:
                        choice_idx = int(choice) - 1
                        if 0 <= choice_idx < len(available_models):
                            selected_model = available_models[choice_idx][0]
                            console.print(f"[green]✓ 已选择: {available_models[choice_idx][1]}[/green]\n")

                            # 设置对应模型的配置
                            if selected_model == "gemini":
                                config["model_name"] = settings.gemini_model_name
                                config["google_api_key"] = settings.google_api_key
                            elif selected_model == "openai":
                                config["model_name"] = settings.openai_model_name
                                config["openai_api_key"] = settings.openai_api_key
                            elif selected_model == "anthropic":
                                config["model_name"] = settings.anthropic_model_name
                                config["anthropic_api_key"] = settings.anthropic_api_key
                            elif selected_model == "groq":
                                config["model_name"] = settings.groq_model_name
                                config["groq_api_key"] = settings.groq_api_key
                            elif selected_model == "siliconflow":
                                config["model_name"] = settings.siliconflow_model_name
                                config["siliconflow_api_key"] = settings.siliconflow_api_key
                            elif selected_model == "xunfei":
                                config["model_name"] = settings.xunfei_model_name
                                config["xunfei_api_key"] = settings.xunfei_api_key
                            break
                        else:
                            console.print("[red]无效的选项，请重新输入[/red]")
                    except ValueError:
                        console.print("[red]请输入有效的数字[/red]")
            except KeyboardInterrupt:
                console.print("\n[yellow]再见！[/yellow]")
                return
            except Exception as e:
                console.print(f"[red]错误: {e}[/red]")
                console.print(f"[red]{traceback.format_exc()}[/red]")
                return
    else:
        # 只有一个可用模型
        selected_model = available_models[0][0]
        console.print(f"[green]使用默认模型: {available_models[0][1]}[/green]\n")

        # 设置对应模型的配置
        if selected_model == "gemini":
            config["model_name"] = settings.gemini_model_name
            config["google_api_key"] = settings.google_api_key
        elif selected_model == "openai":
            config["model_name"] = settings.openai_model_name
            config["openai_api_key"] = settings.openai_api_key
        elif selected_model == "anthropic":
            config["model_name"] = settings.anthropic_model_name
            config["anthropic_api_key"] = settings.anthropic_api_key
        elif selected_model == "groq":
            config["model_name"] = settings.groq_model_name
            config["groq_api_key"] = settings.groq_api_key
        elif selected_model == "siliconflow":
            config["model_name"] = settings.siliconflow_model_name
            config["siliconflow_api_key"] = settings.siliconflow_api_key
        elif selected_model == "xunfei":
            config["model_name"] = settings.xunfei_model_name
            config["xunfei_api_key"] = settings.xunfei_api_key

    agent = SiteExtractorAgent(config)

    # URL 输入循环
    console.print("[cyan]请输入 URL > [/cyan]", end="")
    console.file.flush()

    while not exit_flag['value']:
        try:
            # 非阻塞输入
            try:
                ready, _, _ = select.select([sys.stdin], [], [], 0.1)
            except ValueError:
                break

            if ready:
                try:
                    url = sys.stdin.readline().strip()
                except (OSError, IOError):
                    break

                if url.lower() in ['quit', 'exit', 'q']:
                    console.print("[yellow]再见！[/yellow]")
                    break

                if not url:
                    continue

                console.print(f"[yellow]正在提取: {url}[/yellow]")
                result = await agent.extract(url)
                console.print("[green]✓ 提取完成[/green]")
                console.print_json(json.dumps(result, ensure_ascii=False, indent=2))

                # 重新提示输入
                console.print("[cyan]请输入 URL > [/cyan]", end="")
                console.file.flush()

            if exit_flag['value']:
                console.print("[yellow]再见！[/yellow]")
                break

        except KeyboardInterrupt:
            console.print("\n[yellow]再见！[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]错误: {e}[/red]")
            console.print(f"[red]{traceback.format_exc()}[/red]")


async def main():
    try:
        print_banner()
        print_settings()

        # 检查 API Key
        if not any([settings.google_api_key, settings.openai_api_key, settings.anthropic_api_key, 
                    settings.groq_api_key, settings.siliconflow_api_key, settings.xunfei_api_key]):
            console.print("[red]警告: 未检测到 API Key，请在 .env 文件中配置[/red]")
            console.print("[dim]可以使用 GOOGLE_API_KEY、OPENAI_API_KEY、ANTHROPIC_API_KEY、GROQ_API_KEY、SILICONFLOW_API_KEY 或 XUNFEI_API_KEY[/dim]\n")

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

