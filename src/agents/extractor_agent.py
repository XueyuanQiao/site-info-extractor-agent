"""
主 Agent 实现
使用 LangGraph 构建的状态机式 Agent
"""

import warnings
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator

# 抑制 Python 3.14 与 Pydantic V1 的兼容性警告
warnings.filterwarnings(
    "ignore",
    message=".*Core Pydantic V1 functionality.*",
    category=UserWarning
)


class AgentState(TypedDict):
    """Agent 状态定义"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    extracted_info: dict
    url: str | None


class SiteExtractorAgent:
    """网站信息提取 Agent"""
    
    def __init__(self, config: dict):
        """初始化 Agent
        
        Args:
            config: 配置字典，包含模型配置等
        """
        self.config = config
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
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
    
    async def extract(self, url: str) -> dict:
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
    def _extract_node(self, state: AgentState) -> AgentState:
        """提取节点：从网站提取信息"""
        response = AIMessage(content=f"已处理提取请求: {state['url']}")
        return {
            "messages": state["messages"] + [response],
            "extracted_info": {"url": state["url"], "status": "extracted"},
            "url": state["url"]
        }
