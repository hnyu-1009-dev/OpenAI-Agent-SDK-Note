"""
示例 2：使用 streamable HTTP 启动 MCP Server。

和前一个 stdio 示例相比，这次的重点是：
把 MCP 服务暴露为可通过 HTTP 访问的远程服务。

这样做的意义是：

- 服务端和客户端不必运行在同一个本地进程树里
- Agent 可以连接远程 MCP 服务
- 更适合部署到服务器、容器或局域网服务中
"""

from mcp.server.fastmcp import FastMCP


# 创建一个 MCP 服务实例。
mcp = FastMCP("远程计算服务")


@mcp.tool()
def add(a: int, b: int) -> int:
    """
    计算两个数字的和。
    """

    print(f"Server Log: 收到请求 add({a}, {b})")
    return a + b


@mcp.tool()
def echo_message(msg: str) -> str:
    """
    回显消息。

    这个工具经常用于测试服务联通性或延迟。
    """

    return f"服务端收到: {msg}"


# 直接运行时，启动 streamable HTTP 版 MCP 服务。
#
# 你可以把它理解为：
# “把 MCP 协议封装在 HTTP 传输之上”。
#
# 客户端通常会连接到类似 `http://localhost:8000/mcp` 的地址。
if __name__ == "__main__":
    print("HTTP MCP Server 正在启动，监听 http://localhost:8000")
    mcp.run(transport="streamable-http")
