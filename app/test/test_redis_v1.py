import redis
import threading
from typing import Optional


class RedisPoolManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock: #同一时间，只允许一个线程进入下面的代码
            if cls._instance is None:
                cls._instance = super().__new__(cls) #object().__new__(cls)
                            #返回一个“已经分配好内存、但还没初始化”的 cls 类型(RedisPoolManager)实例对象
                cls._instance._init_pool()
        return cls._instance

    def _init_pool(self):
        """初始化连接池"""
        self.pool = redis.ConnectionPool(
            host='localhost',
            port=16379,
            # password='your_password',
            db=0,
            max_connections=20,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
            decode_responses=True
        )

    def get_connection(self) -> redis.Redis:
        """获取Redis连接"""
        return redis.Redis(connection_pool=self.pool)

    def close_pool(self):
        """关闭连接池"""
        self.pool.disconnect()


# 使用示例
def test_redis_pool():
    pool_manager = RedisPoolManager()

    # 多线程测试
    def worker(thread_id):
        r = pool_manager.get_connection() #redis.Redis
        key = f"thread_{thread_id}"
        r.set(key, f"value_from_thread_{thread_id}")
        value = r.get(key)
        print(f"Thread {thread_id}: {value}")

    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,)) #返回一个线程对象
        threads.append(t)
        t.start() #线程的执行顺序是完全随机的 即使start()后，需要os系统决定执行时机

    for t in threads:
        t.join() #主线程等待每一个t子线程执行完毕。


if __name__ == "__main__":
    test_redis_pool()