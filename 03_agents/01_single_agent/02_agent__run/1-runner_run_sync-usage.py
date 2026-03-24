"""
示例 1：使用 `Runner.run_sync(...)` 同步执行 Agent。

这是最容易理解的一种运行方式：

1. 创建 Agent
2. 同步调用 `Runner.run_sync(...)`
3. 直接拿到结果并打印

它适合：
- 最基础的脚本
- 命令行演示
- 刚开始学习 Agent SDK 的同学

但它的局限也很明显：
- 不适合高并发服务
- 不适合需要与异步框架深度集成的项目
"""

from openai import AsyncOpenAI

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled


BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = "sk-26d57c968c364e7bb14f1fc350d4bff0"
MODEL_NAME = "qwen-plus"


# 创建异步客户端。
#
# 虽然这里后面调用的是同步版 `run_sync`，
# 但底层模型对象仍然可以由异步客户端来承载。
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)


set_tracing_disabled(disabled=True)


def main():
    """
    用同步方式运行一个 Agent。
    """

    # 创建 Agent。
    agent = Agent(
        name="Assistant",
        instructions="你只会用七言绝句回应。",
        model=OpenAIChatCompletionsModel(
            model=MODEL_NAME,
            openai_client=client,
        ),
    )

    # `Runner.run_sync(...)` 会阻塞当前线程，直到 Agent 完成执行并返回结果。
    #
    # 对初学者来说，这种调用方式最符合普通函数调用的直觉。
    result = Runner.run_sync(agent, "给我写一首关于春天的七言绝句")

    # 打印最终输出。
    print(result.final_output)


if __name__ == "__main__":
    main()
