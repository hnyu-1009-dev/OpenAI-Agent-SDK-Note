import asyncio

from openai import AsyncOpenAI

from agents import (
    Agent,
    Runner,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
)

BASE_URL ="https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = "sk-26d57c968c364e7bb14f1fc350d4bff0"
MODEL_NAME = "qwen-plus"

# 1. 创建异步客户端（必须是 AsyncOpenAI！）
client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)
# 2. 全局注册客户端（所有 Agent 都会用它）a
set_default_openai_client(client=client)


set_default_openai_api("chat_completions")   # 必须指定为 chat_completions
set_tracing_disabled(disabled=True)  # 避免因 tracing 导致 401 错误


async def main():
    # 3. 创建 Agent（只需指定 model 名称）
    agent = Agent(
        name="文学专家", # Agent的名字
        instructions="你只会用七言绝句回应", # 给Agent的指令
        model=MODEL_NAME,  # 这里只是字符串
    )
    # 3.运行Aagent
    result = await Runner.run(agent, "给我写一首关于春天的七言绝句") # 运行Agent

    # 4.得到Agent结果
    print(result.final_output)  # 得到Agent结果



if __name__ == '__main__':
    asyncio.run(main())
