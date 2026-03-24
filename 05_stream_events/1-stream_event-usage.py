"""
示例 1：系统性观察 `Runner.run_streamed(...)` 产生的流式事件。

这是学习 Agent 流式机制的关键示例。

你需要先建立一个核心认知：

`run_streamed(...)` 不只是“边输出文字边打印”。
它真正提供的是一条“事件流（event stream）”，而文字增量只是事件中的一种。

本例演示了三大类流式事件：

1. `raw_response_event`
   偏底层，关注模型原始输出流，比如文本增量、推理摘要增量。
2. `run_item_stream_event`
   偏结构化执行过程，关注工具调用、工具输出、消息创建、推理项创建等。
3. `agent_updated_stream_event`
   偏 Agent 运行状态变化，尤其适合多 Agent 场景。

如果你把前面章节的知识串起来看，会更容易理解：

- `raw_response_event` 对应“模型正在吐 token / 片段”
- `run_item_stream_event` 对应“Agent 执行轨迹中的结构化节点”
- `agent_updated_stream_event` 对应“当前负责执行的 Agent 发生变化”
"""

import asyncio

from openai import AsyncOpenAI
from openai.types.responses import (
    ResponseReasoningSummaryTextDeltaEvent,
    ResponseTextDeltaEvent,
)

from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    set_tracing_disabled,
)
from agents.items import (
    HandoffOutputItem,
    MessageOutputItem,
    ReasoningItem,
    ToolCallItem,
    ToolCallOutputItem,
)


# 这里保留了多组不同平台 / 模型配置，方便你切换观察不同模型对流式事件的支持差异。
#
# 不同模型在以下方面可能表现不同：
# - 是否支持更完整的文本增量
# - 是否会显式给出 reasoning summary
# - 工具调用事件的细节是否充分
# - 多 Agent 相关事件是否容易触发

# 示例配置 1：SiliconFlow + 推理模型
BASE_URL = "https://api.siliconflow.cn/v1"
API_KEY = "sk-vnxijjgodhcjisacoilnebjzzlqmrwyuluqdxcpwauocgqjm"
# MODEL_NAME = "Qwen/Qwen3-32B"
MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"

# 示例配置 2：DashScope + 通用模型
# BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
# API_KEY = "sk-26d57c968c364e7bb14f1fc350d4bff0"
# MODEL_NAME = "qwen3-max"

# 示例配置 3：代理接口 + GPT 系列
# BASE_URL = "https://api.openai-proxy.org/v1"
# API_KEY = "sk-3fNNVrOHy9YbLm87IQZdCe9VZDI9rA5CcCRfe9Nw2w9yyEAT"
# MODEL_NAME = "gpt-5"


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)


# 关闭 tracing，避免和流式事件输出混在一起，影响学习观察。
set_tracing_disabled(True)


@function_tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息。

    这里使用最简单的模拟结果，目的是让你把注意力集中在“事件流”上，
    而不是分散到真实外部 API 调用上。
    """

    return f"天气信息: {city} 是晴天"


async def main():
    """
    运行一个带工具的流式 Agent，并分类观察所有事件。
    """

    agent = Agent(
        name="天气助手",
        instructions="你是一个天气助手，用户问天气必须调用 get_weather，禁止编造。",
        model=OpenAIChatCompletionsModel(
            model=MODEL_NAME,
            openai_client=client,
        ),
        tools=[get_weather],
    )

    # 关键点：
    # 只有 `Runner.run_streamed(...)` 才会返回一个可迭代的事件流对象。
    #
    # 如果你使用普通的 `Runner.run(...)`，
    # 你最终只能在任务结束后拿到结果，而看不到中间增量事件。
    result = Runner.run_streamed(agent, "武汉的天气怎么样？")

    # `stream_events()` 是一个异步事件流。
    # 所以这里必须使用 `async for` 去持续消费事件。
    async for event in result.stream_events():
        # ------------------------------------------------------------------
        # 1) RawResponsesStreamEvent
        # ------------------------------------------------------------------
        #
        # 这一类最接近“模型底层原始流输出”。
        # 典型用途是：
        # - 搭建聊天窗口的实时字字输出
        # - 单独显示推理摘要
        if event.type == "raw_response_event":
            # 1.1 文本增量事件
            #
            # `ResponseTextDeltaEvent` 表示模型刚刚又吐出了一小段文本。
            # 把这些 delta 按顺序拼起来，就能得到完整回复。
            if isinstance(event.data, ResponseTextDeltaEvent):
                print(
                    "\n[text_delta]",
                    event.data.delta,
                    end="",
                    flush=True,
                )

            # 1.2 推理摘要增量事件
            #
            # 有些推理模型会把“推理摘要”的增量单独暴露出来。
            # 它和普通文本增量不同，更偏向 reasoning 层信息。
            elif isinstance(event.data, ResponseReasoningSummaryTextDeltaEvent):
                print(
                    "\n[reasoning_summary_delta]",
                    event.data.delta,
                    end="",
                    flush=True,
                )

        # ------------------------------------------------------------------
        # 2) RunItemStreamEvent
        # ------------------------------------------------------------------
        #
        # 这一类事件不是底层 token 流，而是更高层的“执行节点事件”。
        # 它非常适合做调试面板、运行轨迹可视化、审计日志等。
        elif event.type == "run_item_stream_event":
            # `name` 用来区分这是哪一种运行节点。
            name = getattr(event, "name")

            # 2.1 工具调用请求
            #
            # 说明：模型已经决定要调用某个工具，并且构造好了参数。
            if name == "tool_called" and isinstance(event.item, ToolCallItem):
                tool_name = event.item.raw_item.name
                tool_args = event.item.raw_item.arguments
                print(f"\n\n调用工具: {tool_name} args={tool_args}")

            # 2.2 工具执行结果
            #
            # 说明：工具已经真正执行完成，并把结果返回给了 Agent 运行管线。
            elif name == "tool_output" and isinstance(event.item, ToolCallOutputItem):
                print(f"\n工具输出: {event.item.output}")

            # 2.3 新建消息输出
            #
            # 一般表示生成了一条新的对话消息，通常是最终面向用户的回复消息之一。
            elif name == "message_output_created" and isinstance(event.item, MessageOutputItem):
                try:
                    msg = event.item.raw_item
                    print(f"\nmessage_output_created: {msg}")
                except Exception:
                    print("\nmessage_output_created")

            # 2.4 新建推理项
            #
            # 这是执行平面里的结构化推理记录。
            # 它和前面的 `raw_response_event` 中 reasoning delta 的区别在于：
            # - delta 更偏“原始流片段”
            # - reasoning item 更偏“结构化执行记录”
            elif name == "reasoning_item_created" and isinstance(event.item, ReasoningItem):
                try:
                    summary = event.item.raw_item.summary
                    if summary:
                        print("\nreasoning_item_created:", summary[0].text[:200], "...")
                    else:
                        print("\nreasoning_item_created (no summary)")
                except Exception:
                    print("\nreasoning_item_created")

            # 2.5 多 Agent 交接
            #
            # 本示例只有单 Agent，通常不会触发。
            # 但保留这段逻辑有助于你提前理解：
            # 在多 Agent 系统里，事件流还能告诉你“谁把任务交给了谁”。
            elif name in ("handoff_occured", "handoff_requested") and isinstance(
                event.item, HandoffOutputItem
            ):
                try:
                    src = event.item.raw_item.source_agent.name
                    tgt = event.item.raw_item.target_agent.name
                    print(f"\n{name}: {src} -> {tgt}")
                except Exception:
                    print(f"\n{name}")

            else:
                # 其他未单独处理的运行节点事件，这里暂时忽略。
                pass

        # ------------------------------------------------------------------
        # 3) AgentUpdatedStreamEvent
        # ------------------------------------------------------------------
        #
        # 这类事件表示：当前执行上下文中的 Agent 发生了更新。
        # 在单 Agent 示例里意义不大；
        # 在多 Agent 协作中非常重要。
        elif event.type == "agent_updated_stream_event":
            print(f"\n\nagent_updated_stream_event: {event.new_agent.name}")

    # 流式事件全部消费完成后，依然可以直接读取完整最终输出。
    print("\n\nfinal_output:", result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
