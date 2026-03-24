"""
示例 3：使用 `final_output_as()` 把最终输出显式转换成指定类型。

这个例子把三件事串起来了：

1. Agent 必须先调用工具
2. 工具返回的是字符串形式的原始数据
3. Agent 再把这些数据整理成结构化对象

你要重点理解：

- `result.final_output` 通常已经是最终输出
- `result.final_output_as(Person)` 则是要求 SDK 以你指定的类型来读取它

这在你特别想“显式确认类型”时很有用。
"""

import asyncio

from openai import AsyncOpenAI
from pydantic import BaseModel

from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    set_tracing_disabled,
)


# 这里使用的是一个代理接口地址。
# 为了保持示例逻辑不变，本次只补注释，不调整调用配置。
BASE_URL = "https://api.openai-proxy.org/v1"
API_KEY = "sk-3fNNVrOHy9YbLm87IQZdCe9VZDI9rA5CcCRfe9Nw2w9yyEAT"
MODEL_NAME = "gpt-5-nano"


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)


# 定义我们最终希望得到的结构化结果。
class Person(BaseModel):
    name: str
    age: int
    source: str  # 增加一个字段，用于说明数据来源


# 定义一个模拟数据库查询工具。
#
# 注意：
# 工具返回的是字符串，而不是 `Person` 对象。
# 这正好说明 Agent 的职责之一就是：
# “把外部工具的原始返回，整理成我们真正想要的最终结构。”
@function_tool
def query_database(user_id: int) -> str:
    """
    根据用户 ID 查询数据库中的详细信息。
    """

    print(f"\n[模拟数据库] 正在查询 ID: {user_id} ...")
    if user_id == 8888:
        return "DB_RESULT: Found user. Name: 王五. Age: 42. Region: CN-East."
    return "DB_RESULT: User not found."


async def main():
    """
    演示：
    工具返回原始文本，Agent 再输出结构化对象，
    最后通过 `final_output_as()` 以目标类型读取结果。
    """

    agent = Agent(
        name="数据库查询助手",
        # 这段指令非常关键。
        # 它明确告诉 Agent：
        # 先查库，再根据查库结果组织结构化信息。
        instructions=(
            "你是一个用户信息查询助手。"
            "当用户提供ID时，必须先使用工具查询数据库，然后根据查询结果提取结构化信息。"
        ),
        model=OpenAIChatCompletionsModel(
            model=MODEL_NAME,
            openai_client=client,
        ),
        tools=[query_database],
        output_type=Person,
    )

    # 用户输入里只给 ID，不直接给姓名和年龄。
    # 这迫使 Agent 必须调用工具，不能凭空编造结构化信息。
    input_text = "帮我查询ID为8888的用户信息"
    print(f"--- 用户输入: {input_text} ---")

    result = await Runner.run(agent, input_text)

    # 用 `final_output_as(Person)` 显式把最终结果读成 `Person` 类型。
    #
    # 当你特别在意“我要的就是这个类型”时，这个方法很方便。
    person_data = result.final_output_as(Person)

    print("\n--- 1. 查看中间过程 (RunItem) ---")

    # `result.new_items` 可以帮助你观察 Agent 的执行轨迹。
    # 在这个例子里，通常能看到：
    # ToolCall -> ToolOutput -> 最终消息输出
    for i, item in enumerate(result.new_items):
        item_type = type(item).__name__
        content_preview = str(item.raw_item)[:100].replace("\n", " ")
        print(f"步骤 {i + 1} [{item_type}]: {content_preview}...")

    print("\n--- 2. 验证最终结果 (final_output_as) ---")
    print(f"对象类型: {type(person_data)}")
    print(f"姓名: {person_data.name}")
    print(f"年龄: {person_data.age}")
    print(f"来源: {person_data.source}")


if __name__ == "__main__":
    asyncio.run(main())
