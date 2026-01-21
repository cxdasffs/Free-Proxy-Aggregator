import redis
import random

# 使用你刚才测试成功的配置
POOL = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0, decode_responses=True)
REDIS_KEY = 'proxies'

class RedisClient:
    def __init__(self):
        self.db = redis.Redis(connection_pool=POOL)

    def add(self, proxy, score=10):
        """添加代理 (proxy格式: '1.1.1.1:8080')"""
        # zadd 语法: mapping={成员: 分数}
        return self.db.zadd(REDIS_KEY, {proxy: score})

    def all(self):
        """获取所有代理列表"""
        # 返回格式: [('1.1.1.1:80', 100.0), ('2.2.2.2:80', 50.0)]
        return self.db.zrevrange(REDIS_KEY, 0, -1, withscores=True)

    def count(self):
        """获取总数"""
        return self.db.zcard(REDIS_KEY)

    # 后面还可以加 random(), decrease() 等方法，先写这俩够用了