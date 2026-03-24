"""
示例 2：使用 `Runner.run(...)` 异步执行 Agent。

这是更推荐掌握的方式，因为现代 Python 后端、异步任务系统、Agent 工作流，
很多时候都运行在异步环境中。

和 `run_sync` 相比：

- `run_sync`：直接返回结果，写法简单
- `run`：需要 `await`，但更适合并发和复杂流程

如果你以后要把 Agent 接到：
- FastAPI
- 异步 WebSocket
- 多任务协作
- 更复杂的工具链

那么异步写法会更自然。
"""

import asyncio

from openai import AsyncOpenAI

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled


BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = "sk-26d57c968c364e7bb14f1fc350d4bff0"
MODEL_NAME = "qwen-plus"


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)


async def main():
    """
    用异步方式运行 Agent。
    """

    agent = Agent(
        name="Assistant",
        instructions="你只会用七言绝句回应。",
        model=OpenAIChatCompletionsModel(
            model=MODEL_NAME,
            openai_client=client,
        ),
    )

    # 注意这里必须使用 `await`。
    # 因为 `Runner.run(...)` 返回的是一个可等待对象，而不是立即完成的值。
    result = await Runner.run(agent, "给我写一首关于春天的七言绝句")

    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
