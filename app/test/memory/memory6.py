from langchain.memory import ConversationSummaryMemory, ChatMessageHistory
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os
# 加载环境变量
load_dotenv()
# 配置 DeepSeek 模型
llm = ChatOpenAI(
  model='deepseek-chat',
  openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
  openai_api_base=os.getenv("BASE_URL"),
  streaming=True,
  temperature=0.7
)
# 2.定义ConversationSummaryMemory对象
memory = ConversationSummaryMemory(llm=llm)
# 3.存储消息
memory.save_context({"input": "你好"}, {"output": "怎么了"})
memory.save_context({"input": "你是谁"}, {"output": "我是AI助手小智"})
memory.save_context({"input": "初次对话，你能介绍一下你自己吗？"}, {"output": "当然可以了。我是一个无所不能的小智。"})
# 4.读取消息（总结后的）
print(memory.load_memory_variables({}))
# 场景2： 如果实例化ConversationSummaryMemory前，已经有历史消息，可以调用from_messages()实例化
# 1.导入相关包
from langchain.memory import ConversationSummaryMemory, ChatMessageHistory
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os
# 加载环境变量
load_dotenv()
# 配置 DeepSeek 模型
llm = ChatOpenAI(
  model='deepseek-chat',
  openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
  openai_api_base=os.getenv("BASE_URL"),
  streaming=True,
  temperature=0.7
)
# 2.假设原始消息
history = ChatMessageHistory()
history.add_user_message("你好，你是谁？")
history.add_ai_message("我是AI助手小智")
# 3.初始化ConversationSummaryMemory实例
memory = ConversationSummaryMemory.from_messages(
  llm=llm,
  # 是生成摘要的原材料 保留完整对话供必要时回溯。当新增对话时，LLM需要结合原始历史生成新摘要
  chat_memory=history
)
# 4.查看当前记忆中包括了对历史的摘要
print(memory.load_memory_variables({}))
# 5. 增加新的信息
memory.save_context({"input": "我的名字叫做小明"}, {"output": "很高兴认识你"})
print(memory.load_memory_variables({}))
print(memory.chat_memory.messages)