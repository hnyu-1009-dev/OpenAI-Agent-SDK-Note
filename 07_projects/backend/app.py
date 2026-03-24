"""
完整的智能客服后端实现
文件：backend/app.py

这个文件比根目录下的 `server.py` 更完整一些，
可以把它当作“项目版”的后端示例。

你可以重点学习四件事：

1. FastAPI 如何提供 SSE 接口
2. Agent 如何被封装进 Web 后端
3. Agent 流式事件如何转成前端可消费的 SSE 事件
4. 一个 AI 聊天后端的代码分层应该怎么组织
"""

import json
from typing import AsyncGenerator, Optional

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


# 1. 创建 FastAPI 应用
app = FastAPI(title="智能客服系统", version="1.0.0")


# 2. 配置 CORS（跨域资源共享）
#
# 浏览器从前端页面访问后端接口时，如果端口不同、域名不同，
# 就会遇到跨域问题。CORS 中间件会自动给响应补上相应的跨域头。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 演示环境全部放开；生产环境建议限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

 
# 3. 配置模型客户端
BASE_URL = "https://api.siliconflow.cn/v1"
API_KEY = ""
MODEL_NAME = "Qwen/Qwen3-32B"


# 创建异步模型客户端。
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)


# 关闭 tracing，避免在演示环境中带来额外依赖或鉴权问题。
set_tracing_disabled(True)


# 4. 定义工具函数
@function_tool
def get_weather(city: str) -> str:
    """
    获取城市天气信息（模拟工具）。

    在真实项目中，这里通常会：
    1. 调用真实天气 API
    2. 解析返回数据
    3. 转成业务可读文本或结构化结果
    """

    weather_data = {
        "北京": "北京：晴，24℃，风力2级，空气质量良",
        "上海": "上海：多云，26℃，风力3级，空气质量优",
        "武汉": "武汉：阴，22℃，风力1级，空气质量良",
        "广州": "广州：阵雨，28℃，风力2级，空气质量优",
    }
    return weather_data.get(city, f"{city}：天气信息暂时无法获取")


# 5. 创建 Agent 实例
agent = Agent(
    name="天气助手",
    instructions="你是专业的天气助手，专门回答天气相关问题。",
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[get_weather],
    # `required` 表示强制模型优先依赖工具。
    # 这种模式更适合“问题明确属于工具职责”的演示场景。
    model_settings=ModelSettings(tool_choice="required"),
)


# 6. SSE 事件格式化函数
def sse(event: str, data: dict) -> str:
    """
    将事件和数据格式化为 SSE 文本。

    SSE 协议要求形如：

    event: 事件名
    data: JSON数据

    并以两个换行结束，表示这一条事件发送完毕。
    """

    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


# 7. Agent 执行与 SSE 转换的核心函数
async def run_agent_to_sse(user_text: str) -> AsyncGenerator[str, None]:
    """
    运行 Agent，并把整个执行过程转成 SSE 事件流。

    这是整个后端最关键的一层“桥接逻辑”：

    Agent 内部产出的是流式执行事件，
    浏览器前端能消费的是 SSE 文本流，
    这个函数负责完成二者之间的转换。
    """

    # 用来保存：
    # 工具调用 ID -> 工具名称
    tool_name_by_call_id: dict[str, str] = {}

    # 通过 `run_streamed` 获取流式运行结果对象。
    result = Runner.run_streamed(agent, user_text)

    try:
        # 异步遍历全部流式事件。
        async for event in result.stream_events():
            # 1. 处理运行节点事件
            if event.type == "run_item_stream_event":
                event_name = event.name

                # 1.1 工具开始调用
                if event_name == "tool_called":
                    print(f"工具调用: {event.item}")

                    tool_name = event.item.raw_item.name
                    call_id = getattr(event.item.raw_item, "call_id", None)

                    if call_id:
                        tool_name_by_call_id[call_id] = tool_name

                    yield sse(
                        "tool_started",
                        {
                            "tool_name": tool_name,
                            "call_id": call_id,
                        },
                    )

                # 1.2 工具调用完成
                elif event_name == "tool_output":
                    print(f"工具输出: {event.item}")

                    output_item = event.item
                    raw_item = output_item.raw_item
                    call_id = raw_item.get("call_id")

                    if call_id and call_id in tool_name_by_call_id:
                        tool_name = tool_name_by_call_id[call_id]
                        yield sse(
                            "tool_completed",
                            {
                                "tool_name": tool_name,
                                "tool_result": output_item.output,
                            },
                        )

            # 2. 处理文本增量事件
            #
            # 这是前端实现“实时打字机效果”的关键来源。
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                yield sse("text_delta", {"text": event.data.delta})

            # 3. 处理 Agent 更新事件
            if event.type == "agent_updated_stream_event":
                yield sse("agent_updated", {"agent_name": event.new_agent.name})

        # 4. 所有事件结束后，发送 run_completed。
        yield sse("run_completed", {"final_output": result.final_output})

    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Agent执行出错: {error_msg}")
        yield sse("error", {"message": error_msg})


# 8. FastAPI 路由定义
@app.get("/api/chat/sse")
async def chat_sse_get(query: str):
    """
    流式聊天 API。

    前端通过这个接口建立 SSE 长连接，
    后端会持续发送：
    - 工具开始
    - 工具完成
    - 文本增量
    - 运行完成
    等一系列事件。
    """

    async def generate_sse():
        async for chunk in run_agent_to_sse(query):
            yield chunk

    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# 9. 健康检查接口
@app.get("/health")
async def health_check():
    """
    一个简单的健康检查接口。

    常用于：
    - 部署后确认服务是否启动
    - 监控系统定时探测
    - 负载均衡器健康检查
    """

    return {
        "status": "healthy",
        "service": "智能客服系统",
        "version": "1.0.0",
    }


# 10. 启动应用
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8200,
    )
