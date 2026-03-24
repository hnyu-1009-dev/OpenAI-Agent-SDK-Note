"""
一个最小可运行的“Agent + FastAPI + SSE”后端示例。

这个文件的目标是让你看清一条完整链路：

1. 浏览器发起请求
2. FastAPI 接收请求
3. 后端启动一个流式 Agent 运行
4. Agent 在执行中不断产出事件
5. 后端把这些事件转换成 SSE 格式
6. 浏览器通过 EventSource 实时接收并渲染

这已经是一个非常典型的 AI 应用后端模式。
"""

import json
from typing import AsyncGenerator, Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent

from agents import (
    Agent,
    ModelSettings,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    set_tracing_disabled,
)


# 创建 FastAPI 应用实例。
app = FastAPI()


# 配置 CORS（跨域资源共享）。
#
# 因为前端页面和后端接口可能不在同一个端口，
# 浏览器会进行跨域限制，所以这里放开跨域策略用于演示。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 模型服务配置。
BASE_URL = "https://api.siliconflow.cn/v1"
API_KEY = "sk-vnxijjgodhcjisacoilnebjzzlqmrwyuluqdxcpwauocgqjm"
MODEL_NAME = "Qwen/Qwen3-32B"


# 创建异步客户端。
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(True)


@function_tool
def get_weather(city: str) -> str:
    """
    一个最简单的天气工具。
    """

    return f"{city}：晴，24℃，风力2级"


# 预先创建一个全局 Agent。
#
# 在这种简单项目里，把 Agent 当作应用级单例对象使用是很常见的。
agent = Agent(
    name="天气助手",
    instructions=(
        "你是天气助手。\n"
        "用户问天气时必须调用 get_weather 工具获取结果，禁止编造。\n"
        "如果用户没说城市，请追问城市。\n"
        "如果用户只是打招呼或闲聊，不要调用工具，直接礼貌回应。\n"
    ),
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[get_weather],
    # 用 `auto` 而不是 `required`，避免用户随便闲聊时也被强行调用工具。
    model_settings=ModelSettings(tool_choice="auto"),
)


def sse(event: str, data: dict) -> str:
    """
    把一条事件包装成标准 SSE 文本格式。

    SSE（Server-Sent Events）要求服务端按如下格式返回：

    event: 事件名
    data: JSON字符串

    并以空行结尾，表示一条完整事件结束。
    """

    return f"event: {event}\n" f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


async def run_agent_to_sse(
    user_text: str,
    conversation_id: Optional[str],
) -> AsyncGenerator[str, None]:
    """
    运行 Agent，并把流式事件转换成 SSE 数据流。

    这是后端最核心的函数。

    它做的事情包括：
    1. 调用 `Runner.run_streamed(...)` 启动流式 Agent
    2. 监听 Agent 的各类事件
    3. 把内部事件转换成前端可理解的 SSE 事件
    4. 通过 `yield` 一段一段推送给浏览器
    """

    # 启动一次流式 Agent 运行。
    result = Runner.run_streamed(agent, user_text)

    # 用来记录：
    # 工具调用 ID -> 工具名称
    #
    # 因为工具开始调用和工具完成返回是两个不同事件，
    # 中间需要靠 call_id 把它们对应起来。
    tool_name_by_call_id: Dict[str, str] = {}

    try:
        async for ev in result.stream_events():
            # 1. 处理结构化执行节点事件
            if ev.type == "run_item_stream_event":
                name = getattr(ev, "name", None)

                # 工具开始调用
                if name == "tool_called":
                    print("工具调用:", ev.item)
                    tool_name = ev.item.raw_item.name
                    call_id = getattr(ev.item.raw_item, "call_id", None)

                    if call_id:
                        tool_name_by_call_id[call_id] = tool_name

                    yield sse(
                        "tool_started",
                        {
                            "tool_name": tool_name,
                            "call_id": call_id,
                        },
                    )

                # 工具执行完成
                elif name == "tool_output":
                    print("工具输出:", ev.item)

                    # `ToolCallOutputItem.raw_item` 往往是一个 dict，
                    # 里面带有 `call_id` 和原始输出信息。
                    out = ev.item
                    raw_item = out.raw_item
                    call_id = raw_item.get("call_id")

                    if call_id and call_id in tool_name_by_call_id:
                        tool_name = tool_name_by_call_id[call_id]
                        yield sse(
                            "tool_completed",
                            {
                                "tool_name": tool_name,
                                "tool_result": out.output,
                            },
                        )

            # 2. 处理原始文本增量事件
            #
            # 这一类事件用于前端“打字机效果”。
            if ev.type == "raw_response_event" and isinstance(ev.data, ResponseTextDeltaEvent):
                yield sse("text_delta", {"text": ev.data.delta})

            # 3. 处理 Agent 更新事件
            #
            # 当前示例是单 Agent，通常不会频繁切换；
            # 但保留这个事件有助于以后扩展多 Agent 项目。
            if ev.type == "agent_updated_stream_event":
                yield sse("agent_updated", {"agent_name": ev.new_agent.name})

        # 4. 整个运行结束后，发送完成事件。
        yield sse("run_completed", {"final_output": result.final_output})

    except Exception as e:
        # 把异常也包装成 SSE 事件发给前端，
        # 这样前端可以统一处理错误状态。
        yield sse("error", {"message": str(e)})


@app.get("/api/chat/sse")
async def chat_sse_get(query: str, conversation_id: Optional[str] = None):
    """
    SSE 聊天接口。

    前端会通过 EventSource 请求这个接口，
    并持续接收一条条流式事件。
    """

    async def gen():
        async for chunk in run_agent_to_sse(query, conversation_id):
            yield chunk

    return StreamingResponse(gen(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8200)
