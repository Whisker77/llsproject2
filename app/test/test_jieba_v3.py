from langchain_community.embeddings import OllamaEmbeddings  # 修改导入
from langchain.vectorstores import Chroma
from langchain.schema import Document
from test_jieba_v1 import load_and_split_markdown
import jieba

def jieba_tokenize(text: str):
    """使用 Jieba 进行中文分词"""
    return list(jieba.cut(text))


def create_vector_store(documents, embedding_model):
    """创建向量存储"""
    # 处理文档内容（使用 Jieba 分词）
    processed_docs = []
    for doc in documents:
        # 使用 Jieba 分词处理文本
        tokens = jieba_tokenize(doc.page_content)
        processed_text = " ".join(tokens)  # 用空格连接分词结果
        processed_docs.append(Document(page_content=processed_text, metadata=doc.metadata))

    # 创建向量存储
    vectorstore = Chroma.from_documents(processed_docs, embedding_model)
    return vectorstore


# 使用示例 - 修改为使用 OllamaEmbeddings
# 首先确保你已安装并运行了 Ollama，并且下载了合适的嵌入模型
embedding_model = OllamaEmbeddings(
    model="bge-m3:latest",  # 或者使用其他支持的嵌入模型，如 "all-minilm"
    base_url="http://localhost:11434"  # Ollama 服务的地址，默认是 localhost:11434
)
markdown_file = "nrs2002_full.md"  # 替换为你的 Markdown 文件路径
documents = load_and_split_markdown(markdown_file)
# 假设 documents 是从 Markdown 文件加载的文档列表
vectorstore = create_vector_store(documents, embedding_model)