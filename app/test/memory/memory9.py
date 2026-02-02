from langchain.memory import ConversationKGMemory
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

#2 配置 DeepSeek 模型
llm = ChatOpenAI(
  model='deepseek-chat',
  openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
  openai_api_base=os.getenv("BASE_URL"),
  streaming=True,
  temperature=0.7
)

# 3.定义ConversationKGMemory对象
memory = ConversationKGMemory(llm=llm)

# 4.保存会话
memory.save_context({"input": "向山姆问好"}, {"output": "山姆是谁"})
memory.save_context({"input": "山姆是我的朋友"}, {"output": "好的"})

# 5.查询会话
print(memory.load_memory_variables({"input": "山姆是谁"}))

# 6. 增加新的 会话
result = memory.get_knowledge_triplets("她最喜欢的颜色是红色") #只做知识图谱信息抽取，不存进memory
