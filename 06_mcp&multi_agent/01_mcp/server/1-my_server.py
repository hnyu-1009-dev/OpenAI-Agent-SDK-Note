"""
示例 1：最基础的本地 MCP Server（stdio 模式）。

这是 MCP 学习的起点。

你要先理解：
这里的服务端并不是传统 Web API 服务，
而是一个可以通过 MCP 协议暴露工具能力的独立进程。

默认情况下，`mcp.run()` 会使用 stdio 传输方式，
也就是：
- 客户端通过标准输入把请求发给服务端
- 服务端通过标准输出把响应返回给客户端

这非常适合本地开发和命令行进程间通信。
"""

from mcp.server.fastmcp import FastMCP


# 创建一个 FastMCP 服务实例。
#
# 这里的名字 `"demo-server"` 主要用于标识这个 MCP 服务。
mcp = FastMCP("demo-server")


# `@mcp.tool()` 的作用是：
# 把下面这个 Python 函数注册成一个 MCP 工具。
#
# 注册后，外部 MCP 客户端就可以通过协议调用它，
# 而不需要直接 import 当前 Python 文件。
@mcp.tool()
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息。
    """

    print(f"Server Log: 正在查询 {city} 的天气...")
    return f"{city}的天气是晴天，39℃"


@mcp.tool()
def calculate_sum(a: int, b: int) -> int:
    """
    计算两个数字的和。
    """

    return a + b


# 直接运行当前文件时，启动 MCP Server。
# 不传 transport 时，默认是本地 stdio 模式。
if __name__ == "__main__":
    mcp.run()
