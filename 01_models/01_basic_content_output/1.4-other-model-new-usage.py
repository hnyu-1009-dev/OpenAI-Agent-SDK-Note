"""
示例 1.4：在第三方兼容平台上使用新版 `responses.create` 接口。

这个文件可以和 `1.2-new-usage.py` 对照着看：

- `1.2` 演示的是“官方 OpenAI 配置 + 新版 responses 接口”
- 本文件演示的是“第三方兼容配置 + 新版 responses 接口”

你会发现，除了环境变量名称不同，核心调用代码几乎一致。
这说明一旦你掌握了 SDK 的统一抽象层，就可以更灵活地切换模型服务商。
"""

import os

from dotenv import load_dotenv
from openai import OpenAI


# 读取 `.env` 配置文件，让下面的 `os.getenv(...)` 可以拿到第三方平台的配置。
load_dotenv()


# 创建客户端。
#
# 注意这里虽然调用的是 `OpenAI(...)` 类，
# 但不代表你只能访问 OpenAI 官方平台。
# 只要目标服务的接口协议兼容，依然可以复用这个客户端。
client = OpenAI(
    api_key=os.getenv("AL_BAILIAN_API_KEY"),
    base_url=os.getenv("AL_BAILIAN_BASE_URL"),
)


# 使用新版 Responses API 生成文本。
#
# 对比旧版 chat 接口：
# - 简单任务时，写法更短。
# - 输出提取更统一。
# - 后续扩展结构化输出、多模态输入时也更自然。
response = client.responses.create(
    model=os.getenv("AL_BAILIAN_MODEL_NAME"),
    input="写一个关于独角兽的睡前小故事",
)


# 直接打印模型生成的最终文本。
# `output_text` 可以理解为“SDK 已经帮你整理好的可读答案”。
print(response.output_text)
