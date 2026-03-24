"""
示例 1：最基础的多轮对话记忆。

这个例子展示了 `SQLiteSession` 的核心价值：

1. 用同一个 session 运行多轮对话
2. Agent 能记住上一轮用户说过什么
3. 后续问题可以引用前文上下文

这是做聊天机器人、助手类产品时最常见的能力之一。
"""

import asyncio

from openai import AsyncOpenAI

from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    SQLiteSession,
    set_tracing_disabled,
)


BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = "sk-26d57c968c364e7bb14f1fc350d4bff0"
MODEL_NAME = "qwen3-max"


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)


# 创建一个 Agent。
agent = Agent(
    name="Assistant",
    instructions="回答要非常简洁",
    model=OpenAIChatCompletionsModel(
        model=MODEL_NAME,
        openai_client=client,
    ),
)


# 创建一个 SQLite 会话实例。
#
# 这里传入的是 session_id。
# 在未额外指定数据库文件时，SDK 会使用默认的 SQLite 持久化位置或默认配置。
# 你可以把它理解为：
# “这个对话线程的唯一身份标识是 `conversation_123`。”
session = SQLiteSession("conversation_123")


async def first_turn():
    """
    第一轮：建立上下文。
    """

    result = await Runner.run(
        agent,
        "金门大桥在哪个城市",
        session=session,
    )
    print(f"Turn 1 Output: {result.final_output}")


async def second_turn():
    """
    第二轮：测试 Agent 是否记得上一轮问题。
    """

    result = await Runner.run(
        agent,
        "我刚刚问了什么？",
        session=session,
    )
    print(f"Turn 2 Output: {result.final_output}")


async def third_turn():
    """
    第三轮：测试指代理解。

    “它的人口是多少？” 里的“它”没有直接写出城市名，
    Agent 需要结合前面对话上下文来推断“它”指的是哪个城市。
    """

    result = await Runner.run(
        agent,
        "它的人口是多少？",
        session=session,
    )
    print(f"Turn 3 Output: {result.final_output}")


async def get_items():
    """
    调试辅助函数：查看 session 中已保存的所有条目。
    """

    print("--- Session Items ---")
    items = await session.get_items()
    for it in items:
        print(it)


async def main():
    """
    按顺序执行三轮对话，共用同一个 session。
    """

    await first_turn()
    await second_turn()
    await third_turn()
    # 如果你想查看底层会话记录，可以取消下面一行的注释。
    # await get_items()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
