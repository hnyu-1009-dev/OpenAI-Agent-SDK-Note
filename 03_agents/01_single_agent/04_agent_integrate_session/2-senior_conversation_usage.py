"""
示例 2：会话隔离与工具调用记忆。

这个例子比前一个更进一步，重点展示两个知识点：

1. Session 不只是记住普通文本消息，也可以记住工具调用相关上下文。
2. 不同 session_id 代表不同会话空间，彼此上下文隔离。

这对多用户系统尤其关键：
- 用户 A 的对话历史不能污染用户 B
- 同一数据库文件中也可以保存多个独立会话
"""

import asyncio

from openai import AsyncOpenAI

from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    SQLiteSession,
    function_tool,
    set_tracing_disabled,
)


BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = "sk-26d57c968c364e7bb14f1fc350d4bff0"
MODEL_NAME = "qwen3-max"


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)


@function_tool
def get_weather(city: str) -> str:
    """
    模拟获取天气信息的工具函数。
    """

    return f"天气信息: {city} 是晴天"


# 创建 Agent。
# 这里特别强调：当用户问天气时必须调用 `get_weather`。
agent = Agent(
    name="Assistant",
    instructions="你是一个天气助手，只回答天气问题。当用户问天气时必须调用 get_weather。",
    model=OpenAIChatCompletionsModel(
        model=MODEL_NAME,
        openai_client=client,
    ),
    tools=[get_weather],
)


# 创建两个 Session，二者共用同一个数据库文件，
# 但使用不同的 `session_id`，因此上下文相互独立。
session_user1 = SQLiteSession("user123", "conversation_123.db")
session_user2 = SQLiteSession("user1234", "conversation_123.db")


async def first_turn():
    """
    用户 1 的第一轮：询问天气。
    """

    print("\n--- User 1: 问天气 ---")
    result = await Runner.run(
        agent,
        "武汉的天气怎么样？",
        session=session_user1,
    )
    print(f"Agent: {result.final_output}")


async def second_turn():
    """
    用户 1 的第二轮：测试是否记住前面问过的问题。
    """

    print("\n--- User 1: 追问 ---")
    result = await Runner.run(
        agent,
        "我刚刚问了什么？",
        session=session_user1,
    )
    print(f"Agent: {result.final_output}")


async def third_turn():
    """
    用户 1 的第三轮：测试是否记住前面发生过函数调用。
    """

    print("\n--- User 1: 问函数调用 ---")
    result = await Runner.run(
        agent,
        "你刚刚调用了什么函数？",
        session=session_user1,
    )
    print(f"Agent: {result.final_output}")


async def four_turn():
    """
    用户 2 的第一轮：使用全新 session 测试上下文隔离。

    因为 `session_user2` 没有前面的历史记录，
    所以它不应该知道用户 1 那条会话中刚刚调用了什么函数。
    """

    print("\n--- User 2: 问函数调用 (全新上下文) ---")
    result = await Runner.run(
        agent,
        "你刚刚调用了什么函数？",
        session=session_user2,
    )
    print(f"Agent: {result.final_output}")


async def main():
    """
    顺序演示：
    - 用户 1 的连续多轮对话
    - 用户 2 的独立新会话
    """

    await first_turn()
    await second_turn()
    await third_turn()
    await four_turn()


if __name__ == "__main__":
    asyncio.run(main())
