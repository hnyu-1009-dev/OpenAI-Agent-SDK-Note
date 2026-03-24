"""
这一组示例讲 MCP 服务端。

你会看到三种常见暴露方式：

1. 本地 stdio 服务
   适合本机进程间通信，最容易起步。
2. streamable HTTP 服务
   适合走标准 HTTP 协议的远程调用。
3. SSE 服务
   适合通过 Server-Sent Events 做流式服务端推送。

它们的共同点都是：
把 Python 函数注册成 MCP 工具，供客户端或 Agent 远程调用。
"""
