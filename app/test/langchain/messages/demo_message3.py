# from langchain_core.messages import SystemMessage, HumanMessage
# from langchain_openai import ChatOpenAI
# from dotenv import load_dotenv
# import os
#
# # 加载环境变量
# load_dotenv()
#
# # 配置 DeepSeek 模型
# chat = ChatOpenAI(
#    model="deepseek-chat",
#    temperature=0.7,
#    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
#    openai_api_base="https://api.deepseek.com/v1"
# )
#
# # 第一组消息
# sys_message = SystemMessage(
#    content="我是一个人工智能的助手，我的名字叫小智",
# )
# human_message = HumanMessage(content="猫王是一只猫吗？")
# message1 = [sys_message, human_message]
#
# # 第二组消息
# sys_message1 = SystemMessage(
#    content="我可以做很多事情，有需要就找我吧",
# )
# human_message1 = HumanMessage(content="你叫什么名字？")
# message2 = [sys_message1, human_message1]
#
# # 调用 DeepSeek 模型，传入两组消息
# response1 = chat.invoke(message1)
# print("第一组消息回复:", response1.content)
#
# response2 = chat.invoke(message2)
# print("第二组消息回复:", response2.content)
# 多轮对话的封装 - DeepSeek版本
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 配置 DeepSeek 模型
openai = ChatOpenAI(
  model="deepseek-chat",
  temperature=0.7,
  openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
  openai_api_base="https://api.deepseek.com/v1"
)

# 第一组对话
messages1 = [
  SystemMessage(content="你是沃林AI研究院的助手，请根据用户的问题给出回答"),
  HumanMessage(content="我是学员，我叫卢小联"),
  AIMessage(content="欢迎你的到来"),
  HumanMessage(content="我是谁？"),
]

# 第二组对话
messages2 = [
  SystemMessage(content="我是一个人工智能助手，我的名字叫小智"),
  HumanMessage(content="很高兴认识你"),
  AIMessage(content="欢迎你的到来"),
  HumanMessage(content="我是谁？"),
]

# 调用 DeepSeek 模型
print("=== 第一组对话 ===")
res1 = openai.invoke(messages1)
print(res1.content)

print("\n=== 第二组对话 ===")
res2 = openai.invoke(messages2)
print(res2.content)