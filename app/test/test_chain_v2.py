from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama import OllamaLLM
from typing import Dict, Any


class ConversationManager:
    """对话管理器"""

    def __init__(self, llm_model="modelscope.cn/unsloth/DeepSeek-R1-Distill-Qwen-1.5B-GGUF:latest", system_message=None):
        self.llm = OllamaLLM(model=llm_model)
        self.store = {}
        self.system_message = system_message or "你是一个友好的AI助手"

        # 创建提示模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_message),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        # 创建链
        self.chain = self.prompt | self.llm

        # 创建带历史的链
        self.conversation = RunnableWithMessageHistory(
            self.chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        ) #这个类是只有调用chat方法才会执行初始化。很离谱

    def get_session_history(self, session_id: str) -> ChatMessageHistory:
        """获取会话历史"""
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]

    def chat(self, message: str, session_id: str = "default") -> str:
        """发送消息并获取回复"""
        config = {"configurable": {"session_id": session_id}}
        response = self.conversation.invoke({"input": message}, config=config)
        return response

    def clear_history(self, session_id: str = "default"):
        """清除特定会话的历史"""
        if session_id in self.store:
            self.store[session_id].clear()

    def get_history(self, session_id: str = "default"):
        """获取会话历史"""
        if session_id in self.store:
            return self.store[session_id].messages
        return []


# 使用示例
def main():
    # 创建对话管理器
    chat_manager = ConversationManager(
        llm_model="modelscope.cn/unsloth/DeepSeek-R1-Distill-Qwen-1.5B-GGUF:latest",
        system_message="你是一个友好的AI助手，乐于提供详细和具体的回答。"
    )

    # 进行对话
    print("开始对话（输入'退出'结束）:")

    while True:
        user_input = input("\n你: ")
        if user_input.lower() in ['退出', 'exit', 'quit']:
            break

        response = chat_manager.chat(user_input, "user_session_1")
        print(f"AI: {response}")


if __name__ == "__main__":
    main()
    chat_manager = ConversationManager(
        llm_model="modelscope.cn/unsloth/DeepSeek-R1-Distill-Qwen-1.5B-GGUF:latest",
        system_message="你是一个友好的AI助手，乐于提供详细和具体的回答。"
    )
    response1 = chat_manager.chat("数学问题", session_id="math_session")
    response2 = chat_manager.chat("历史问题", session_id="history_session")

    history = chat_manager.get_history("user_session_1")
    for msg in history:
        print(f"{msg.type}: {msg.content}")

    chat_manager.clear_history("user_session_1")

    technical_assistant = ConversationManager(
        system_message="你是一个专业的技术专家，提供准确的技术解答"
    )

    creative_writer = ConversationManager(
        system_message="你是一个有创意的作家，帮助用户进行创意写作"
    )

    customer_service = ConversationManager(
        system_message="你是一个专业的客服代表，礼貌耐心地解决用户问题"
    )