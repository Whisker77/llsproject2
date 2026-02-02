from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os

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
# 1. 设置API密钥
os.environ["TAVILY_API_KEY"] = "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"

# 2. 初始化搜索工具
search = TavilySearchResults(max_results=3)

# 3. 创建Tool的实例，这里的name是工具名称，description是工具的描述，func是工具的函数
search_tool = Tool(
  name="Search",
  description="用于从互联网搜索信息",
  func=search.run,
)

# 4. 初始化大模型
# 使用前面初始化好的 chat

# 5. 创建AgentExecutor
agent_executor = initialize_agent(
  tools=[search_tool],
  llm=chat,
  agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, #react模式的agent有内置方法提出tool需要的参数
  verbose=True,
)

# 6. 测试查询
query = "今天深圳的天气怎么样？"
result = agent_executor.run(query)
print(result)