"""
示例 1：把一个最基础的函数工具接入 Agent。

这个例子是“Agent 调工具”的最小闭环版本：

1. 用 `@function_tool` 标记一个 Python 函数
2. 在 `Agent(..., tools=[...])` 中注册该工具
3. 给 Agent 一条用户消息
4. Agent 判断是否需要调用工具
5. 工具执行结果参与最终回答生成

对比前面手动写 JSON Schema 的工具调用方式：

- 前面是“底层写法”，更能看到协议细节
- 这里是“SDK 封装写法”，更适合日常开发
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


BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = "sk-26d57c968c364e7bb14f1fc350d4bff0"
MODEL_NAME = "qwen-plus"


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)


# `@function_tool` 的作用是把一个普通 Python 函数包装成 Agent 可调用的工具。
#
# SDK 会基于函数名、参数、文档字符串等信息，
# 自动生成工具描述，减少我们手写 JSON Schema 的工作量。
@function_tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息。

    这里为了教学简单，只返回一个模拟结果。
    在真实项目中，你可以把这里替换成真实天气 API 请求。
    """

    return f"天气信息: {city} 是晴天"


async def main():
    """
    创建带工具的 Agent，并演示一次工具调用。
    """

    # 创建 Agent。
    #
    # `tools=[get_weather]` 表示把这个函数工具注册给 Agent。
    # 后续当 Agent 认为“需要查询天气”时，就有机会调用它。
    agent = Agent(
        name="天气助手",
        instructions="你是一个天气助手，你只能回答关于天气的问题。",
        model=OpenAIChatCompletionsModel(
            model=MODEL_NAME,
            openai_client=client,
        ),
        tools=[get_weather],
    )

    # 运行 Agent。
    #
    # 用户问“武汉的天气”，这会触发 Agent 判断是否调用 `get_weather`。
    result = await Runner.run(agent, "武汉的天气")

    # 输出最终结果。
    # 注意：这里打印的是 Agent 整合工具结果后的最终回答，
    # 而不是工具函数的原始返回值本身。
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
