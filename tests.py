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


def get_dns_records(dname: str):
    records_of_dname = {}
    type_of_records = ["A", "AAAA", "NS", "TXT", "MX", "CNAME"]
    for type_record in type_of_records:
        query = dns.message.make_query(
            dname, dns.rdatatype.from_text(type_record), payload=4096
        )
        response = dns.query.udp(query, "194.85.61.20", timeout=3)
        values_record = get_records_from_response(response)
        records_of_dname[type_record] = values_record
    print(type(records_of_dname["NS"]))
    if records_of_dname["NS"] is None:
        print(records_of_dname["NS"])
        raise MyException
    return records_of_dname


def get_records_from_response(response):
    values_record = []
    if not response.answer:
        values_record = None
    else:
        for answer in response.answer[0]:
            answer = str(answer).strip('"')
            values_record.append(answer)
    return values_record


print(get_dns_records("мама.рф"))

"""def a(s):
    bab = s+2
    if bab == 3:
        raise MyException
    return bab

print(a(1))"""
