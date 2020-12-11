import redis

from config import EXPIRED_RECORD
from utilits import MyException

redis_conn = redis.Redis()

# TODO decode для dns_info, чтобы выводились списки, а не строки с записями


def check_connect_redis():
    try:
        redis_conn.ping()
    except redis.exceptions.ConnectionError:
        raise MyException


def check_cache_redis(dname, method):
    cache = redis_conn.get(f"{method}:{dname}")
    if cache:
        return cache.decode("utf-8", "replace")
    return cache


def rec_redis(dname, method, info):
    redis_conn.setex(f"{method}:{dname}", EXPIRED_RECORD, info)


def check_dns_info(dname, method):
    dns_info = redis_conn.hgetall(f"{method}:{dname}")
    if dns_info:
        dns_info_decode = {}
        for key, val in dns_info.items():
            dns_info_decode[key.decode("utf-8", "replace")] = val.decode(
                "utf-8", "replace"
            )
        return dns_info_decode
    return dns_info


def rec_dns_info(dname, method, dns_info):
    for type_record, val_record in dns_info.items():
        redis_conn.hset(f"{method}:{dname}", type_record, str(val_record))
    redis_conn.expire(f"{method}:{dname}", EXPIRED_RECORD)


def get_all_key():
    all_key = []
    for key in redis_conn.scan_iter():
        all_key.append(key.decode("utf-8", "replace"))
    return all_key
