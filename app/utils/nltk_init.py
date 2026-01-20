import nltk
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nltk_init")


def init_nltk():
    # 适配容器环境的NLTK数据路径
    nltk_data_path = os.getenv("NLTK_DATA", str(Path.home() / "nltk_data"))
    os.makedirs(nltk_data_path, exist_ok=True)
    if nltk_data_path not in nltk.data.path:
        nltk.data.path.append(nltk_data_path)

    # 下载必需资源（分词、词性标注）
    required_resources = [
        ("averaged_perceptron_tagger", "taggers/averaged_perceptron_tagger"),
        ("punkt", "tokenizers/punkt")
    ]
    for name, path in required_resources:
        try:
            nltk.data.find(path)
            logger.info(f"NLTK资源已存在：{name}")
        except LookupError:
            logger.info(f"下载NLTK资源：{name}")
            nltk.download(name, download_dir=nltk_data_path)

    logger.info("NLTK初始化完成，可用于文本预处理")


if __name__ == "__main__":
    init_nltk()