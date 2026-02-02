import redis
r = redis.Redis(host='localhost',port=16379,db=0)
r.set('test_key', 'Hello Redis')
print("Redis连接成功，取值结果:", r.get('test_key').decode('utf-8'))

# 设置普通键值
r.set("username", "alice")
print(r.get("username"))  # 输出：alice

# 设置带过期时间的键（10秒后过期）
r.setex("temp_token", 10, "abc123")

# 计数器
r.set("page_views", 0)
r.incr("page_views")  # 1
r.incr("page_views", 5)  # 6（一次加5）
print(r.get("page_views"))  # 6

# 存储用户信息
r.hset("user:100", mapping={
    "name": "bob",
    "age": "25", #hash是键值对集合
    "email": "bob@example.com"
})
# 获取单个字段
print(r.hget("user:100", "name"))  # bob
# 获取所有字段
print(r.hgetall("user:100"))  # {'name': 'bob', 'age': '25', 'email': 'bob@example.com'}
# 字段自增（积分增加5）
r.hincrby("user:100", "points", 5)
print(r.hget("user:100", "points"))  # 5

# 左侧添加元素（栈：后进先出）
r.lpush("stack", "a")
r.lpush("stack", "b")  # 此时列表：[b, a]

# 右侧添加元素（队列：先进先出）
r.rpush("queue", "job1")
r.rpush("queue", "job2")  # 此时列表：[job1, job2]

# 获取列表所有元素
print(r.lrange("stack", 0, -1))  # ['b', 'a']
print(r.lrange("queue", 0, -1))  # ['job1', 'job2']

# 移除元素
print(r.lpop("stack"))  # b（栈顶弹出）
print(r.rpop("queue"))  # job2（队尾弹出）

# 添加元素（自动去重）
r.sadd("user:100:follow", "user200", "user300", "user200")  # 实际添加2个元素

# 查看集合元素
print(r.smembers("user:100:follow"))  # {'user200', 'user300'}

# 判断元素是否存在
print(r.sismember("user:100:follow", "user200"))  # True

# 计算共同关注（交集）
r.sadd("user:200:follow", "user300", "user400")
common = r.sinter("user:100:follow", "user:200:follow")
print(common)  # {'user300'}（两人共同关注的用户）

# 添加排行榜数据（用户：分数）
r.zadd("game_ranking", {  #z是sorted 有序的数据
    "player1": 300,
    "player2": 500,
    "player3": 400
})

# 降序取前2名（带分数）
top2 = r.zrevrange("game_ranking", 0, 1, withscores=True) #取第0名和第1名
print(top2)  # [('player2', 500.0), ('player3', 400.0)]

# 给player1增加100分
r.zincrby("game_ranking", 100, "player1")  # 300 → 400

# 查看player1的排名（升序，即从低到高）
print(r.zrank("game_ranking", "player1"))  # 1（此时分数400，排名第2，索引1）

# 检查键是否存在
print(r.exists("username"))  # 1（存在）

# 设置键过期时间
r.set("session", "xyz")
r.expire("session", 1800)  # 30分钟后过期
print(r.ttl("session"))  # 1800（剩余秒数） #time to live

# 删除键
delete_count = r.delete("session", "temp_key")
print(f"删除了 {delete_count} 个键")
