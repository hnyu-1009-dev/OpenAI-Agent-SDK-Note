"""
示例 2：通过自定义 `ModelProvider` 为 Agent 提供模型。

这个示例的核心价值在于“解耦”：

前一个示例是把默认客户端注册到全局环境里。
这个示例则更进一步，把“如何根据模型名获取模型对象”封装进 `ModelProvider`。

这样做的好处包括：

1. 模型切换逻辑可以集中管理。
2. 可以更方便地做多模型路由。
3. 在大型项目中，Agent 不需要关心底层模型实例怎么创建。

如果你以后要做：
- 不同 Agent 用不同模型
- 根据任务动态选模型
- 企业内部统一封装模型访问层

那么 `ModelProvider` 会是一个非常实用的抽象点。
"""

from __future__ import annotations

import asyncio

from openai import AsyncOpenAI

from agents import (
    Agent,
    Model,
    ModelProvider,
    OpenAIChatCompletionsModel,
    RunConfig,
    Runner,
    set_tracing_disabled,
)


BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = "sk-26d57c968c364e7bb14f1fc350d4bff0"
MODEL_NAME = "qwen-plus"


# 创建异步客户端。
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)


# 关闭 tracing，减少教学示例中的无关输出。
set_tracing_disabled(disabled=True)


# 自定义一个模型提供器。
#
# `ModelProvider` 可以理解为：
# “给我一个模型名，我来告诉你应该返回哪个可执行的模型对象。”
class CustomModelProvider(ModelProvider):
    """
    一个最简自定义模型提供器。

    通过重写 `get_model(...)` 方法，把字符串模型名映射到具体的 `Model` 实例。
    """

    def get_model(self, model_name: str) -> Model:
        """
        根据模型名返回一个模型对象。

        为什么返回的是 `OpenAIChatCompletionsModel`？
        因为当前目标平台更适合走 chat completions 协议。

        也正因为这里已经明确构造了 `OpenAIChatCompletionsModel`，
        所以不需要再额外调用 `set_default_openai_api("chat_completions")`。
        """

        return OpenAIChatCompletionsModel(
            model=model_name,
            openai_client=client,
        )


# 创建一个全局可复用的模型提供器实例。
CUSTOM_MODEL_PROVIDER = CustomModelProvider()


async def main():
    """
    使用自定义 ModelProvider 运行一个 Agent。
    """

    # 这里依然要给 Agent 指定 `model=MODEL_NAME`。
    #
    # 原因是：
    # `ModelProvider` 需要收到一个“模型名”，
    # 才能在 `get_model(model_name)` 中决定返回哪一个模型对象。
    agent = Agent(
        name="Assistant",
        instructions="你只会用七言绝句回应。",
        model=MODEL_NAME,
    )

    # `RunConfig` 是一次运行的配置对象。
    #
    # 这里通过 `run_config=RunConfig(model_provider=...)`
    # 告诉本次运行：模型从这个 provider 中获取。
    result = await Runner.run(
        agent,
        input="给我写一首关于春天的七言绝句",
        run_config=RunConfig(model_provider=CUSTOM_MODEL_PROVIDER),
    )

    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
