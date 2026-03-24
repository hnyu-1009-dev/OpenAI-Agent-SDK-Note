"""
示例 1.1：使用经典的 `chat.completions.create` 接口生成普通文本。

这个文件适合你先建立三个基础认知：

1. OpenAI SDK 的“客户端对象”是怎么创建的。
2. 提示词为什么要拆成 `system` 和 `user` 两种角色。
3. 为什么最终结果要从 `response.choices[0].message.content` 里取出。

这是很多旧项目、旧教程里最常见的一种调用方式。
即使现在官方更推荐新的 `responses` 接口，这种写法你依然需要看得懂，
因为维护老代码时经常会遇到它。
"""

import os

from dotenv import load_dotenv
from openai import OpenAI


# `load_dotenv()` 会读取项目根目录中的 `.env` 文件，
# 并把里面的键值对加载到当前进程的环境变量中。
#
# 典型写法例如：
# OPENAI_API_KEY=你的密钥
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_MODEL_NAME=gpt-4.1-mini
#
# 这样做的好处是：
# 1. 避免把敏感信息直接写死在代码里。
# 2. 切换环境时，只改配置，不改代码。
load_dotenv()


# 创建 OpenAI 客户端。
#
# 这里最重要的两个参数是：
# - `api_key`：身份凭证，告诉服务端“你是谁”。
# - `base_url`：请求发往哪个服务地址。
#
# 如果你使用官方 OpenAI 平台，`base_url` 通常指向官方接口地址。
# 如果你使用兼容 OpenAI 协议的第三方平台，也可以在这里替换成第三方地址。
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)


# 发起一次“聊天补全”请求。
#
# `model`：指定要调用的模型名称。
# 不把模型名写死，而是从环境变量读取，方便以后更换模型。
#
# `messages`：这是 chat 接口最核心的输入格式，它是一个“消息列表”。
# 列表中的每一项都包含：
# - `role`：消息角色
# - `content`：消息内容
#
# 常见角色有：
# - `system`：系统指令，决定模型扮演什么角色、遵守什么规则。
# - `user`：用户提问或任务描述。
# - `assistant`：模型历史回复，常用于多轮对话。
response = client.chat.completions.create(
    model=os.getenv("OPENAI_MODEL_NAME"),
    messages=[
        {
            "role": "system",
            "content": "你是一个专业的 Python 开发人员。",
        },
        {
            "role": "user",
            "content": "如何检查 Python 对象是否是类的实例？",
        },
    ],
)


# `response` 是一个较复杂的响应对象，不是最终文本本身。
#
# 为什么要写成 `choices[0].message.content`？
# - `choices`：模型可能返回多个候选答案，因此是一个列表。
# - `[0]`：取第一个候选答案。大多数入门示例都只取第一个。
# - `message`：聊天消息对象。
# - `content`：消息里的文本内容。
#
# 所以这一行的意思是：打印“第一个候选回复中的文本内容”。
print(response.choices[0].message.content)
