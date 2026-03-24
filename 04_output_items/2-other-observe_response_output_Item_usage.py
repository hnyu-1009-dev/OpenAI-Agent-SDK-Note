"""
示例 4：观察普通消息输出项 `MessageOutputItem`。

在所有 output items 里，最容易理解的一类就是“模型消息输出项”。
它通常代表：

- 模型最终说给用户的话
- 或某一轮中模型创建的一条消息内容

这个文件的目标就是让你区分：

1. `result.final_output`
   更偏向“最终摘要结果”
2. `MessageOutputItem`
   更偏向“运行过程中产生的一条消息项”
"""

import asyncio

from openai import AsyncOpenAI

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from agents.items import MessageOutputItem


# 下面保留了多套模型配置，方便你切换观察不同模型的输出行为。
#
# 一些模型更偏向直接给出最终答案；
# 一些推理模型可能还会额外暴露 reasoning 相关条目。

# qwen3-max 模型
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = "sk-26d57c968c364e7bb14f1fc350d4bff0"
MODEL_NAME = "qwen3-max"

# Qwen/Qwen3-32B 模型
# BASE_URL = "https://api.siliconflow.cn/v1"
# API_KEY = "sk-vnxijjgodhcjisacoilnebjzzlqmrwyuluqdxcpwauocgqjm"
# MODEL_NAME = "Qwen/Qwen3-32B"

# gpt-5 系列模型
# BASE_URL = "https://api.openai-proxy.org/v1"
# API_KEY = "sk-3fNNVrOHy9YbLm87IQZdCe9VZDI9rA5CcCRfe9Nw2w9yyEAT"
# MODEL_NAME = "gpt-5-nano"


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)


async def main():
    """
    运行一个不带工具的简单 Agent，并观察普通消息输出项。
    """

    agent = Agent(
        name="天气助手",
        instructions="你是一个天气助手，你只能回答关于天气的问题。",
        model=OpenAIChatCompletionsModel(
            model=MODEL_NAME,
            openai_client=client,
        ),
    )

    result = await Runner.run(agent, "北京的天气")

    for item in result.new_items:
        print(item)

        # `MessageOutputItem` 表示模型产生了一条消息输出。
        # 这是最接近“普通聊天回复”的一种 item。
        if isinstance(item, MessageOutputItem):
            print("模型回答【原始事件】:", item.raw_item)
            print("模型回答（原始事件内容）:", item.raw_item.content)

    print(f"Agent最终输出: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
