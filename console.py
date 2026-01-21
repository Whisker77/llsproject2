# 当日作业
# 1.Prototype与ABC区别在哪？请提供代码示例展现不同的用法。
# 2.文档分片不同策略适用哪些场景，每一种至少举一个例子进行说明。
# 3.Minio封装哪些方法，请提供测试代码完成创建桶、上传文件、获取连接地址。
# 4.用多线程去实现多个文档的切片，并提供运行截图。




# 1
# 继承abc基类定义的类，定义的抽象方法需要用abc.abstractmethod装饰。
# 然后继承这个类的子类必须要全部定义这些被抽象装饰的方法。起到了类的定义结构统一的作用。
# prototype的优势和作用在于能够快速克隆新的对象，克隆得到的对象与原对象有相同的属性和方法。
# 属性和可用方法相同，但是不同的对象用不同的方法参数执行方法能有不同结果。



import abc
import copy


# ======================== 第一部分：ABC（抽象基类）示例 ========================
# ABC 核心：通过抽象方法约束子类必须实现指定接口，保证子类行为统一
class DocumentLoaderBase(abc.ABC):
    """
    抽象基类（ABC）：定义文档加载器的接口规范
    所有子类必须实现 @abstractmethod 装饰的方法，否则实例化时报错
    """
    # 抽象方法：子类必须实现的核心加载方法
    @abc.abstractmethod
    def load(self, file_path: str) -> str:
        """加载文档的核心方法（抽象方法，子类必须实现）"""
        pass

    # 抽象方法：子类必须实现的文件类型获取方法
    @abc.abstractmethod
    def get_supported_type(self) -> str:
        """返回支持的文件类型（抽象方法，子类必须实现）"""
        pass


# 实现ABC的子类1：PDF加载器
class PDFLoader(DocumentLoaderBase):
    """遵循ABC接口规范的PDF加载器子类"""
    def load(self, file_path: str) -> str:
        # 实现抽象方法：PDF文件加载逻辑
        return f"[PDFLoader] 加载文件: {file_path}，解析PDF内容"

    def get_supported_type(self) -> str:
        # 实现抽象方法：返回支持的文件类型
        return ".pdf"


# 实现ABC的子类2：DOCX加载器
class DOCXLoader(DocumentLoaderBase):
    """遵循ABC接口规范的DOCX加载器子类"""
    def load(self, file_path: str) -> str:
        # 实现抽象方法：DOCX文件加载逻辑
        return f"[DOCXLoader] 加载文件: {file_path}，解析DOCX内容"

    def get_supported_type(self) -> str:
        # 实现抽象方法：返回支持的文件类型
        return ".docx"


# ======================== 第二部分：Prototype（原型模式）示例 ========================
# Prototype 核心：通过克隆方法复制已有对象，快速创建新实例，避免重复初始化
class DocumentProcessorPrototype:
    """
    原型模式类：文档处理器原型
    提供克隆方法，可快速创建属性相似的新处理器实例
    """
    def __init__(self, chunk_size: int, chunk_overlap: int, max_workers: int = 4):
        """初始化原型对象的核心属性"""
        self.chunk_size = chunk_size      # 文本分块大小
        self.chunk_overlap = chunk_overlap  # 分块重叠长度
        self.max_workers = max_workers    # 最大线程数

    def clone(self):
        """
        浅克隆方法（基础克隆）
        适用场景：对象属性为不可变类型（int/str等），无嵌套对象
        """
        return copy.copy(self)

    def deep_clone(self):
        """
        深克隆方法（深度克隆）
        适用场景：对象包含嵌套可变对象（如列表/字典），需完全独立复制
        """
        return copy.deepcopy(self)

    def process(self, file_path: str) -> str:
        """处理器核心方法：模拟文档处理逻辑"""
        return (f"[DocumentProcessor] 处理文件: {file_path} | "
                f"分块大小: {self.chunk_size} | 重叠长度: {self.chunk_overlap} | "
                f"线程数: {self.max_workers}")

    def __str__(self):
        """方便打印对象信息"""
        return (f"DocumentProcessor(chunk_size={self.chunk_size}, "
                f"chunk_overlap={self.chunk_overlap}, max_workers={self.max_workers})")


# 2
# RecursiveCharacterTextSplitter,适用于pdf和docx
# CharacterTextSplitter,适用于doc
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader
from app.test.doc2txt_loader import Doc2txtLoader

project_root = Path(__file__).parent
pdf = project_root / 'docs' / "中华人民共和国劳动合同法.pdf"
doc = project_root / 'docs' / "合同法案例.doc"

loader_pdf = PyPDFLoader(pdf)
document_pdf = loader_pdf.load()
split_pdf = RecursiveCharacterTextSplitter(
                    chunk_size=1200,
                    chunk_overlap=150,
                    length_function=len,
                ).split_documents(document_pdf)

loader_doc = Doc2txtLoader(doc)
document_doc = loader_doc.load()
split_doc = CharacterTextSplitter(
                    chunk_size=1200,
                    chunk_overlap=150,
                    length_function=len,
                ).split_documents(document_doc)

# 3.Minio封装哪些方法，请提供测试代码完成创建桶、上传文件、获取连接地址。
from app.utils.minio_client import MinioClient


minio_client = MinioClient(bucket_name='test-bucket')



test_file_path = pdf
try:
    with open(test_file_path, "rb") as f:
        object_name = minio_client.upload_file(
                file_object=f,
                original_name="中华人民共和国劳动合同法.pdf")
        print(f"文件上传成功，存储名称: {object_name}")
except Exception as e:
    print(f"默认桶上传失败: {e}")
from datetime import timedelta
EXPIRES_TIME = timedelta(hours=1)

try:
    custom_presigned_url = minio_client.get_presigned_url_for_bucket(
        object_name=object_name,
        expires_in=EXPIRES_TIME,
    bucket_name='test-bucket')
    print(f"自定义桶预签名URL生成成功（1小时内有效）:")
    print(custom_presigned_url)
except Exception as e:
    print(f"生成自定义桶URL失败: {e}")









