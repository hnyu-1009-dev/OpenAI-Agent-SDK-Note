"""
示例 3：直接把 `Model` 对象传给 Agent。

这是三种模型接入方式里最直观的一种：

1. 自己先创建底层客户端
2. 自己显式创建 `OpenAIChatCompletionsModel`
3. 在 `Agent(...)` 的 `model` 参数里直接传这个模型对象

这种写法的优点是“配置最显式”：
- 看代码的人一眼就知道 Agent 用的是哪个模型实现
- 不依赖全局默认客户端
- 不依赖额外的 ModelProvider 抽象

特别适合：
- 小型项目
- 单个 Agent 原型验证
- 教学演示
"""

import asyncio

from openai import AsyncOpenAI

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled


BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = "sk-26d57c968c364e7bb14f1fc350d4bff0"
MODEL_NAME = "qwen-plus"


# 创建异步客户端。
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)


# 关闭 tracing，方便聚焦最核心的 Agent 行为。
set_tracing_disabled(disabled=True)


async def main():
    """
    直接将模型对象绑定到 Agent 上并执行。
    """

    # 创建 Agent。
    #
    # 注意这里和前两个示例最大的差别：
    # `model=` 不再是字符串，而是一个真正的模型对象。
    agent = Agent(
        name="Assistant",
        instructions="你只会用七言绝句回应。",
        model=OpenAIChatCompletionsModel(
            model=MODEL_NAME,
            openai_client=client,
        ),
    )

    # 运行 Agent。
    result = await Runner.run(agent, "给我写一首关于春天的七言绝句")

    # 获取本次运行的最终输出。
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
