"""
示例 1.3：使用“兼容 OpenAI 协议的第三方模型服务”完成普通文本生成。

这个例子最重要的学习点不是提示词本身，而是下面这个事实：

很多第三方大模型平台虽然不是 OpenAI 官方，但它们提供了“OpenAI 兼容接口”。
只要它们的请求格式与 OpenAI SDK 兼容，你就仍然可以继续使用同一个 Python SDK，
只需要替换：

- API Key
- Base URL
- 模型名称

这会极大降低你在不同模型平台之间切换的成本。
"""

import os

from dotenv import load_dotenv
from openai import OpenAI


# 加载环境变量配置。
#
# 这个文件里保留了两套思路：
# - 一套是被注释掉的 `SF_*` 配置
# - 一套是当前实际启用的 `AL_BAILIAN_*` 配置
#
# 这样写的教学意义在于：你可以直观看到，切换供应商时，
# 真正变化的通常只是“配置项”，而不是整段业务代码。
load_dotenv()


# 创建客户端。
#
# 这里当前使用的是阿里百炼兼容接口：
# - `AL_BAILIAN_API_KEY`
# - `AL_BAILIAN_BASE_URL`
#
# 如果你未来切换到别的平台，只要那个平台兼容 OpenAI 协议，
# 一般也只需要改这里和下面的模型名。
client = OpenAI(
    # api_key=os.getenv("SF_API_KEY"),
    # base_url=os.getenv("SF_BASE_URL"),
    api_key=os.getenv("AL_BAILIAN_API_KEY"),
    base_url=os.getenv("AL_BAILIAN_BASE_URL"),
)


# 调用旧版 chat completions 接口。
#
# 虽然服务商变了，但调用方式没有变：
# - 还是传 `model`
# - 还是传 `messages`
# - 还是得到一个 `response` 响应对象
#
# 这正是“兼容 OpenAI 协议”带来的好处。
response = client.chat.completions.create(
    # model=os.getenv("SF_MODEL_NAME"),
    model=os.getenv("AL_BAILIAN_MODEL_NAME"),
    messages=[
        {
            "role": "system",
            "content": "你是一个乐于助人的助手。",
        },
        {
            "role": "user",
            "content": "你是谁？",
        },
    ],
)


# 输出第一个候选答案的文本内容。
# 注意：这一行和 OpenAI 官方接口示例几乎完全一致，
# 这恰好说明“兼容层”让 SDK 的使用体验保持统一。
print(response.choices[0].message.content)
