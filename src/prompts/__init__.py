"""
提示词模块
包含系统提示词和模板
"""

from pathlib import Path

# 获取提示词文件路径
PROMPTS_DIR = Path(__file__).parent


def load_system_prompt() -> str:
    """加载系统提示词
    
    Returns:
        系统提示词内容
    """
    prompt_file = PROMPTS_DIR / "system_prompt.md"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8")
    
    # 默认提示词
    return """你是一个专业的网站信息提取专家。你的任务是从给定的网站内容中提取关键信息。

请遵循以下原则：
1. 准确提取信息，不要编造
2. 结构化组织提取的信息
3. 保持信息的原始语境
4. 对于不确定的信息，标注为未知"""
