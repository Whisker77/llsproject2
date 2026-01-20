import time
import random
import logging
from pymilvus import (
    connections,
    utility,
    db,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    AnnSearchRequest,
    RRFRanker,
    WeightedRanker
)

# --- 配置日志 (提供运行日志接口) ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MilvusHomework")

# 连接 Milvus
try:
    connections.connect("default", host="localhost", port="19530")
    logger.info("成功连接到 Milvus")
except Exception as e:
    logger.error(f"连接失败: {e}")


# ==========================================
# 1. Milvus 切换 default 到新创建的 custom_db
#    (方法封装示例代码)
# ==========================================
def switch_to_custom_db(db_name: str):
    """
    封装方法：检查数据库是否存在，不存在则创建，然后切换。
    """
    try:
        existing_dbs = db.list_database()
        if db_name not in existing_dbs:
            logger.info(f"数据库 {db_name} 不存在，正在创建...")
            db.create_database(db_name)

        db.using_database(db_name)
        logger.info(f"已切换当前数据库为: {db_name}")
    except Exception as e:
        logger.error(f"切换数据库失败: {e}")


# 执行切换
switch_to_custom_db("custom_db")


# ==========================================
# 2. Milvus 相似度匹配示例代码
# ==========================================
def basic_similarity_search_demo():
    logger.info("--- 开始任务 2: 基础相似度匹配 ---")
    # 快速创建一个临时 Collection 用于演示
    dim = 8
    collection_name = "demo_basic_search"
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim)
    ]
    schema = CollectionSchema(fields)
    collection = Collection(collection_name, schema)

    # 插入少量数据
    vectors = [[random.random() for _ in range(dim)] for _ in range(10)]
    collection.insert([vectors])
    collection.create_index("vector", {"index_type": "FLAT", "metric_type": "L2", "params": {}})
    collection.load()

    # 相似度匹配 (Search)
    search_vec = [[random.random() for _ in range(dim)]]
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}} #十个桶
    results = collection.search(search_vec, "vector", search_params, limit=3)

    logger.info(f"基础搜索返回结果数量: {len(results[0])}")  #第一个查询向量的搜索结果
    for hit in results[0]:
        logger.info(f"Hit ID: {hit.id}, Score: {hit.score}")

    # 清理
    utility.drop_collection(collection_name)


# 执行任务2
basic_similarity_search_demo()


# ==========================================
# 3. Milvus 集合混合查询示例代码
#    a) 多分区 (img_part, txt_part), 噪声 -0.06~0.06, mock数据100条
#    b) 多向量值检索, dim=16, 返回20条, RRFRanker (权重0.75, 0.25)
#    c) 衰减排序器 (通过时间过滤模拟)
# ==========================================

def hybrid_search_demo():
    logger.info("--- 开始任务 3: 集合混合查询 (Hybrid Search) ---")

    collection_name = "homework_hybrid_collection"
    dim = 16

    # 1. 定义 Schema (支持多向量以进行混合检索)
    # 假设我们有两个向量字段：image_vector 和 text_vector，以及一个时间戳字段
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="image_vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
        FieldSchema(name="text_vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
        FieldSchema(name="timestamp", dtype=DataType.INT64)  # 用于 c) 时间倒序/过滤
    ]
    schema = CollectionSchema(fields, description="混合检索作业集合")

    # 重建集合
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
    collection = Collection(collection_name, schema)

    # 2. 创建分区 (题目要求 a: img_part, txt_part)
    collection.create_partition("img_part")
    collection.create_partition("txt_part")
    logger.info("已创建分区: img_part, txt_part")

    # 3. Mock 数据 (题目要求: 100条, 噪声 -0.06 到 0.06)
    # 生成 100 条数据
    row_count = 100

    # 生成随机向量，范围在 -0.06 到 0.06 之间
    # random.uniform(a, b) 生成指定范围内的浮点数
    vectors_img = [[random.uniform(-0.06, 0.06) for _ in range(dim)] for _ in range(row_count)]
    vectors_txt = [[random.uniform(-0.06, 0.06) for _ in range(dim)] for _ in range(row_count)]

    # 模拟时间戳 (最近 5 天的时间戳)
    current_time = int(time.time())  #现在时刻的秒数
    timestamps = [current_time - random.randint(0, 5 * 86400) for _ in range(row_count)]

    # 为了演示分区存入，我们将前50条存入 img_part，后50条存入 txt_part
    # 插入 img_part
    collection.insert(
        [vectors_img[:50], vectors_txt[:50], timestamps[:50]],
        partition_name="img_part"
    )
    # 插入 txt_part
    collection.insert(
        [vectors_img[50:], vectors_txt[50:], timestamps[50:]],
        partition_name="txt_part"
    )
    logger.info(f"Mock 数据插入完成，共 {row_count} 条，数据范围 -0.06~0.06")

    # 4. 创建索引
    index_params = {"index_type": "FLAT", "metric_type": "L2", "params": {}}
    collection.create_index("image_vector", index_params)
    collection.create_index("text_vector", index_params)
    collection.load()

    # 5. 构建混合搜索请求 (Hybrid Search)
    # 模拟查询向量 (同样使用 -0.06~0.06 的噪声范围)
    query_vec_img = [[random.uniform(-0.06, 0.06) for _ in range(dim)]]
    query_vec_txt = [[random.uniform(-0.06, 0.06) for _ in range(dim)]]

    # 定义两个 AnnSearchRequest
    # 这里的 expr 用于题目 c) 时间过滤：例如只查最近 3 天的数据
    three_days_ago = current_time - (3 * 86400)
    time_filter_expr = f"timestamp > {three_days_ago}"

    search_param_1 = {
        "data": query_vec_img,
        "anns_field": "image_vector",
        "param": {"metric_type": "L2", "params": {"nprobe": 10}},
        "limit": 20,
        "expr": time_filter_expr  # 加上时间过滤
    }
    req_1 = AnnSearchRequest(**search_param_1)

    search_param_2 = {
        "data": query_vec_txt,
        "anns_field": "text_vector",
        "param": {"metric_type": "L2", "params": {"nprobe": 10}},
        "limit": 20,
        "expr": time_filter_expr  # 加上时间过滤
    }
    req_2 = AnnSearchRequest(**search_param_2)

    # 6. 定义 Ranker (题目要求: RRFRanker)
    ranker = RRFRanker(k=60) #以搜索向量排名来确定分数

    # 如果你想用权重 0.75/0.25，代码应该是:
    # ranker = WeightedRanker(0.75, 0.25)

    logger.info("执行混合检索 (Hybrid Search) 使用 RRFRanker...")

    # 7. 执行混合检索
    # 题目要求 a: 多分区查询 (指定 partition_names)
    res = collection.hybrid_search(
        [req_1, req_2],
        ranker,
        limit=20,  # 题目要求 b: 返回 20 条
        partition_names=["img_part", "txt_part"],  # 跨分区查询
        output_fields=["timestamp"]
    )

    logger.info(f"混合检索返回结果数量: {len(res[0])}")
    for i, hit in enumerate(res[0]):
        # 题目 c) 隐含要求结果可能需要按时间倒序展示，虽然 RRF 已经排好序了，
        # 但我们可以打印时间戳来验证是否在最近3天内
        logger.info(f"Rank: {i + 1}, ID: {hit.id}, Score: {hit.score}, Time: {hit.entity.get('timestamp')}")


# 执行任务3
hybrid_search_demo()