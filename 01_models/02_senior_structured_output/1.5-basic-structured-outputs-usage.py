"""
示例 1.5（旧接口版）：使用 `chat.completions.parse` 获得结构化输出。

前面的示例里，模型返回的是“普通文本”。
普通文本适合直接给人看，但不一定方便程序继续处理。

例如，当你希望模型输出：
- 人名
- 年龄
- 日期
- 地点

这类结构明确的数据时，最好让模型直接返回一个可解析的数据结构，
而不是让程序再去从自然语言里二次提取。

本例使用：
- `Pydantic` 定义结构
- `chat.completions.parse(...)` 让模型按结构返回结果
"""

import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


# `BaseModel` 是 Pydantic 中最核心的基类。
# 继承它之后，我们就可以用“声明字段”的方式定义一个结构化数据模型。
#
# 这里定义的 `Person` 表示：我们希望模型最终输出一个“人”的结构，
# 其中必须包含：
# - `name`：字符串类型
# - `age`：整数类型
#
# 这比“请你返回一个包含姓名和年龄的 JSON”更可靠，
# 因为 SDK 和 Pydantic 会一起帮助我们做结构约束与解析。
class Person(BaseModel):
    name: str
    age: int


# 加载环境变量。
# 本示例使用的是第三方兼容平台配置。
load_dotenv()


# 创建客户端。
# 这里仍然使用 OpenAI SDK，但目标地址指向兼容 OpenAI 协议的服务。
client = OpenAI(
    api_key=os.getenv("AL_BAILIAN_API_KEY"),
    base_url=os.getenv("AL_BAILIAN_BASE_URL"),
)


# `chat.completions.parse(...)` 与普通的 `create(...)` 最大的区别在于：
# 你可以通过 `response_format=Person` 告诉 SDK：
# “我希望模型输出的结果符合 `Person` 这个结构。”
#
# 输入文本是：`Jane, 54 years old`
# 我们期待模型理解后返回类似：
# {
#   "name": "Jane",
#   "age": 54
# }
response = client.chat.completions.parse(
    model=os.getenv("AL_BAILIAN_MODEL_NAME"),
    messages=[
        {
            "role": "user",
            "content": "Jane, 54 years old",
        }
    ],
    response_format=Person,
)


# 这里打印的是消息中的原始内容。
# 在某些场景下，这个内容看起来可能像 JSON 字符串。
print(response.choices[0].message.content)


# 更值得你记住的知识点是：
# 如果你想拿到“已经被解析成 Pydantic 对象”的结果，
# 通常可以查看 `response.choices[0].message.parsed`。
#
# 也就是说，结构化输出的真正价值不只是“格式更好看”，
# 而是你可以把返回结果当成一个有明确字段的数据对象继续使用。
