from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser  # 处理LLM输出为纯字符串
from langchain_community.utilities import SQLDatabase  # 数据库工具（v1.0+ 位置）
from langchain.chains.sql_database.query import create_sql_query_chain  # 新版SQL链
from langchain_ollama import OllamaLLM  # Ollama模型集成


class HealthRiskAnalysisChain:#chain1 = HealthR(uri1,llm1) chain2= HealthR(uri2,llm2)
    def __init__(self, db_uri, llm):
        # 1. 初始化数据库连接（支持MySQL、PostgreSQL等，需对应驱动）
        self.db = SQLDatabase.from_uri(db_uri)
        self.llm = llm

        # 2. 新版SQL查询链（生成SQL字符串，不自动执行）
        self.sql_chain = create_sql_query_chain(llm, self.db)

        # 3. 修复：用管道语法替代 LLMChain（消除弃用警告）
        self.analysis_prompt = PromptTemplate(
            input_variables=["query", "sql", "sql_result"],
            template="""
            基于以下信息进行专业健康风险分析，要求结合数据给出具体结论和建议：
            1. 用户问题：{query}
            2. 执行SQL：{sql}
            3. 查询结果：{sql_result}

            分析输出格式：
            - 风险分布：基于数据说明高风险患者的年龄集中区间
            - 潜在问题：结合年龄分布推测可能的健康风险因素
            - 建议：针对该年龄区间提出预防或干预建议
            """
        )
        # 管道链：prompt → llm → 解析为纯字符串（替代LLMChain）
        self.analysis_chain = self.analysis_prompt | self.llm | StrOutputParser()

    def analyze_health_risk(self, natural_language_query):
        # 第一步：生成SQL（新版链返回纯SQL字符串）
        sql_query = self.sql_chain.invoke({"question": natural_language_query})
        print(f"生成的SQL：{sql_query}")  # 调试：查看生成的SQL是否正确

        # 第二步：执行SQL并获取结果（手动执行，更灵活）
        try:
            sql_result = self.db.run(sql_query)
        except Exception as e:
            return {"error": f"SQL执行失败：{str(e)}", "sql_query": sql_query}

        # 第三步：分析结果（管道链直接返回纯字符串，无需取["text"]）
        analysis = self.analysis_chain.invoke({
            "query": natural_language_query,
            "sql": sql_query,
            "sql_result": sql_result
        })

        # 返回结构化结果
        return {
            "sql_query": sql_query,
            "data": sql_result if sql_result else "无匹配数据",
            "analysis": analysis
        }


# 使用示例（修复模型名 + 数据库驱动适配）
if __name__ == "__main__":
    # 1. 修复1：初始化正确的Ollama模型（先执行命令下载）
    # 第一步：查看qwen可用模型：ollama search qwen
    # 第二步：下载模型（示例：下载0.5b轻量版）：ollama pull qwen:0.5b
    llm = OllamaLLM(model="qwen3:0.6b",base_url='http://127.0.0.1:11434')  # 替换为已下载的模型名（如qwen:1.8b）

    # 2. 修复2：数据库连接适配（解决MySQL驱动问题）
    # 方案A：用pymysql驱动（Windows更易安装，需先执行：pip install pymysql）
    db_uri = "mysql+pymysql://root:123456@localhost:3306/test_db"
    # 方案B：用mysqlclient驱动（需先执行：pip install mysqlclient，Windows可能需额外配置）
    # db_uri = "mysql+mysqldb://remote:zh&*DB2021@localhost:3306/test_db"

    # 3. 创建分析链并执行
    try:
        health_chain = HealthRiskAnalysisChain(db_uri=db_uri, llm=llm)
        result = health_chain.analyze_health_risk(
            "查询最近一周（2024-01-01至2024-09-27）高风险患者的年龄分布，按年龄组统计人数"
        )

        # 打印结果
        print("\n=== 健康风险分析结果 ===")
        if "error" in result:
            print(f"错误：{result['error']}")
        else:
            print(f"SQL查询：{result['sql_query']}")
            print(f"原始数据：{result['data']}")
            print(f"分析结论：\n{result['analysis']}")
    except Exception as e:
        print(f"程序运行失败：{str(e)}")