"""
主 Agent 实现
使用 LangGraph 构建的状态机式 Agent

该模块实现了网站信息提取的核心逻辑，包括：
- 动态加载不同 LLM 提供商
- 构建提取工作流
- 执行网站信息提取任务
- 处理提取结果和错误
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
# 标记各提供商的可用性状态
GEMINI_AVAILABLE = False
OPENAI_AVAILABLE = False
ANTHROPIC_AVAILABLE = False
GROQ_AVAILABLE = False
SILICONFLOW_AVAILABLE = False
XUNFEI_AVAILABLE = False
CEREBRAS_AVAILABLE = False

# 导入 Google Gemini
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    pass

# 导入 OpenAI
try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
    # SiliconFlow、讯飞和 Cerebras 也使用 OpenAI 兼容的 API
    SILICONFLOW_AVAILABLE = True
    XUNFEI_AVAILABLE = True
    CEREBRAS_AVAILABLE = True
except ImportError:
    pass

# 导入 Anthropic
try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    pass

# 导入 Groq
try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    pass


class AgentState(TypedDict):
    """Agent 状态定义
    
    定义了提取过程中的状态数据结构，包括：
    - messages: 消息历史记录
    - extracted_info: 提取的信息
    - url: 目标网站 URL
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    extracted_info: dict[str, Any]
    url: str | None


class SiteExtractorAgent:
    """网站信息提取 Agent
    
    基于 LangChain 和 LangGraph 实现的网站信息提取系统，
    支持多种 LLM 提供商，包括 Google Gemini、OpenAI、Anthropic、Groq、SiliconFlow 和讯飞。
    """

    def __init__(self, config: dict[str, Any]):
        """初始化 Agent

        Args:
            config: 配置字典，包含模型配置和 API Key 等信息
                - model_name: 模型名称
                - temperature: 生成温度
                - max_tokens: 最大令牌数
                - google_api_key: Google API Key（可选）
                - openai_api_key: OpenAI API Key（可选）
                - anthropic_api_key: Anthropic API Key（可选）
                - groq_api_key: Groq API Key（可选）
                - siliconflow_api_key: SiliconFlow API Key（可选）
                - xunfei_api_key: 讯飞 API Key（可选）
        """
        self.config = config
        self.llm = self._create_llm()
        self.graph = self._build_graph()

    def _create_llm(self):
        """创建 LLM 实例

        根据配置选择合适的 LLM 提供商并创建实例。
        优先顺序：Google Gemini → OpenAI → Anthropic → Groq → SiliconFlow → 讯飞

        Returns:
            对应的 LLM 实例

        Raises:
            ValueError: 当没有提供有效的 API Key 时
        """
        # 优先使用 Google Gemini
        if self.config.get("google_api_key") and GEMINI_AVAILABLE:
            return ChatGoogleGenerativeAI(
                model=self.config.get("model_name"),
                temperature=self.config.get("temperature", 0.0),
                api_key=self.config["google_api_key"]
            )
        
        # 备用 OpenAI
        elif self.config.get("openai_api_key") and OPENAI_AVAILABLE:
            return ChatOpenAI(
                model=self.config.get("model_name"),
                temperature=self.config.get("temperature", 0.0),
                api_key=self.config["openai_api_key"]
            )
        
        # 备用 Anthropic
        elif self.config.get("anthropic_api_key") and ANTHROPIC_AVAILABLE:
            return ChatAnthropic(
                model=self.config.get("model_name"),
                temperature=self.config.get("temperature", 0.0),
                api_key=self.config["anthropic_api_key"]
            )
        
        # 备用 Groq
        elif self.config.get("groq_api_key") and GROQ_AVAILABLE:
            return ChatGroq(
                model=self.config.get("model_name"),
                temperature=self.config.get("temperature", 0.0),
                api_key=self.config["groq_api_key"]
            )
        
        # 备用 SiliconFlow
        elif self.config.get("siliconflow_api_key") and SILICONFLOW_AVAILABLE:
            return ChatOpenAI(
                model=self.config.get("model_name"),
                temperature=self.config.get("temperature", 0.0),
                api_key=self.config["siliconflow_api_key"],
                base_url="https://api.siliconflow.cn/v1"
            )
        
        # 备用 讯飞
        elif self.config.get("xunfei_api_key") and XUNFEI_AVAILABLE:
            return ChatOpenAI(
                model=self.config.get("model_name"),
                temperature=self.config.get("temperature", 0.0),
                api_key=self.config["xunfei_api_key"],
                base_url="https://maas-api.cn-huabei-1.xf-yun.com/v2"
            )
        
        # 备用 Cerebras
        elif self.config.get("cerebras_api_key") and CEREBRAS_AVAILABLE:
            return ChatOpenAI(
                model=self.config.get("model_name"),
                temperature=self.config.get("temperature", 0.0),
                api_key=self.config["cerebras_api_key"],
                base_url="https://api.cerebras.ai/v1"
            )
        
        # 无可用的 API Key
        else:
            raise ValueError(
                "需要提供以下 API Key 之一: "
                "google_api_key、openai_api_key、anthropic_api_key、"
                "groq_api_key、siliconflow_api_key、xunfei_api_key 或 cerebras_api_key"
            )

    def _build_graph(self):
        """构建 LangGraph 工作流

        创建并配置 LangGraph 状态图，定义提取流程。
        当前实现为单节点流程：提取 → 结束

        Returns:
            编译后的 StateGraph 实例
        """
        # 创建状态图
        graph = StateGraph(AgentState)

        # 添加提取节点
        graph.add_node("extractor", self._extract_node)

        # 设置入口点为提取节点
        graph.set_entry_point("extractor")

        # 添加边：提取完成后结束流程
        graph.add_edge("extractor", END)

        # 编译并返回状态图
        return graph.compile()

    async def extract(self, url: str) -> dict[str, Any]:
        """执行提取任务

        启动提取工作流，从指定 URL 提取信息。

        Args:
            url: 目标网站 URL

        Returns:
            提取的信息字典，包含网站的标题、描述、内容等信息
        """
        # 初始化状态
        initial_state: AgentState = {
            "messages": [HumanMessage(content=f"请提取网站信息: {url}")],
            "extracted_info": {},
            "url": url
        }

        # 执行工作流
        result = await self.graph.ainvoke(initial_state)
        return result["extracted_info"]

    async def _extract_node(self, state: AgentState) -> AgentState:
        """提取节点：从网站提取信息

        执行实际的信息提取逻辑：
        1. 构建消息列表
        2. 调用 LLM 进行提取
        3. 解析 LLM 响应
        4. 处理提取结果或错误

        Args:
            state: 当前状态

        Returns:
            更新后的状态，包含提取结果
        """
        try:
            # 构建消息列表：系统提示 + 历史消息
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
            ] + list(state["messages"])

            # 调用 LLM 执行提取
            response = await self.llm.ainvoke(messages)

            # 初始化提取结果
            extracted_info = {
                "url": state["url"],
                "status": "success"
            }

            # 尝试解析响应为 JSON
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
                    # 直接使用响应内容
                    json_str = content

                # 解析 JSON 数据
                extracted_data = json.loads(json_str)
                extracted_info.update(extracted_data)
                
            except (json.JSONDecodeError, Exception) as parse_error:
                # 解析失败，使用原始文本
                extracted_info["raw_response"] = str(response.content)
                extracted_info["status"] = "parsed_error"
                extracted_info["parse_error"] = str(parse_error)

            # 更新消息历史
            updated_messages = list(state["messages"]) + [response]
            
            # 返回更新后的状态
            return {
                "messages": updated_messages,
                "extracted_info": extracted_info,
                "url": state["url"]
            }
            
        except Exception as e:
            # 处理执行错误
            error_response = AIMessage(content=f"提取失败: {str(e)}")
            updated_messages = list(state["messages"]) + [error_response]
            
            # 返回错误状态
            return {
                "messages": updated_messages,
                "extracted_info": {
                    "url": state["url"],
                    "status": "error",
                    "error": str(e)
                },
                "url": state["url"]
            }
