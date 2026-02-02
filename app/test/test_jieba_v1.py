import os
import jieba
import jieba.analyse #切关键词
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import logging
from typing import List

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_jieba(cut_mode='default', user_dict_path=None):
    """
    初始化 Jieba 分词器

    Args:
        cut_mode: 分词模式，可选 'default'(精确模式), 'cut_all'(全模式), 'search'(搜索引擎模式)
        user_dict_path: 自定义词典路径
    """
    # 加载用户词典（如果有）
    if user_dict_path and os.path.exists(user_dict_path):
        jieba.load_userdict(user_dict_path)
        logger.info(f"已加载用户词典: {user_dict_path}")

    # 设置不同的分词模式
    if cut_mode == 'cut_all':
        jieba.cut_for_search = False  # 确保不是搜索引擎模式
        jieba.cut_all = True  # 全模式
    elif cut_mode == 'search':
        jieba.cut_all = False  # 确保不是全模式
        jieba.cut_for_search = True  # 搜索引擎模式
    else:
        jieba.cut_all = False  # 默认精确模式
        jieba.cut_for_search = False

    logger.info(f"Jieba 初始化完成，模式: {cut_mode}")


def jieba_tokenize(text: str) -> List[str]:
    """
    使用 Jieba 进行中文分词

    Args:
        text: 要分词的文本

    Returns:
        分词后的词语列表
    """
    return list(jieba.cut(text)) #jieba.cut返回一个生成器


def load_and_split_markdown(file_path: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[Document]:
    """
    加载并分割 Markdown 文档

    Args:
        file_path: Markdown 文件路径
        chunk_size: 分割块大小
        chunk_overlap: 分割块重叠大小

    Returns:
        分割后的文档列表
    """
    # 加载 Markdown 文档
    loader = UnstructuredMarkdownLoader(file_path)
    documents = loader.load()

    # 创建文本分割器
    text_splitter = RecursiveCharacterTextSplitter( #这个是把document对象切块的
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", "、", " "]
    )

    # 分割文档
    split_docs = text_splitter.split_documents(documents)
    logger.info(f"已将文档分割为 {len(split_docs)} 个块")
    return split_docs #List[Document]


def process_with_jieba(documents: List[Document]) -> List[List[str]]:
    """
    使用 Jieba 处理所有文档块

    Args:
        documents: 文档块列表

    Returns:
        每个文档块的分词结果
    """
    all_tokens = []
    for i, doc in enumerate(documents):
        tokens = jieba_tokenize(doc.page_content) #-> list
        all_tokens.append(tokens)
        logger.info(f"文档块 {i + 1} 分词结果: {tokens[:10]}...")  # 只显示前10个词

    return all_tokens


def extract_keywords_with_jieba(text: str, top_k: int = 10) -> List[str]:
    """
    使用 Jieba 提取关键词

    Args:
        text: 要提取关键词的文本
        top_k: 返回关键词数量

    Returns:
        关键词列表
    """
    # 基于 TF-IDF 算法提取关键词
    keywords_tfidf = jieba.analyse.extract_tags(text, topK=top_k, withWeight=False)

    # 基于 TextRank 算法提取关键词
    keywords_textrank = jieba.analyse.textrank(text, topK=top_k, withWeight=False)

    return keywords_tfidf, keywords_textrank


# 主函数
def main():
    # 初始化 Jieba（尝试不同模式）
    modes = ['default', 'cut_all', 'search']

    for mode in modes:
        print(f"\n=== 使用 {mode} 模式 ===")
        init_jieba(cut_mode=mode)

        # 加载并分割 Markdown 文档
        markdown_file = "nrs2002_full.md"  # 替换为你的 Markdown 文件路径
        documents = load_and_split_markdown(markdown_file)

        # 使用 Jieba 处理文档
        tokens_list = process_with_jieba(documents)

        # 提取关键词（使用第一个文档块作为示例）
        if documents:
            sample_text = documents[0].page_content
            keywords_tfidf, keywords_textrank = extract_keywords_with_jieba(sample_text)
            print(f"TF-IDF 关键词: {keywords_tfidf}")
            print(f"TextRank 关键词: {keywords_textrank}")


if __name__ == "__main__":
    main()
