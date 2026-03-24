"""
示例 8：使用 handoff 把用户问题交给专家 Agent。

这个示例和前一个 `agent_as_tool` 最大的不同是：

- `as_tool`：总控 Agent 始终掌握主导权，只把专家当工具调用
- `handoff`：总控 Agent 会把控制权真正移交给专家 Agent

因此 handoff 更像：
“前台把客户转接给专业部门，由专业部门继续主导对话。”
"""

import asyncio

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


# ====== OpenAI-compatible 配置（以 DashScope/Qwen 示例）======
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = "sk-26d57c968c364e7bb14f1fc350d4bff0"
MODEL_NAME = "qwen3-max"


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(True)


# ====== 1) 底层真实工具（演示：写死）======
@function_tool
def get_weather(city: str) -> str:
    """
    查询天气。
    """

    return f"{city}：晴，24℃，风力2级"


@function_tool
def get_air_quality(city: str) -> str:
    """
    查询空气质量。
    """

    return f"{city}：AQI 55（良），PM2.5 18"


# ====== 2) 专家 Agents（接管后自己输出最终答案）======
weather_agent = Agent(
    name="Weather agent",
    instructions=(
        "你是天气专家。\n"
        "当用户问天气时：\n"
        "1) 如果用户没说城市，先追问城市（不要调用工具）。\n"
        "2) 如果用户说了城市，必须调用 get_weather 工具获取结果，禁止编造。\n"
        "3) 输出要口语化、简短。\n"
    ),
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[get_weather],
    # 这里用 `auto` 而不是 `required`，
    # 因为当用户没提供城市时，专家应该先追问，而不是强行调用工具。
    model_settings=ModelSettings(tool_choice="auto"),
)


aqi_agent = Agent(
    name="AQI agent",
    instructions=(
        "你是空气质量专家。\n"
        "当用户问空气质量/AQI/PM2.5：\n"
        "1) 如果用户没说城市，先追问城市（不要调用工具）。\n"
        "2) 如果用户说了城市，必须调用 get_air_quality 工具获取结果，禁止编造。\n"
        "3) 输出要口语化、简短。\n"
    ),
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[get_air_quality],
    model_settings=ModelSettings(tool_choice="auto"),
)


# ====== 3) 分诊 Agent（handoffs：把控制权交给专家）======
triage_agent = Agent(
    name="Triage agent",
    instructions=(
        "你是分诊助手，只负责把用户的问题交给合适的专家处理。\n"
        "规则：\n"
        "- 用户问【天气/温度/下雨/晴天】-> 交接给 Weather agent。\n"
        "- 用户问【空气质量/AQI/PM2.5/雾霾】-> 交接给 AQI agent。\n"
        "- 如果用户同时问天气+空气质量：\n"
        "  先交接给 Weather agent 处理天气部分，回答后引导用户继续问空气质量（让用户再问一次）。\n"
        "你自己不要调用任何工具，也不要自己回答具体数据。\n"
    ),
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    handoffs=[weather_agent, aqi_agent],
)


async def main():
    """
    演示分诊 Agent 如何把控制权交给专家 Agent。
    """

    user_question = "武汉天气怎么样？顺便空气质量呢？"

    result = Runner.run_streamed(triage_agent, user_question)

    print("\n=== STREAM EVENTS ===")

    async for event in result.stream_events():
        # A) agent 更新事件
        #
        # 这是 handoff 场景里最有代表性的信号。
        # 一旦发生交接，你会看到当前活跃 Agent 变成另一个专家 Agent。
        if event.type == "agent_updated_stream_event":
            print("\n👤 agent_updated_stream_event ->", event.new_agent.name)

        # B) 执行节点事件
        if event.type == "run_item_stream_event":
            name = getattr(event, "name", None)

            if name == "tool_called":
                tool_name = event.item.raw_item.name
                tool_args = event.item.raw_item.arguments
                print(f"\n✅ tool_called: {tool_name} args={tool_args}")

            elif name == "tool_output":
                print(f"\n✅ tool_output: {event.item.output}")

            elif name == "message_output_created":
                msg = event.item.raw_item
                print(f"\n🧾 message_output_created: role={getattr(msg, 'role', None)}")

        # C) 文本增量
        # handoff 之后，最终输出内容会由“接管后的专家 Agent”流出来。
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)

    print("\n\n=== FINAL OUTPUT ===")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
