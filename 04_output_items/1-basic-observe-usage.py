"""
示例 1：观察一次 Agent 运行产生的 `new_items`。

这个例子是理解 output items 的入门起点。

你要先建立一个认知：

Agent 一次运行结束后，不只有一个 `final_output`。
在执行过程中，它还可能产生很多“步骤型产物”，例如：

- 工具调用项
- 工具输出项
- 模型消息项

这些内容都会出现在 `result.new_items` 中。

因此：
- `final_output` 更像“最终交付结果”
- `new_items` 更像“本次执行过程的轨迹记录”
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
set_tracing_disabled(disabled=True)


# 定义一个最简单的天气工具。
# 这样在 Agent 运行时，我们就能更容易观察到：
# “工具调用项”与“最终回答”之间的关系。
@function_tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息。
    """

    return f"天气信息: {city} 是晴天"


async def main():
    """
    运行 Agent，并打印本次新增的所有输出项。
    """

    agent = Agent(
        name="天气专家",
        instructions="根据用户输入的问题，调用工具查询天气",
        model=OpenAIChatCompletionsModel(
            model=MODEL_NAME,
            openai_client=client,
        ),
        tools=[get_weather],
    )

    result = await Runner.run(agent, "武汉的天气")

    # `result.new_items` 表示：
    # 本次运行过程中，新产生的所有中间项。
    #
    # 这些项不一定都是最终给用户看的自然语言，
    # 也可能是工具调用、工具结果等内部运行痕迹。
    for i, item in enumerate(result.new_items):
        print(
            f"Agent运行期间产生的步骤: {i}, "
            f"输出项类型: {type(item)}, "
            f"输出项原始对象: {item.raw_item}"
        )

    # 最后再看最终输出。
    print(f"Agent最终输出: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
