"""
示例 6：观察工具结果项 `ToolCallOutputItem`。

和上一份文件不同，这次关注的不是“调用请求”，
而是“工具已经执行完之后的结果”。

因此这里要重点区分：

1. `ToolCallItem`
   模型请求调用工具
2. `ToolCallOutputItem`
   工具执行完成后的输出

在调试 Agent 时，这类 item 非常有价值，
因为它能帮助你判断问题到底出在：
- 模型没正确选工具
- 还是工具本身返回了不符合预期的结果
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
from agents.items import ToolCallOutputItem


# qwen3-max 模型
# BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
# API_KEY = "sk-26d57c968c364e7bb14f1fc350d4bff0"
# MODEL_NAME = "qwen3-max"

# Qwen/Qwen3-32B 模型
BASE_URL = "https://api.siliconflow.cn/v1"
API_KEY = "sk-vnxijjgodhcjisacoilnebjzzlqmrwyuluqdxcpwauocgqjm"
MODEL_NAME = "Qwen/Qwen3-32B"

# gpt-5 系列模型
# BASE_URL = "https://api.openai-proxy.org/v1"
# API_KEY = "sk-3fNNVrOHy9YbLm87IQZdCe9VZDI9rA5CcCRfe9Nw2w9yyEAT"
# MODEL_NAME = "gpt-5-nano"


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
    运行 Agent，并专门提取工具输出项。
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
        if isinstance(item, ToolCallOutputItem):
            print("模型回答【原始事件】:", item.raw_item)

            # 一些底层原始结构里，输出值可以从 `raw_item["output"]` 读取。
            print("工具结果(raw_item):", item.raw_item["output"])

            # SDK 也通常提供更方便的属性访问方式。
            print("工具结果(output属性):", item.output)

    print(f"Agent最终输出: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
