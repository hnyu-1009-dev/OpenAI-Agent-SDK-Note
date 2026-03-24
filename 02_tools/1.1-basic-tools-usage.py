"""
示例 1.1：最基础的工具调用（Function Calling / Tool Calling）用法。

这个文件非常重要，因为它展示了很多 Agent、工作流应用的核心套路：

1. 我们先定义一个“本地 Python 函数”作为工具。
2. 再把这个工具的元信息描述给模型，包括：
   - 工具名称
   - 工具用途
   - 参数结构
3. 模型收到用户问题后，先判断是否应该调用工具。
4. 如果模型决定调用工具，它会返回：
   - 要调用哪个工具
   - 工具参数是什么
5. 你的程序拿到这些参数后，真正执行本地函数。
6. 再把函数结果作为 `tool` 消息发回给模型。
7. 模型基于工具结果生成最终面向用户的回复。

你可以把它理解为：
“模型负责做决策和理解语言，Python 代码负责执行真实动作。”
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI


# 加载环境变量。
#
# 本示例使用的是兼容 OpenAI 协议的第三方平台配置：
# - `AL_BAILIAN_API_KEY`
# - `AL_BAILIAN_BASE_URL`
# - `AL_BAILIAN_MODEL_NAME`
#
# 这样做的目的和前面章节一致：
# 把密钥、地址、模型名从代码中解耦出来，方便切换环境和切换平台。
load_dotenv()


# 创建客户端。
#
# 虽然这里实例化的是 `OpenAI` 客户端，
# 但只要第三方平台兼容 OpenAI 的接口协议，
# 依然可以直接复用同一套 SDK。
client = OpenAI(
    api_key=os.getenv("AL_BAILIAN_API_KEY"),
    base_url=os.getenv("AL_BAILIAN_BASE_URL"),
)


# 定义一个本地工具函数。
#
# 在真实项目里，这里可以替换成：
# - 查询数据库
# - 调用天气 API
# - 查询订单状态
# - 读取本地文件
# - 调用企业内部系统
#
# 本例为了便于学习，没有请求真实天气服务，
# 而是用一个字典模拟“城市 -> 天气信息”的映射关系。
def get_weather(city: str) -> str:
    """
    根据城市名称返回天气描述。

    参数：
    - `city`：城市名，例如“北京”“上海”

    返回值：
    - 字符串类型的天气信息

    为什么这里返回字符串而不是复杂对象？
    因为入门示例要先让你理解工具调用流程本身。
    在很多简单场景中，直接把工具结果作为文本传回模型已经足够。
    """

    weather_data = {
        "北京": "北京：晴天，15-25°C，适宜外出",
        "上海": "上海：多云，18-28°C，微风",
        "广州": "广州：阵雨，22-30°C，记得带伞",
        "深圳": "深圳：晴转多云，23-31°C，湿度较高",
    }

    # `dict.get(key, default)` 的意思是：
    # - 如果 `city` 在字典中存在，就返回对应天气
    # - 如果不存在，就返回默认值
    #
    # 这样可以避免因为找不到键而抛出 KeyError。
    return weather_data.get(city, f"暂无{city}的天气信息")


# 使用最底层、最显式的方式完成工具调用。
#
# 之所以叫“底层 JSON 方式”，是因为我们手动写出了工具的描述结构，
# 而不是借助额外封装自动生成。
#
# 这种写法特别适合教学，因为你可以很清楚地看到：
# 模型到底是如何知道“有哪些工具可用”的。
def chat_with_basic_tools():
    """
    演示一次完整的工具调用闭环。

    返回值：
    - 第一次模型响应对象 `response`

    注意：
    这个函数内部会在检测到工具调用时继续执行第二轮请求，
    最终打印真正面向用户的回答。
    """

    print("=== 1. 底层方式：手动编写工具定义 ===")

    # `messages` 保存的是整个对话上下文。
    #
    # 为什么要用列表？
    # 因为大模型在多轮对话中需要看到前面发生过什么，
    # 所以我们通常会把所有关键消息依次放进同一个消息列表中。
    messages = [
        {
            "role": "system",
            "content": "你是一个天气助手，可以查询天气信息。",
        },
        {
            "role": "user",
            "content": "我想知道北京的天气怎么样？",
        },
    ]

    # 第一次请求发送给模型。
    #
    # 这次请求除了普通的 `messages`，还额外传入了 `tools` 参数。
    # `tools` 的作用是：告诉模型“你现在有哪些工具可以调用”。
    response = client.chat.completions.create(
        model=os.getenv("AL_BAILIAN_MODEL_NAME"),
        messages=messages,
        tools=[
            {
                # `type=function` 表示这是一个函数型工具。
                "type": "function",
                "function": {
                    # 工具名。
                    # 这个名字后续会被模型用于指明“我要调用哪个工具”。
                    "name": "get_weather",

                    # 工具描述。
                    # 这段说明会帮助模型理解这个工具适合在什么情况下使用。
                    "description": "查询指定城市的天气信息",

                    # 参数定义采用 JSON Schema 风格。
                    # 这是工具调用中非常关键的一部分：
                    # 模型不只要知道“有这个工具”，还要知道“这个工具怎么传参”。
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "城市名称，如'北京'、'上海'",
                            },
                        },

                        # `required` 表示调用工具时必须提供 `city` 字段。
                        "required": ["city"],

                        # `additionalProperties=False` 表示不允许出现未声明的额外字段。
                        # 这有助于减少模型胡乱传参的情况。
                        "additionalProperties": False,
                    },
                },
            }
        ],
    )

    # 取出模型第一次响应中的消息对象。
    message = response.choices[0].message

    # 把模型的这条消息也加入上下文中。
    #
    # 为什么要追加？
    # 因为后续第二次请求时，模型需要“记得自己刚才发起过工具调用”。
    messages.append(message)

    # `message.tool_calls` 用来判断：模型这次是否请求调用工具。
    #
    # 如果为空，说明模型直接回答了，不需要走工具流程。
    # 如果非空，说明模型认为需要调用一个或多个工具。
    if message.tool_calls:
        # 理论上一次响应里可以包含多个工具调用，所以这里用 `for` 遍历。
        for tool_call in message.tool_calls:
            # 先判断当前工具调用的目标函数名。
            # 这是一个非常常见的分发写法：
            # 根据 `tool_call.function.name` 决定调用本地哪个 Python 函数。
            if tool_call.function.name == "get_weather":
                # `tool_call.function.arguments` 是一个 JSON 字符串，
                # 例如可能长这样：
                # '{"city":"北京"}'
                #
                # `json.loads(...)` 会把 JSON 字符串转成 Python 字典。
                args = json.loads(tool_call.function.arguments)

                # 真正执行本地工具函数。
                # 这一步不是模型做的，而是你的 Python 程序做的。
                result = get_weather(args["city"])

                # 把工具执行结果作为一条 `tool` 消息追加到上下文中。
                #
                # 这一步是整个工具调用机制里最容易忽略、但最关键的步骤之一：
                # 你必须把工具结果发回模型，模型才能基于真实结果生成最终答案。
                messages.append(
                    {
                        "role": "tool",

                        # `tool_call_id` 必须对应模型刚才发起的那个工具调用 ID。
                        # 这样模型才能知道：这条工具结果是对哪次调用的响应。
                        "tool_call_id": tool_call.id,

                        # 工具执行后的文本结果。
                        "content": result,
                    }
                )

        # 第二次请求：让模型基于工具返回值生成最终自然语言答案。
        #
        # 第一次请求的任务其实是“决定是否调用工具、如何调用工具”。
        # 第二次请求的任务才是“结合工具结果，正式回复用户”。
        second_response = client.chat.completions.create(
            model=os.getenv("AL_BAILIAN_MODEL_NAME"),
            messages=messages,
        )

        print(f"最终回复: {second_response.choices[0].message.content}")

    # 这里返回的是第一次响应对象，方便你调试时观察：
    # - 模型是否触发了工具调用
    # - 工具调用参数长什么样
    return response


# 这段判断的意思是：
# 只有当你直接运行当前文件时，才执行 `chat_with_basic_tools()`。
#
# 如果这个文件被别的模块 `import` 进去，就不会自动执行。
# 这是 Python 示例代码中非常常见、也非常推荐的写法。
if __name__ == "__main__":
    chat_with_basic_tools()
