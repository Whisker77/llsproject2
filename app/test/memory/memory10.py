import os
from dotenv import load_dotenv
from langchain.memory import VectorStoreRetrieverMemory, ConversationBufferMemory
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings

# 加载环境变量
load_dotenv()

# 1. 配置 DeepSeek 模型
llm = ChatOpenAI(
  model='deepseek-chat',
  openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
  openai_api_base=os.getenv("BASE_URL", "https://api.deepseek.com/v1"),
  temperature=0.7
)

# 2. 初始化对话记忆
conversation_memory = ConversationBufferMemory()

# 3. 添加对话到记忆
conversation_memory.save_context({"input": "我最喜欢的食物是披萨"}, {"output": "很高兴知道"})
conversation_memory.save_context({"input": "我喜欢的运动是跑步"}, {"output": "好的,我知道了"})
conversation_memory.save_context({"input": "我最喜欢的运动是足球"}, {"output": "好的,我知道了"})

# 4. 使用更轻量的本地嵌入模型
try:
  embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
   )

except:
  # 如果上面的模型下载失败，尝试使用更基础的模型
  embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-albert-small-v2"
   )

# 5. 直接从对话记忆构建文本
texts = []
for message in conversation_memory.chat_memory.messages:
  texts.append(message.content)


# 6. 初始化向量数据库
vectorstore = FAISS.from_texts(texts, embeddings_model)

# 7. 定义检索对象
retriever = vectorstore.as_retriever(search_kwargs=dict(k=1))

# 8. 初始化VectorStoreRetrieverMemory
memory = VectorStoreRetrieverMemory(retriever=retriever)

print("记忆检索测试:")
print("查询: 食物")
result1 = memory.load_memory_variables({"prompt": "食物"})  #获取食物相关的记忆
print(f"结果: {result1}")

print("\n查询: 运动")
result2 = memory.load_memory_variables({"prompt": "运动"})
print(f"结果: {result2}")

print("\n查询: 跑步")
result3 = memory.load_memory_variables({"prompt": "跑步"})
print(f"结果: {result3}")