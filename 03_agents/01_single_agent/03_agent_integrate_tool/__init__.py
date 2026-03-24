"""
这一组示例讲 Agent 与工具的集成。

和前一章直接手写 `tools=[...]` 的 JSON 定义相比，
Agents SDK 提供了更方便的 `@function_tool` 装饰器。

你会学到：

1. 如何把一个普通 Python 函数暴露给 Agent
2. Agent 何时会决定调用工具
3. 工具输出如何影响 Agent 的最终回答
4. 工具结果如何进一步和结构化输出结合使用
"""
