"""
示例 6：通过 `MCPServerSse` 连接 SSE MCP Server。

这和 HTTP 客户端示例很像，但连接方式换成了 SSE。

学习重点：

1. 客户端类不同：`MCPServerSse`
2. 服务端 URL 不同：通常是 `/sse`
3. 连接成功后，使用方式对 Agent 来说几乎一致

这说明 MCP 的重要价值之一就是：
“对 Agent 层屏蔽不同传输协议的细节差异。”
"""

import asyncio

from openai import AsyncOpenAI

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from agents.mcp import MCPServerSse


BASE_URL = "https://api.siliconflow.cn/v1"
API_KEY = "sk-vnxijjgodhcjisacoilnebjzzlqmrwyuluqdxcpwauocgqjm"
MODEL_NAME = "Qwen/Qwen3-32B"


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(True)


async def main():
    """
    连接 SSE MCP Server 并让 Agent 调用其工具。
    """

    print("正在连接 SSE MCP Server...")

    async with MCPServerSse(
        name="My Remote Server",
        params={
            "url": "http://127.0.0.1:8000/sse",
            "timeout": 30,
        },
        cache_tools_list=True,
    ) as server_connection:
        print(f"已通过 SSE 连接到: {server_connection.name}")

        agent = Agent(
            name="Remote Caller",
            instructions="请调用远程工具回答问题。",
            model=OpenAIChatCompletionsModel(
                model=MODEL_NAME,
                openai_client=client,
            ),
            mcp_servers=[server_connection],
        )

        print("\n--- 发送请求 ---")
        result = await Runner.run(agent, "请帮我计算 1024 加 2048 是多少")
        print(f"Agent 回复: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
