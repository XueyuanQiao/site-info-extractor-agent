"""
主 Agent 实现
使用 LangGraph 构建的状态机式 Agent
"""

import warnings
import json
import operator
from typing import TypedDict, Annotated, Any
from collections.abc import Sequence
from pathlib import Path
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

# 抑制 Python 3.14 与 Pydantic V1 的兼容性警告
warnings.filterwarnings(
    "ignore",
    message=".*Core Pydantic V1 functionality.*",
    category=UserWarning
)

# 加载系统提示词
SYSTEM_PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "system_prompt.md"
SYSTEM_PROMPT = SYSTEM_PROMPT_FILE.read_text(encoding="utf-8") if SYSTEM_PROMPT_FILE.exists() else "你是一个专业的网站信息提取专家。"

# 动态导入 LLM 提供商
GEMINI_AVAILABLE = False
OPENAI_AVAILABLE = False
ANTHROPIC_AVAILABLE = False

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    pass

try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    pass

try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    pass


class AgentState(TypedDict):
    """Agent 状态定义"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    extracted_info: dict[str, Any]  # 修复类型注解，使用大写的 Any
    url: str | None


class SiteExtractorAgent:
    """网站信息提取 Agent"""

    def __init__(self, config: dict[str, Any]):
        """初始化 Agent

        Args:
            config: 配置字典，包含模型配置等
        """
        self.config = config
        self.llm = self._create_llm()
        self.graph = self._build_graph()

    def _create_llm(self):
        """创建 LLM 实例

        Returns:
            LLM 实例
        """
        # 优先使用 Google Gemini
        if self.config.get("google_api_key") and GEMINI_AVAILABLE:
            return ChatGoogleGenerativeAI(
                model=self.config.get("model_name", "gemini-2.5-flash"),
                temperature=self.config.get("temperature", 0.0),
                api_key=self.config["google_api_key"]
            )
        # 备用 OpenAI
        elif self.config.get("openai_api_key") and OPENAI_AVAILABLE:
            return ChatOpenAI(
                model=self.config.get("model_name", "gpt-4o-mini"),
                temperature=self.config.get("temperature", 0.0),
                api_key=self.config["openai_api_key"]
            )
        # 备用 Anthropic
        elif self.config.get("anthropic_api_key") and ANTHROPIC_AVAILABLE:
            return ChatAnthropic(
                model=self.config.get("model_name", "claude-3-5-sonnet-20241022"),
                temperature=self.config.get("temperature", 0.0),
                api_key=self.config["anthropic_api_key"]
            )
        else:
            raise ValueError("需要提供 google_api_key、openai_api_key 或 anthropic_api_key")
    
    def _build_graph(self):
        """构建 LangGraph 工作流

        Returns:
            构建好的 StateGraph 实例
        """
        graph = StateGraph(AgentState)

        # 添加节点
        graph.add_node("extractor", self._extract_node)

        # 设置入口点
        graph.set_entry_point("extractor")

        # 添加边
        graph.add_edge("extractor", END)

        return graph.compile()
    
    async def extract(self, url: str) -> dict[str, Any]:
        """执行提取任务

        Args:
            url: 目标网站 URL

        Returns:
            提取的信息字典
        """
        initial_state: AgentState = {
            "messages": [HumanMessage(content=f"请提取网站信息: {url}")],
            "extracted_info": {},
            "url": url
        }

        result = await self.graph.ainvoke(initial_state)
        return result["extracted_info"]
    
    # 实现各个节点函数
    async def _extract_node(self, state: AgentState) -> AgentState:
        """提取节点：从网站提取信息"""
        try:
            # 构建消息列表
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
            ] + list(state["messages"])

            # 调用 LLM
            response = await self.llm.ainvoke(messages)

            # 尝试解析响应为 JSON，如果失败则使用原始文本
            extracted_info = {"url": state["url"], "status": "success"}

            try:
                # 确保获取字符串类型的 content
                content = response.content
                if isinstance(content, list):
                    content = " ".join(str(item) for item in content)
                elif not isinstance(content, str):
                    content = str(content)

                # 尝试从响应中提取 JSON
                if "```json" in content:
                    # 提取 ```json 和 ``` 之间的内容
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    json_str = content[json_start:json_end].strip()
                elif "```" in content:
                    # 提取 ``` 和 ``` 之间的内容
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    json_str = content[json_start:json_end].strip()
                else:
                    json_str = content

                extracted_data = json.loads(json_str)
                extracted_info.update(extracted_data)
            except (json.JSONDecodeError, Exception) as e:
                # 解析失败，使用原始文本
                extracted_info["raw_response"] = str(response.content)
                extracted_info["status"] = "parsed_error"

            # 将序列转换为列表以避免类型错误
            updated_messages = list(state["messages"]) + [response]
            return {
                "messages": updated_messages,
                "extracted_info": extracted_info,
                "url": state["url"]
            }
        except Exception as e:
            # 错误处理
            error_response = AIMessage(content=f"提取失败: {str(e)}")
            updated_messages = list(state["messages"]) + [error_response]
            return {
                "messages": updated_messages,
                "extracted_info": {"url": state["url"], "status": "error", "error": str(e)},
                "url": state["url"]
            }
