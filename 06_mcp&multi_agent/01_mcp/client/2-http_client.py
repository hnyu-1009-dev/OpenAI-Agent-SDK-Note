"""
示例 5：通过 `MCPServerStreamableHttp` 连接远程 HTTP MCP Server。

这个例子演示：
如何让 Agent 通过 HTTP 连接一个远程 MCP 服务。

你需要重点理解两件事：

1. 客户端连接的是 MCP Server，而不是普通 REST API
2. 连接成功后，这个 MCP Server 提供的工具会被 Agent 当作外部可调用能力
"""

import asyncio

from openai import AsyncOpenAI

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from agents.mcp import MCPServerStreamableHttp


BASE_URL = "https://api.siliconflow.cn/v1"
API_KEY = "sk-vnxijjgodhcjisacoilnebjzzlqmrwyuluqdxcpwauocgqjm"
MODEL_NAME = "Qwen/Qwen3-32B"


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(True)


async def main():
    """
    连接远程 HTTP MCP Server 并运行 Agent。
    """

    print("正在连接 MCP Server...")

    # `MCPServerStreamableHttp` 表示通过 streamable HTTP 方式连接 MCP 服务。
    #
    # `url` 一般指向 MCP 服务挂载点，例如 `/mcp`。
    async with MCPServerStreamableHttp(
        name="Remote Server",
        params={
            "url": "http://localhost:8000/mcp",
            "timeout": 30,
        },
        cache_tools_list=True,
    ) as server_connection:
        print(f"已连接到: {server_connection.name}")

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
        result = await Runner.run(agent, "请帮我计算 55 加 66")
        print(f"Agent 回复: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
