"""import redis


test_conn = redis.Redis()

dname = "reg.ru"
key = "fff"
val = "aaa"
key2 = "ggg"
val2 = "iii"

test_conn.hset(dname, key, val)
test_conn.hset(dname, key2, val2)

test_conn.expire(dname, 10)

print(test_conn.hgetall(dname))"""

import dns.name
import dns.message
import dns.query
import dns.flags
import dns.resolver
from utilits import MyException


"""class MyClass:
    def __init__(self, a):
        self.a = a
        self.a = self.bab()

    def bab(self):
        c = self.a + 1
        return c

    def aba(self):
        b = self.bab()
        return b

zaz = MyClass(1)

print(zaz.bab())"""

a = []

print(not a)
