"""
示例 2：把一次运行结果转换成下一轮输入 `to_input_list()`。

这个示例非常重要，因为它说明了：
Agent 的运行结果不仅能“看”，还能“复用”。

`to_input_list()` 的作用可以简单理解为：

“把刚才这轮运行中对下一轮有价值的上下文，整理成标准输入列表。”

这在以下场景里很实用：

1. 你不想直接使用 Session，但仍想手动维护多轮上下文
2. 你想调试 Agent 每一轮究竟把哪些信息带到了下一轮
3. 你想把一次运行的结果拼接进另一个工作流
"""

import asyncio

from openai import AsyncOpenAI

from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    set_tracing_disabled,
)


BASE_URL = "https://api.siliconflow.cn/v1"
API_KEY = "sk-vnxijjgodhcjisacoilnebjzzlqmrwyuluqdxcpwauocgqjm"
MODEL_NAME = "Qwen/Qwen3-32B"


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)

# 建议先关闭 tracing，避免调试 `to_input_list()` 时混入额外干扰。
set_tracing_disabled(disabled=True)


@function_tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息。

    这里额外打印了一行日志，方便你观察工具什么时候被真正执行。
    """

    print(f"  >>> [工具调用] 正在查询 {city} 的天气...")
    return f"{city}是晴天，气温 28 度"


async def main():
    """
    先完成第一轮运行，再把结果转成第二轮输入。
    """

    agent = Agent(
        name="天气助手",
        instructions="你是一个天气助手，负责查询天气。",
        model=OpenAIChatCompletionsModel(
            model=MODEL_NAME,
            openai_client=client,
        ),
        tools=[get_weather],
    )

    print("=== 第一轮：询问天气 ===")

    # 第一轮运行。
    result1 = await Runner.run(agent, "武汉的天气怎么样？")
    print(f"Agent回复: {result1.final_output}\n")

    # `to_input_list()` 会把这一轮结果整理为“下一轮可直接继续使用”的输入列表。
    #
    # 它通常会包含：
    # - 用户原始输入
    # - Agent 的输出
    # - 工具调用及工具结果等必要上下文
    history = result1.to_input_list()

    print("=== 审查 to_input_list() 的内容 ===")

    # 把每一项打印出来，观察它到底保存了什么。
    for i, item in enumerate(history):
        print(f"[{i}] | 内容: {item}...")

    print("\n=== 第二轮：基于历史继续追问 ===")

    # 手动模拟多轮对话：
    # 把上一轮整理好的 history 作为前文，
    # 再拼接一条新的用户输入。
    new_input = history + [
        {"role": "user", "content": "那这种天气适合去跑步吗？"}
    ]

    result2 = await Runner.run(agent, new_input)
    print(f"Agent回复: {result2.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
