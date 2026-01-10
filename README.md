# Site Info Extractor Agent

基于最新 LangChain 和 LangGraph 构建的网站信息提取智能 Agent 系统。

## 快速开始

### 环境要求

- Python >= 3.10（推荐 3.11+）

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install
```

### 环境变量配置

复制 `.env.example` 为 `.env` 并配置相关 API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写必要的 API 密钥：
- `GOOGLE_API_KEY`: Google API 密钥（必需 - Gemini 模型）
- `OPENAI_API_KEY`: OpenAI API 密钥（可选）
- `ANTHROPIC_API_KEY`: Anthropic API 密钥（可选）
- `TAVILY_API_KEY`: Tavily 搜索 API 密钥（可选）

**⚠️ 安全注意事项**：
- `.env` 文件已被 `.gitignore` 保护，不会被提交到 Git 仓库
- 永远不要将包含真实 API 密钥的 `.env` 文件提交到 GitHub
- 如果意外提交了敏感文件，请使用 [git-crypt](https://github.com/AGWA/git-crypt) 或删除历史记录

**获取 Google API Key**：
1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 登录 Google 账户
3. 创建新的 API Key
4. 将 API Key 添加到 `.env` 文件的 `GOOGLE_API_KEY` 中

### 运行项目

```bash
python src/main.py
```

## 项目结构

```
site-info-extractor-agent/
├── src/
│   ├── agents/           # Agent 实现
│   ├── tools/            # 工具集合
│   ├── prompts/          # 提示词
│   ├── graph/            # LangGraph 工作流
│   ├── config/           # 配置管理
│   └── main.py           # 入口文件
├── tests/                # 测试文件
├── requirements.txt      # 依赖列表
├── .env.example          # 环境变量示例
└── README.md            # 项目说明
```

## 主要功能

- 基于浏览器的网页信息提取
- 智能内容解析和结构化
- 支持多种提取策略
- 可扩展的工具系统
- 基于 LangGraph 的状态管理
- 支持多个 LLM 提供商（Google Gemini、OpenAI、Anthropic）

## 支持的模型

- **Google Gemini**: gemini-2.5-flash-exp（默认）、gemini-1.5-flash、gemini-1.5-pro、gemini-pro
- **OpenAI**: gpt-4o-mini、gpt-4o、gpt-3.5-turbo
- **Anthropic**: claude-3-5-sonnet-20241022、claude-3-opus-20240229

**注意**：
- 如果遇到模型未找到错误（404 NOT_FOUND），请尝试其他 Gemini 模型
- 访问 [Google AI Models](https://ai.google.dev/models) 查看可用模型列表
- 某些模型可能需要在 Google AI Studio 中手动启用

## 开发说明

项目使用 LangGraph 构建工作流，支持复杂的提取任务编排。

## License

MIT
