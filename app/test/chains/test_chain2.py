import warnings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
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

# 创建提示词模板
chat_prompt_template = ChatPromptTemplate.from_messages([
("system","你是一位{area}领域具备丰富经验的高端技术人才"),
("human","给我讲一个 {adjective} 笑话")
])
parser = StrOutputParser()

# 创建链
chain = chat_prompt_template | chat | parser

# 调用链
result = chain.invoke({"area": "机器学习", "adjective": "工作中的"})
print(result)