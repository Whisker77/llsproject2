from langchain.agents import Tool, AgentExecutor
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.tools.render import render_text_description
from langchain_ollama import OllamaLLM
from langchain.chains import LLMMathChain
from langchain_core.prompts import PromptTemplate

# 初始化组件
llm = OllamaLLM(model="qwen3:0.6b", temperature=0)
math_chain = LLMMathChain.from_llm(llm=llm)

# 定义工具
tools = [
    Tool(
        name="Calculator",
        func=lambda x: math_chain.invoke({"question": x})["text"],
        description="用于数学计算"
    )
]

# 创建ReAct风格的提示模板
template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

prompt = PromptTemplate.from_template(template)

# 创建代理
agent = {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
            "tools": lambda x: render_text_description(tools),
            "tool_names": lambda x: ", ".join([t.name for t in tools]),
        } | prompt | llm | ReActSingleInputOutputParser()

# 创建执行器
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 使用
result = agent_executor.invoke({"input": "计算 9 的平方根是多少？"})
print(result["output"])


from langchain.chains.base import Chain


class CustomClassificationChain(Chain):
    """自定义分类 Chain"""

    @property
    def input_keys(self):
        return ["text", "categories"]

    @property
    def output_keys(self):
        return ["classification"]

    def _call(self, inputs):
        text = inputs["text"]
        categories = inputs["categories"]

        prompt = f"""
        将以下文本分类到提供的类别中：
        文本: {text}
        类别: {', '.join(categories)}

        只返回类别名称：
        """

        response = self.llm(prompt)
        return {"classification": response.strip()}