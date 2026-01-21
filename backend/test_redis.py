# test_redis.py
import redis

# phpstudy 的 redis 默认通常没有密码，端口 6379
# 如果你设了密码，加上 password='你的密码'
r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)

try:
    r.set('test_key', 'Hello PhpStudy!')
    print("连接成功！读取到的值是:", r.get('test_key'))
except Exception as e:
    print("连接失败:", e)