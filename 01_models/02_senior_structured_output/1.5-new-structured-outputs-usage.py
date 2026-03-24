"""
示例 1.5（新接口版）：使用 `responses.parse` 获得结构化输出。

这个例子展示的是新版写法，建议和旧版 `chat.completions.parse` 对照学习。

你要重点理解三件事：

1. 我们先用 Pydantic 定义“理想输出结构”。
2. 再把这个结构告诉 SDK，让模型按这个结构组织答案。
3. 最后直接拿到一个已经解析好的 Python 对象，而不是手动处理字符串。

这类能力在实际项目里非常常见，比如：
- 从一句话里提取会议事件
- 从客服对话里提取工单字段
- 从网页内容里提取结构化信息
"""

import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


# 这是我们定义的“日历事件”结构。
#
# 字段说明：
# - `name`：事件名称，例如“science fair”
# - `date`：事件日期或时间描述，例如“Friday”
# - `participants`：参与者列表，例如 ["Alice", "Bob"]
#
# 当模型输出符合这个结构时，后续代码就可以直接访问：
# `event.name`、`event.date`、`event.participants`
# 而不必从一大段自然语言中自己切分和匹配。
class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]


# 读取 OpenAI 官方配置。
load_dotenv()


# 创建客户端。
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)


# `responses.parse(...)` 是新版接口中的结构化输出写法。
#
# 这里和 `responses.create(...)` 的核心区别是：
# - 不再只是要求模型“写一段文字”
# - 而是要求模型“返回一个符合 `CalendarEvent` 结构的数据”
#
# `input` 这里使用的是“消息列表”形式，而不是简单字符串，
# 是因为我们想同时传入：
# - system 指令：告诉模型当前任务是“提取事件信息”
# - user 输入：提供待提取的原始文本
response = client.responses.parse(
    model=os.getenv("OPENAI_MODEL_NAME"),
    input=[
        {
            "role": "system",
            "content": "Extract the event information.",
        },
        {
            "role": "user",
            "content": "Alice and Bob are going to a science fair on Friday.",
        },
    ],
    text_format=CalendarEvent,
)


# `output_parsed` 是本例最关键的输出。
# 它不是普通字符串，而是已经被解析成 `CalendarEvent` 类型的对象。
#
# 这意味着你可以在后续代码中直接这样使用：
# - `response.output_parsed.name`
# - `response.output_parsed.date`
# - `response.output_parsed.participants`
#
# 这就是结构化输出相对于普通文本输出的最大价值：
# “模型回答”可以直接进入程序逻辑，而不是只适合给人阅读。
print(response.output_parsed)
