from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain.chains import SimpleSequentialChain
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv #.env
import os
# 过滤警告
# warnings.filterwarnings("ignore", category=UserWarning, module=".*ChatOpenAI.*")
# 加载环境变量
load_dotenv()
# 配置 DeepSeek 模型
chat = ChatOpenAI(
  model='deepseek-chat',
  openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
  openai_api_base=os.getenv("BASE_URL"),
  streaming=True,
  temperature=0.7
)
# 2. 创建大模型实例
# 3. 定义一个给剧名写大纲的LLMChain
template1 = """你是个剧作家。给定剧本的标题，你的工作就是为这个标题写一个大纲。
Title:{title}
"""
prompt_template1 = PromptTemplate(
  template=template1,
  input_variables=["title"]
)
synopsis_chain = LLMChain(llm=chat, prompt=prompt_template1)
# 4. 定义一个给剧本大纲写一篇评论的LLMChain
template2 ="""你是<<纽约时报>>的剧作家。有了剧本的大纲，你的工作是为剧本写一篇关于这个评论。
剧情大纲：
{synopsis}
"""
prompt_template2 = PromptTemplate(
  template=template2,
  input_variables=["synopsis"]
)
review = LLMChain(llm=chat, prompt=prompt_template2)
# 5. 定义一个完整的链按顺序运行这条链
# verbose=True 打印链的执行过程
overall_chain = SimpleSequentialChain(chains=[synopsis_chain, review], verbose=True)
# 6. 调用完整链顺序执行这两个链
review = overall_chain.run("日落海滩上的悲剧")
print(review)
