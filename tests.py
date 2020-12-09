import redis


test_conn = redis.Redis()

import mysql.connector

test_conn_db = mysql.connector.connect(
    host="localhost", user="alexandr", password="1", database="mysqltest"
)

print(test_conn_db.ping())

"""dname = "reg.ru"
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

    def bab(self):
        if self.a == 1:
            self.a = 2
        c = self.a + 1
        return c

    def aba(self):
        b = self.a + 1
        return b

zaz = MyClass(1)

print(zaz.bab())
print(zaz.aba())"""

"""import re

a = '1reg.ru'
b = 'xn--p1ai.xn--p1ai'
c = 'dfsdfsdf'

z = re.search(r'^[a-z0-9]{1,1}[a-z0-9-]{,61}[a-z0-9]{1,1}\.{1,1}(ru|(xn--p1ai){1,1})', a)

if re.search(r'^[a-z\d]{1,1}[a-z0-9-]{,61}[a-z0-9]{1,1}\.{1,1}(ru|(xn--p1ai))$', a):
    print('1')
else:
    print('2')"""


"""import redis

a = {"a": [1, 2, 3], "b": [2, 3, 4]}
dname = "reg.ru"


test_conn = redis.Redis()

for key, val in a.items():
    test_conn.hset(dname, str(key), str(val))

b = test_conn.hgetall(dname)
c = {}
for key, val in b.items():
    c[key.decode("utf-8", "replace")] = list(val.decode("utf-8", "replace"))

print(c)

test_conn.setex("rere.ru", 60, "qweqweqwe")
if not test_conn.hgetall("dnamee"):
    print("1")
else:
    print("2")"""

"""def qwe():
    a = {}
    a = {'a':"123"}
    a["a"] = "345"
    print(a.get("a"))

qwe()"""