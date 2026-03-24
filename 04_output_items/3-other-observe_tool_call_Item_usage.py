"""
示例 5：观察工具调用项 `ToolCallItem`。

`ToolCallItem` 代表的是：
模型已经决定要调用某个工具，并给出了工具名和参数。

注意它还不是“工具执行结果”，而只是“调用请求”。

所以你可以把它理解为：

- `ToolCallItem`：我要调用哪个工具、参数是什么
- `ToolCallOutputItem`：这个工具真正执行完后返回了什么
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
from agents.items import ToolCallItem


# 这里默认启用 gpt-5 系列示例配置。
# 你也可以切换到注释掉的其他模型，比较不同平台在工具调用上的表现。

# qwen3-max 模型
# BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
# API_KEY = "sk-26d57c968c364e7bb14f1fc350d4bff0"
# MODEL_NAME = "qwen3-max"

# Qwen/Qwen3-32B 模型
# BASE_URL = "https://api.siliconflow.cn/v1"
# API_KEY = "sk-vnxijjgodhcjisacoilnebjzzlqmrwyuluqdxcpwauocgqjm"
# MODEL_NAME = "Qwen/Qwen3-32B"

# gpt-5 系列模型
BASE_URL = "https://api.openai-proxy.org/v1"
API_KEY = "sk-3fNNVrOHy9YbLm87IQZdCe9VZDI9rA5CcCRfe9Nw2w9yyEAT"
MODEL_NAME = "gpt-5-nano"


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)


@function_tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息。
    """

    return f"天气信息: {city} 是晴天"


async def main():
    """
    运行带工具的 Agent，并专门观察工具调用请求项。
    """

    agent = Agent(
        name="天气助手",
        instructions="你是一个天气助手，你只能回答关于天气的问题。",
        model=OpenAIChatCompletionsModel(
            model=MODEL_NAME,
            openai_client=client,
        ),
        tools=[get_weather],
    )

    result = await Runner.run(agent, "武汉的天气")

    for item in result.new_items:
        print(item)

        # `ToolCallItem` 表示模型已经构造好了工具调用请求。
        if isinstance(item, ToolCallItem):
            print("模型回答【原始事件】:", item.raw_item)
            print("调用工具:", item.raw_item.name)
            print("参数:", item.raw_item.arguments)

    print(f"Agent最终输出: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
