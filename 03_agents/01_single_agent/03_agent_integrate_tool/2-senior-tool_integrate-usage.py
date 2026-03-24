"""
示例 2：工具调用与结构化输出结合使用。

这是一个非常有实战价值的模式：

1. Agent 通过工具拿到外部信息
2. 最终结果不再只是一段自然语言字符串
3. 而是被约束为一个 `Pydantic` 数据模型

这样做的意义是：

- 对用户：仍然可以获得清晰答案
- 对程序：拿到的是结构化对象，更适合后续工作流处理

例如你以后可以把这种结果直接用于：
- 存数据库
- 返回前端 API
- 交给下一个 Agent
- 触发自动化流程
"""

import asyncio
import json

from openai import AsyncOpenAI
from pydantic import BaseModel

from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    set_tracing_disabled,
)


BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = "sk-26d57c968c364e7bb14f1fc350d4bff0"
MODEL_NAME = "qwen-plus"


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)


# 定义最终输出的数据结构。
#
# 这表示：我们希望 Agent 的最终结果不是任意文本，
# 而是一个明确包含这些字段的对象。
class WeatherResult(BaseModel):
    city: str
    condition: str
    source: str
    message: str


@function_tool
def get_weather(city: str) -> str:
    """
    模拟天气工具，并以 JSON 字符串形式返回结构化信息。

    为什么工具返回 JSON 字符串？
    因为工具调用结果在很多模型工作流里首先会以文本形式传回模型。
    返回 JSON 可以让这个文本具有稳定结构，更便于模型继续整理成最终输出。
    """

    return json.dumps(
        {
            "city": city,
            "condition": "晴",
            "source": "tool",
            "message": f"{city}天气晴朗",
        },
        ensure_ascii=False,
    )


async def main():
    """
    运行一个带工具、并要求结构化输出的 Agent。
    """

    # 这里的关键点在于 `output_type=WeatherResult`。
    #
    # 这意味着 Agent 最终输出会尽量被整理成 `WeatherResult` 结构，
    # 而不是任意字符串。
    agent = Agent(
        name="天气助手",
        instructions=(
            "你是天气助手，只回答天气问题。"
            "当用户问天气时必须调用 get_weather。"
        ),
        model=OpenAIChatCompletionsModel(
            model=MODEL_NAME,
            openai_client=client,
        ),
        tools=[get_weather],
        output_type=WeatherResult,
    )

    result = await Runner.run(agent, "武汉的天气")

    # 这里的 `final_output` 不再只是字符串，
    # 而是 `WeatherResult` 类型的对象。
    print("final_output:", result.final_output)

    # `model_dump()` 是 Pydantic 模型常用方法，
    # 可以把对象转成普通 Python 字典，方便后续 JSON 序列化或接口返回。
    print("as dict:", result.final_output.model_dump())


if __name__ == "__main__":
    asyncio.run(main())
