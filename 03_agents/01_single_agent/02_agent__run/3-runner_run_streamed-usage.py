"""
示例 3：使用 `Runner.run_streamed(...)` 流式执行 Agent。

流式执行特别适合以下场景：

1. 聊天界面
   用户希望边生成边看到内容，而不是等全部生成完才显示。
2. 长文本输出
   如果内容较长，流式输出会显著改善交互体验。
3. 实时展示工具调用或推理过程
   在更复杂的 Agent 应用里，你还可以一边监听事件，一边渲染界面状态。

本例重点学习两个知识点：

1. `Runner.run_streamed(...)` 返回的不是最终字符串，而是一个“流式结果对象”。
2. 需要通过 `async for` 遍历 `stream_events()` 才能逐步读取增量输出。
"""

import asyncio

from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled


BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = "sk-26d57c968c364e7bb14f1fc350d4bff0"
MODEL_NAME = "qwen-plus"


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(True)


async def main():
    """
    流式运行 Agent，并实时打印文本增量。
    """

    agent = Agent(
        name="Assistant",
        instructions="你只会用七言绝句回应。",
        model=OpenAIChatCompletionsModel(
            model=MODEL_NAME,
            openai_client=client,
        ),
    )

    # 创建流式运行对象。
    #
    # 这里还没有把所有结果一次性取完，
    # 而是得到一个可被持续监听事件流的结果对象。
    result = Runner.run_streamed(agent, "给我写一首关于春天的七言绝句")

    print("\n===== 实时流式输出开始 =====\n")

    # `stream_events()` 会持续产出各种事件。
    # 因为是异步流，所以必须用 `async for`。
    async for event in result.stream_events():
        # 这里只关心“原始响应事件”中的文本增量。
        if event.type == "raw_response_event":
            # `ResponseTextDeltaEvent` 表示文本的一小段增量。
            if isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta, end="", flush=True)

    print("\n\n===== 流结束 =====")

    # 即使前面已经逐块打印了文本，最终仍然可以从 `final_output` 取到完整结果。
    print("最终完整结果：", result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
