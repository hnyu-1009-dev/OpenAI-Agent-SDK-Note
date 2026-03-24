"""
示例 4：通过 `MCPServerStdio` 连接本地 MCP Server。

这个例子是“Agent 调用本地 MCP 服务”的最小闭环。

执行流程可以概括为：

1. 客户端先启动一个本地 MCP Server 子进程
2. 再通过 stdio 建立 MCP 连接
3. 然后把这个连接对象挂到 Agent 的 `mcp_servers` 中
4. Agent 后续就能把 MCP 服务中的工具当成自己的可调用能力使用

这和前面直接 `tools=[本地函数]` 的差别在于：
这里的工具不是直接定义在 Agent 所在文件里，
而是来自一个独立进程。
"""

import asyncio
from pathlib import Path

from openai import AsyncOpenAI

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from agents.mcp import MCPServerStdio


BASE_URL = "https://api.siliconflow.cn/v1"
API_KEY = "sk-vnxijjgodhcjisacoilnebjzzlqmrwyuluqdxcpwauocgqjm"
MODEL_NAME = "Qwen/Qwen3-32B"


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(True)


async def main():
    """
    启动本地 MCP Server 子进程，并让 Agent 通过它调用工具。
    """

    # 计算服务端脚本的绝对路径。
    # 这样可以避免因为当前工作目录变化导致 subprocess 找不到脚本。
    server_script_path = Path(__file__).parent.parent / "server" / "1-my_server.py"

    # `async with MCPServerStdio(...)` 会：
    # 1. 启动一个子进程
    # 2. 与该进程建立 stdio 协议连接
    # 3. 在退出 with 块时自动关闭连接并回收子进程
    async with MCPServerStdio(
        name="My Local Python Server",
        params={
            "command": "python",
            "args": [str(server_script_path)],
        },
    ) as server_connection:
        print(f"已连接到 MCP Server: {server_connection.name}")

        # 把 MCP 连接对象挂到 Agent 上。
        # 这意味着 Agent 可以把远程 MCP 工具当作自己的工具能力来使用。
        agent = Agent(
            name="Weather Assistant",
            instructions="你可以使用工具查询天气或计算数字。",
            model=OpenAIChatCompletionsModel(
                model=MODEL_NAME,
                openai_client=client,
            ),
            mcp_servers=[server_connection],
        )

        print("--- 第一轮：查天气 ---")
        result1 = await Runner.run(agent, "武汉天气怎么样？")
        print(f"Agent: {result1.final_output}")

        print("\n--- 第二轮：做计算 ---")
        result2 = await Runner.run(agent, "算一下 88 加 99 等于多少")
        print(f"Agent: {result2.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
