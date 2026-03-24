"""
这一组示例讲 MCP 客户端。

学习重点：

1. 如何连接本地 stdio MCP Server
2. 如何连接远程 streamable HTTP MCP Server
3. 如何连接 SSE MCP Server
4. 如何把连接成功的 MCP Server 挂到 Agent 的 `mcp_servers` 中

理解这部分后，你会发现：
Agent 不一定只能调用“当前文件里的本地函数”，
它还可以调用“远程 MCP 服务提供的工具”。
"""
