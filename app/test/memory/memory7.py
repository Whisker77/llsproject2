# 1.导入相关的包
from langchain.memory import ConversationSummaryBufferMemory
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()
# 2.定义模型
llm = ChatOpenAI(
  model='deepseek-chat',
  openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
  openai_api_base=os.getenv("BASE_URL"),
  streaming=True,
  temperature=0.7
)
# 3.定义ConversationSummaryBufferMemory对象


memory = ConversationSummaryBufferMemory(
  llm=llm,
  max_token_limit=40, # 控制缓冲区的大小
  return_messages=True
)
# 4.保存消息
memory.save_context({"input": "你好，我的名字叫小明"}, {"output": "很高兴认识你，小明"})
memory.save_context({"input": "李白是哪个朝代的诗人"}, {"output": "李白是唐朝诗人"})
memory.save_context({"input": "唐宋八大家里有苏轼吗？"}, {"output": "有"})
# 5.读取内容
print(memory.load_memory_variables({}))
# 6. 把缓冲区的大小修改成100 ，对比结果
# print(memory.chat_memory.messages)

from langchain.memory import ConversationSummaryBufferMemory
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.llm import LLMChain
# 1、初始化大语言模型
llm = ChatOpenAI(
  model="gpt-4o-mini",
  temperature=0.5,
  max_tokens=500
)

# 2、定义提示模板
prompt = ChatPromptTemplate.from_messages([
   ("system", "你是电商客服助手，用中文友好回复用户问题。保持专业但亲切的语气。"),
  MessagesPlaceholder(variable_name="chat_history"),
   ("human", "{input}")
])
# 3、创建带摘要缓冲的记忆系统
memory = ConversationSummaryBufferMemory(
  llm=llm,
  max_token_limit=400,
  memory_key="chat_history",
  return_messages=True
)
# 4、创建对话链
chain = LLMChain(
  llm=llm,
  prompt=prompt,
  memory=memory,
)
# 5、模拟多轮对话
dialogue = [
   ("你好，我想查询订单12345的状态", None),
   ("这个订单是上周五下的", None),
   ("我现在急着用，能加急处理吗", None),
   ("等等，我可能记错订单号了，应该是12346", None),
   ("对了，你们退货政策是怎样的", None)
]
# 6、执行对话
for user_input, _ in dialogue:
  response = chain.invoke({"input": user_input})
  print(f"用户: {user_input}")
  print(f"客服: {response['text']}\n")
  
# 7、查看当前记忆状态
print("\n=== 当前记忆内容 ===")
print(memory.load_memory_variables({}))