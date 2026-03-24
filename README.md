# OpenAI-Agent-SDK-Note

一个面向 `OpenAI Agents SDK` 的学习型示例仓库，按主题拆分了模型调用、工具集成、单 Agent、流式事件、MCP、多 Agent，以及一个基于 FastAPI + SSE 的小项目。

这个仓库的特点不是“做成一个完整产品”，而是把常见能力拆成一组可以单独运行、单独理解的样例，适合用来：

- 快速上手 `openai-agents`
- 对照脚本理解 Agent、Tool、Session、Stream Event 的用法
- 练习 OpenAI 兼容接口的接入方式
- 作为后续项目的代码片段仓库

## 仓库结构

```text
.
├─00_environment                # 环境依赖
├─01_models                     # 模型层：基础输出、结构化输出
├─02_tools                      # 工具调用与底层 function calling
├─03_agents                     # 单 Agent：模型、运行、工具、会话
├─04_output_items               # Output items 观察与解析
├─05_stream_events              # 流式事件
├─06_mcp&multi_agent            # MCP 与多 Agent 协作
├─07_projects                   # 项目化示例：SSE 聊天 demo
├─01_model_plane.ipynb          # 模型相关 notebook
├─02_capability_plane_tool.ipynb
├─03_capability_plane_agent.ipynb
├─test.py                       # 简单 Agent 运行样例
└─README.md
```

## 你会学到什么

### 1. Models

位于 `01_models/`，主要覆盖：

- 普通文本输出
- 新旧写法对比
- 结构化输出
- OpenAI 兼容模型接入

### 2. Tools

位于 `02_tools/`，主要覆盖：

- 底层 `chat.completions` 的工具定义
- 函数参数 schema
- 工具调用结果回填

### 3. Agents

位于 `03_agents/`，主要覆盖：

- `Agent` 如何绑定模型
- `Runner.run_sync`、`Runner.run`、`Runner.run_streamed`
- Agent 集成工具
- 会话与持久化会话

### 4. Output Items

位于 `04_output_items/`，主要覆盖：

- `final_output`
- `response output item`
- `tool call item`
- `tool call output item`
- `reasoning summary`

### 5. Stream Events

位于 `05_stream_events/`，主要覆盖：

- 流式输出过程中的事件监听
- 文本增量输出
- 运行过程观察

### 6. MCP & Multi-Agent

位于 `06_mcp&multi_agent/`，主要覆盖：

- 本地 MCP Server / Client 示例
- HTTP / SSE 方式接入 MCP
- `agent.as_tool()`
- Agent handoff 与多 Agent 协作

### 7. Projects

位于 `07_projects/`，提供一个项目化示例：

- FastAPI 后端
- SSE 流式响应
- 简单前端页面
- Agent + Tool 的端到端演示

## 环境准备

建议使用 `Python 3.10+`。

### 1. 创建虚拟环境

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. 安装依赖

仓库里有两种依赖声明方式：

- `00_environment/requirements.txt`
- `00_environment/setup.py`

推荐直接安装 `setup.py` 中声明的完整依赖：

```powershell
pip install -e .\00_environment
```

如果你只想跑最基础的脚本，也可以：

```powershell
pip install -r .\00_environment\requirements.txt
pip install fastapi uvicorn openai
```

## 环境变量配置

仓库中不少样例依赖 `.env`。建议统一使用环境变量，而不是把 `API_KEY` 写死在代码里。

可以在项目根目录创建 `.env`：

```env
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL_NAME=gpt-5-mini

SF_API_KEY=your_siliconflow_key
SF_BASE_URL=https://api.siliconflow.cn/v1
SF_MODEL_NAME=Qwen/Qwen3-32B

AL_BAILIAN_API_KEY=your_dashscope_key
AL_BAILIAN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AL_BAILIAN_MODEL_NAME=qwen3-max
```

## 推荐学习顺序

如果你是第一次看这个仓库，建议按下面顺序：

1. `01_model_plane.ipynb`
2. `01_models/01_basic_content_output/`
3. `01_models/02_senior_structured_output/`
4. `02_tools/1.1-basic-tools-usage.py`
5. `03_agents/01_single_agent/`
6. `04_output_items/`
7. `05_stream_events/1-stream_event-usage.py`
8. `06_mcp&multi_agent/`
9. `07_projects/`

这样看下来，路径会比较自然：先理解模型，再理解工具，再进入 Agent、流式、MCP 和项目化落地。

## 快速运行示例

### 基础模型调用

```powershell
python .\01_models\01_basic_content_output\1.1-basic-usage.py
```

### 工具调用

```powershell
python .\02_tools\1.1-basic-tools-usage.py
```

### 单 Agent 同步运行

```powershell
python .\03_agents\01_single_agent\02_agent__run\1-runner_run_sync-usage.py
```

### 流式事件

```powershell
python .\05_stream_events\1-stream_event-usage.py
```

### 多 Agent

```powershell
python '.\06_mcp&multi_agent\02_multi_agent\1-agent_as_tool-usage.py'
```

### 项目化 SSE 示例

启动后端：

```powershell
python .\07_projects\backend\app.py
```

或者：

```powershell
python .\07_projects\server.py
```

前端页面在：

```text
07_projects/front/index.html
```

后端默认监听：

```text
http://localhost:8200
```

## 重点目录说明

### `00_environment/`

- `requirements.txt`：最小依赖
- `setup.py`：包含 `fastapi`、`uvicorn`、`python-dotenv`、`openai-agents`

### `03_agents/01_single_agent/`

这是仓库里最值得细看的部分，基本覆盖了单 Agent 的核心能力：

- `01_agent_integrate_model/`：模型接入方式
- `02_agent__run/`：不同运行方式
- `03_agent_integrate_tool/`：Agent 结合工具
- `04_agent_integrate_session/`：对话上下文与持久化

### `06_mcp&multi_agent/`

如果你已经理解了单 Agent，这部分建议重点看：

- `01_mcp/client/`
- `01_mcp/server/`
- `02_multi_agent/`

### `07_projects/`

这是从“单脚本示例”走向“项目化结构”的过渡目录，适合拿来继续改造成自己的 demo。

## 注意事项

1. 仓库中的部分脚本目前仍然写死了 `BASE_URL`、`API_KEY`、`MODEL_NAME`，运行前请先替换成你自己的配置。
2. 建议优先把这些硬编码改成读取 `.env`，这样更适合长期维护。
3. `.gitignore` 已忽略 `.env`，不要把真实密钥提交到仓库。
4. 如果你已经把真实密钥写进代码或提交过，应该立即更换该密钥。
5. `06_mcp&multi_agent` 目录名包含 `&`，在 PowerShell 中执行命令时要记得给路径加引号。

## 适合怎么用这个仓库

- 当作学习笔记：按目录顺序逐个运行
- 当作代码片段库：从现有脚本里复制最小可用示例
- 当作 demo 基础工程：从 `07_projects/` 开始继续扩展

## 后续可继续补充的方向

- 为每个目录单独补一个 README
- 统一所有示例的环境变量读取方式
- 增加 `uv` 或 `poetry` 的安装方式
- 为 `07_projects` 增加启动说明和接口文档
- 补充测试与常见报错排查
