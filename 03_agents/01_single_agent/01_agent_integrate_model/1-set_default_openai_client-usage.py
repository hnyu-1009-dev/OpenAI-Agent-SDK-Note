"""
示例 1：通过“设置默认 OpenAI 客户端”的方式让 Agent 使用指定模型服务。

这个示例重点在于理解 Agents SDK 的“全局默认配置”机制：

1. 先创建一个 `AsyncOpenAI` 客户端。
2. 再通过 `set_default_openai_client(...)` 把它注册为默认客户端。
3. 通过 `set_default_openai_api(...)` 告诉 SDK 默认走哪一种 OpenAI 兼容接口。
4. 后续 Agent 只需要写模型名，就能复用这套默认配置。

这种方式适合：
- 教学示例
- 小项目
- 只有一个主要模型来源的程序
"""

import asyncio

from openai import AsyncOpenAI

from agents import (
    Agent,
    Runner,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
)


# 这里使用的是一个 OpenAI-compatible 接口地址。
# `compatible-mode` 表示目标平台提供了和 OpenAI SDK 兼容的调用方式。
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 这里直接写死了 API Key，仅适合教学演示。
# 在真实项目中，更推荐改成：
# `os.getenv("AL_BAILIAN_API_KEY")`
# 这样能避免把密钥直接提交到代码仓库中。
API_KEY = "sk-26d57c968c364e7bb14f1fc350d4bff0"

# 要使用的模型名称。
MODEL_NAME = "qwen-plus"


# 创建异步版 OpenAI 客户端。
#
# 为什么使用 `AsyncOpenAI`？
# 因为 Agents SDK 的很多运行方式天然支持异步，
# 尤其当你未来要做并发请求、流式输出、工具调用编排时，异步会更自然。
client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)


# 把这个客户端设置成 Agents SDK 的“默认客户端”。
# 这样后面如果 Agent 只写 `model="qwen-plus"`，
# SDK 也知道应该通过哪个底层客户端去请求模型。
set_default_openai_client(client=client)


# 告诉 SDK：默认使用 `chat_completions` 这套接口协议。
#
# 一些 OpenAI-compatible 平台对 `responses` 接口支持不完整，
# 但通常会兼容 `chat_completions`，所以这里显式指定更稳妥。
set_default_openai_api("chat_completions")


# 关闭 tracing。
#
# tracing 通常用于追踪 Agent 执行链路、调试、可观测性分析。
# 教学入门时先关闭，可以减少额外干扰。
set_tracing_disabled(disabled=True)


async def main():
    """
    创建一个最简单的 Agent，并异步运行它。

    这里你要重点观察：
    - `Agent(...)` 本身只负责定义智能体，不会自动运行
    - 真正执行 Agent 的是 `Runner.run(...)`
    """

    # 创建 Agent。
    #
    # `name`：给 Agent 一个名字，方便日志和调试识别。
    # `instructions`：相当于 Agent 的长期系统提示词，决定它的行为风格。
    # `model`：这里直接传字符串模型名，因为我们已经提前设置了默认客户端。
    agent = Agent(
        name="Assistant",
        instructions="你只会用七言绝句回应",
        model=MODEL_NAME,
    )

    # 运行 Agent。
    #
    # `Runner.run(...)` 是异步函数，所以这里必须 `await`。
    # 输入是：“给我写一首关于春天的七言绝句”
    result = await Runner.run(agent, "给我写一首关于春天的七言绝句")

    # `final_output` 表示本次 Agent 运行后的最终结果。
    print(result.final_output)


# 作为脚本直接执行时，启动异步事件循环并运行 `main()`。
if __name__ == "__main__":
    asyncio.run(main())
