"""
示例 3：使用 SSE（Server-Sent Events）启动 MCP Server。

SSE 的核心特点是：
服务端可以持续地向客户端推送事件流。

在 MCP 场景中，这种传输方式适合：
- 持续连接
- 流式结果返回
- 一些更偏实时推送的客户端交互模式

从工具注册角度看，它和前面的 stdio / HTTP 版本没有本质区别，
差异主要在“传输层”。
"""

from mcp.server.fastmcp import FastMCP


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
    """

    return f"服务端收到: {msg}"


# 通过 `transport="sse"` 启动 SSE 版 MCP 服务。
# 对应客户端通常会连接到类似 `http://127.0.0.1:8000/sse` 的地址。
if __name__ == "__main__":
    print("HTTP MCP Server 正在启动，监听 http://localhost:8000")
    mcp.run(transport="sse")
