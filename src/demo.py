# pip install -qU "langchain[google-genai]" 调用 Gemini 模型

import sys
import os
import warnings

# 过滤冗余警告
warnings.filterwarnings("ignore", category=UserWarning, message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater.")

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from config.settings import settings

def get_weather(city: str) -> str:
    """获取指定城市的天气"""
    return f"{city} 天气总是晴朗！"

# 确保 Google API 密钥存在
if not settings.google_api_key:
    print("\n Google API key not found!")
    print("Please set GOOGLE_API_KEY in your .env file.")
    print("\nExiting...\n")
    exit()

# 直接创建 Gemini 模型实例（与 extractor_agent.py 相同的方式）
llm = ChatGoogleGenerativeAI(
    model=settings.gemini_model_name,
    temperature=0.0,
    api_key=settings.google_api_key
)

def main():
    # 构建消息列表
    messages = [
        SystemMessage(content="你是一个乐于助人的助手"),
        HumanMessage(content="旧金山天气如何？")
    ]
    
    # 同步调用 LLM
    response = llm.invoke(messages)
    
    # 输出结果
    print("\nLLM Response:")
    print(response.content)

# 运行同步函数
if __name__ == "__main__":
    main()