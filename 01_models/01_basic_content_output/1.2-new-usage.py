"""
示例 1.2：使用新版 `responses.create` 接口生成普通文本。

学习这个文件时，你要重点理解：

1. 新接口 `responses` 是官方当前更推荐的统一入口。
2. 当任务比较简单时，`input` 可以直接传一个字符串。
3. 返回结果可以直接通过 `response.output_text` 读取，使用起来更直观。

如果你正在写新项目，通常更建议优先学习这一种写法。
"""

import os

from dotenv import load_dotenv
from openai import OpenAI


# 从 `.env` 文件加载环境变量。
# 这样本文件就能通过 `os.getenv(...)` 读取 API Key、Base URL、模型名等配置。
load_dotenv()


# 创建 SDK 客户端。
# 这一步只负责“建立调用配置”，并不会真的向模型发送请求。
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)


# 使用新版 Responses API 发起请求。
#
# 与旧版 chat 接口相比，这里有两个非常明显的特点：
# 1. 接口名从 `chat.completions.create(...)` 变成了 `responses.create(...)`。
# 2. 简单场景下直接传 `input="..."` 即可，不一定非要手写消息列表。
#
# 这种设计更统一，也更适合后续扩展到多模态输入、结构化输出等能力。
response = client.responses.create(
    model=os.getenv("OPENAI_MODEL_NAME"),
    input="写一个关于独角兽的睡前小故事",
)


# `output_text` 是 SDK 帮我们整理好的最终纯文本结果。
# 对初学者来说，这比从更深层的响应结构里手动提取内容更容易理解。
print(response.output_text)
