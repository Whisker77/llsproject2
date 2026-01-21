from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnableBranch

# 1. 初始化组件
llm = OllamaLLM(model="qwen3:0.6b")
output_parser = StrOutputParser()


# 2. 定义条件判断函数
def route_function(input_dict):
    """根据文本长度决定处理路径"""
    text = input_dict["text"]
    if len(text) > 100:
        return "long"
    else:
        return "short"


# 3. 构建处理链
# 长文本处理链：摘要
long_chain = (
        ChatPromptTemplate.from_template("请为以下长文本生成一个简洁的摘要：\n\n{text}")
        | llm
        | output_parser
)

# 短文本处理链：分析
short_chain = (
        ChatPromptTemplate.from_template("请直接分析以下短文本的核心信息：\n\n{text}")
        | llm
        | output_parser
)

# 4. 修复：添加默认分支
route_branch = RunnableBranch(
    (lambda x: x["key"] == "long", long_chain),  # 条件1：长文本
    (lambda x: x["key"] == "short", short_chain),  # 条件2：短文本
    short_chain  # 默认分支（必须提供）
)

# 5. 组合完整流程
full_chain = (
        RunnableParallel(text=RunnableLambda(lambda x: x))  # 创建初始输入字典
        | {
            "key": RunnableLambda(route_function),  # 添加路由键
            "text": RunnableLambda(lambda x: x["text"])  # 保留原始文本
        }
        | route_branch  # 路由到相应链
)

# 6. 测试
if __name__ == "__main__":
    # 测试短文本
    print("=== 测试短文本 ===")
    short_text = "今天天气很好，适合户外运动。"
    short_result = full_chain.invoke(short_text)
    print(f"输入: {short_text}")
    print(f"输出: {short_result}")
    print()

    # 测试长文本
    print("=== 测试长文本 ===")
    long_text = """
    人工智能是计算机科学的一个分支，旨在创造能够执行通常需要人类智能的任务的机器。
    这些任务包括学习、推理、问题解决、感知和语言理解。AI技术已经广泛应用于各个领域，
    从医疗诊断到自动驾驶汽车，从语音助手到推荐系统。机器学习是人工智能的一个子集，
    它使计算机能够在没有明确编程的情况下学习。深度学习又是机器学习的一个子集，
    使用具有多个层次的神经网络。这些网络可以学习数据的层次化表示，在图像识别、
    自然语言处理等领域取得了突破性进展。
    """
    long_result = full_chain.invoke(long_text)
    print(f"输入长度: {len(long_text)} 字符")
print(f"输出: {long_result}")