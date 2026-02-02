from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from langchain_ollama import OllamaLLM



def create_marketing_pipeline():
    """创建营销内容生成管道"""

    # 创建Ollama LLM实例（使用新的类名OllamaLLM）
    llm = OllamaLLM(model="qwen3:0.6b")
    # 产品名称生成链
    name_chain = (
            ChatPromptTemplate.from_template("为{product_type}想一个创新的产品名称:") #from_messages的区别？
            | llm
            | StrOutputParser()
    )

    # 营销口号生成链
    slogan_chain = (
            ChatPromptTemplate.from_template("为产品'{product_name}'写一个吸引人的营销口号:")
            | llm
            | StrOutputParser()
    )

    # 组合管道
    pipeline = (
        RunnableParallel({
            "product_name": name_chain,   #产品名称
            "product_type": RunnablePassthrough()  #pipeline的输入
        })
        .assign(
            slogan=lambda x: slogan_chain.invoke({"product_name": x["product_name"]})
        )
    )

    return pipeline  #pipeline的输入和输出都是一个字典


if __name__ == "__main__":
    pipeline = create_marketing_pipeline()
    result = pipeline.invoke({"product_type": "环保水杯"})

    print("=" * 50)
    print("营销内容生成结果:")
    print("=" * 50)
    print(f"产品名称: {result['product_name']}")
    print(f"营销口号: {result['slogan']}")