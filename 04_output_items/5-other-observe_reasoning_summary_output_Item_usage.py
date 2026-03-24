"""
示例 7：观察推理摘要项 `ReasoningItem`。

这是本目录里最容易“因模型不同而表现不同”的示例。

你要先理解一个现实情况：

不是所有模型都会显式返回 reasoning item。

有些模型：
- 内部会推理，但不把推理内容单独暴露出来

有些模型：
- 会把推理摘要或 reasoning 内容作为独立 item 返回

所以这份代码更适合用来学习“如何检测 reasoning item”，
而不是保证每次都一定能看到它。
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
from agents.items import ReasoningItem


# --- 配置部分 ---
BASE_URL = "https://api.siliconflow.cn/v1"
API_KEY = "sk-vnxijjgodhcjisacoilnebjzzlqmrwyuluqdxcpwauocgqjm"

# 如果你想更稳定地测试 ReasoningItem，通常更适合尝试更偏推理型的模型。
# 这里保留原始配置，不改动运行逻辑。
# MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
MODEL_NAME = "Qwen/Qwen3-32B"

# 也可以切换到其他代理接口模型：
# BASE_URL = "https://api.openai-proxy.org/v1"
# API_KEY = "sk-3fNNVrOHy9YbLm87IQZdCe9VZDI9rA5CcCRfe9Nw2w9yyEAT"
# MODEL_NAME = "gpt-5"


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)


@function_tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息，包含具体数值。

    这里故意返回一个可参与数学计算的温度，
    方便后续让模型执行“工具 + 推理”的组合任务。
    """

    return f"数据源返回: {city}的气温是 24 摄氏度"


async def main():
    """
    运行一个需要“先查天气，再做数学推理”的任务，
    观察是否会产生 `ReasoningItem`。
    """

    agent = Agent(
        name="数学与天气专家",
        instructions="你是一个逻辑严密的数学家，同时也是气象专家。",
        model=OpenAIChatCompletionsModel(
            model=MODEL_NAME,
            openai_client=client,
        ),
        tools=[get_weather],
    )

    # 这个任务同时包含：
    # - 工具调用：先获取温度
    # - 逻辑推理：判断是否为质数，并计算与最近质数的差值
    complex_task = (
        "帮我查一下武汉的气温，然后告诉我这个数字是不是质数？"
        "如果不是，它离最近的质数相差多少？"
    )

    print(f"--- 任务: {complex_task} ---")
    result = await Runner.run(agent, complex_task)

    for item in result.new_items:
        # 专门捕获 `ReasoningItem`
        if isinstance(item, ReasoningItem):
            # 不同厂商返回的原始结构可能不完全一致，
            # 所以这里一方面打印原始对象，一方面再尝试读取常见字段。
            print("\n模型回答【原始事件】:", item.raw_item)

            # 一些实现会把推理摘要放在 `summary` 中。
            # 本示例沿用原写法，直接读取第一段摘要文本。
            print("\n思考完整内容:", item.raw_item.summary[0].text)

    print(f"\n--- Agent最终输出 ---\n{result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
