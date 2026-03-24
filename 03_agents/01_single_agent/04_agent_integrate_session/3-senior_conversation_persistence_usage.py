"""
示例 3：流式输出、工具调用事件、Session 持久化三者结合。

这是本目录里信息量最大、也最接近真实项目的一份示例。

你会学到：

1. Agent 如何在流式运行中逐步产出事件
2. 如何监听工具调用开始、工具结果返回、消息创建等事件
3. 如何把这些事件相关数据保存到 SQLiteSession 中
4. 如何在第二轮对话中复用前一轮上下文

如果你未来要做真正可观测的 Agent 应用，
这个模式会非常常见。
"""

import asyncio

from openai import AsyncOpenAI
from openai.types.responses import (
    ResponseReasoningSummaryTextDeltaEvent,
    ResponseTextDeltaEvent,
)

from agents import (
    Agent,
    ModelSettings,
    OpenAIChatCompletionsModel,
    Runner,
    SQLiteSession,
    function_tool,
    set_tracing_disabled,
)


# ====== OpenAI-compatible 配置（以 DashScope 为例）======
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = "sk-26d57c968c364e7bb14f1fc350d4bff0"
MODEL_NAME = "qwen-plus"


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(True)


# 定义工具函数。
# 这里仍然使用一个模拟天气工具，方便聚焦 Agent 流程本身。
@function_tool
def get_weather(city: str) -> str:
    """
    返回指定城市的模拟天气结果。
    """

    return f"{city}：晴，24℃，风力2级"


async def main():
    """
    运行一个带工具、带 session、带流式事件监听的 Agent 示例。
    """

    # 1) 创建 Agent
    #
    # `model_settings=ModelSettings(tool_choice="required")` 的含义是：
    # 只要进入需要工具的场景，就强制模型使用工具，而不是自行编造答案。
    agent = Agent(
        name="天气助手",
        instructions=(
            "你是天气助手。\n"
            "当用户询问天气时，必须调用 get_weather 工具获取结果，禁止编造。\n"
            "如果用户没说城市，请追问用户城市。\n"
        ),
        model=OpenAIChatCompletionsModel(
            model=MODEL_NAME,
            openai_client=client,
        ),
        tools=[get_weather],
        model_settings=ModelSettings(tool_choice="required"),
    )

    # 2) 创建 Session，并指定落盘数据库文件名。
    #
    # 这意味着本次会话相关记录会被持久化到 `conversations1.db`。
    session = SQLiteSession("user_001_weather_chat", "conversations1.db")

    # ------------------ 第一轮（streamed） ------------------
    print("\n=== TURN 1 (streamed) ===")

    # 启动一次流式运行。
    result = Runner.run_streamed(
        agent,
        "武汉的天气怎么样？",
        session=session,
    )

    # 监听流式事件。
    async for event in result.stream_events():
        # A) 运行条目事件：工具调用 / 工具输出 / 消息创建
        #
        # 这些事件更偏向 Agent 运行过程层面，
        # 很适合用于日志、调试面板、监控界面。
        if event.type == "run_item_stream_event":
            # `tool_called`：表示 Agent 已经决定调用工具。
            if getattr(event, "name", None) == "tool_called":
                print(
                    "\n✅ tool_called:",
                    event.item.raw_item.name,
                    "args=",
                    event.item.raw_item.arguments,
                )

            # `tool_output`：表示工具执行完成并产出结果。
            elif getattr(event, "name", None) == "tool_output":
                print("\n✅ tool_output:", event.item.output)

            # `message_output_created`：表示创建了一条输出消息。
            elif getattr(event, "name", None) == "message_output_created":
                msg = event.item.raw_item
                print(f"\n🧾 message_output_created: msg:{msg}")

        # B) 原始响应事件：文本增量 / 推理摘要增量
        #
        # 这类事件更接近模型底层输出流。
        if event.type == "raw_response_event":
            # 文本增量事件：适合实时打印到界面。
            if isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta, end="", flush=True)

            # 推理摘要增量事件：有些模型会产出 reasoning summary。
            # 这里不额外打印，只是演示你可以区分处理不同事件类型。
            elif isinstance(event.data, ResponseReasoningSummaryTextDeltaEvent):
                pass

        # C) Agent 更新事件
        #
        # 在更复杂的多 Agent 场景中，当前活动 Agent 可能发生变化。
        # 本例虽然是单 Agent，也保留这段代码，帮助你建立“事件驱动”的观察习惯。
        if event.type == "agent_updated_stream_event":
            print("\n👤 agent_updated_stream_event:", event.new_agent.name)

    # 流式结束后，依然可以拿到完整最终结果。
    print("\n\nfinal_output:", result.final_output)

    # ------------------ 验证：session 中是否包含 tool call ------------------
    print("\n=== VERIFY session items ===")
    items = await session.get_items()
    print("session total items =", len(items))

    # 打印 session 中保存的全部条目，
    # 方便你直观看到：消息、工具调用、工具结果都被记录下来了。
    for i, it in enumerate(items, 1):
        print(it)

    # ------------------ 第二轮（非流式） ------------------
    print("\n=== TURN 2 (non-stream) ===")
    result2 = await Runner.run(
        agent,
        "我刚刚问了你什么？",
        session=session,
    )
    print("final_output:", result2.final_output)

    print("\nDone. conversations1.db 已写入（包含 tool calls / outputs / messages）。")


if __name__ == "__main__":
    asyncio.run(main())
