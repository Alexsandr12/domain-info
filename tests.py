import redis


test_conn = redis.Redis()

dname = "reg.ru"
key = 'fff'
val = 'aaa'
key2 = 'ggg'
val2 = 'iii'

"""test_conn.hset(dname, key, val)
test_conn.hset(dname, key2, val2)
"""
test_conn.expire(dname, 10)

print(test_conn.hgetall(dname))
