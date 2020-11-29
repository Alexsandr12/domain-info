import redis

from config import EXPIRED_RECORD

redis_conn = redis.Redis()


# TODO 2 модуля, на запись и на check


def check_whois_text(dname):
    return redis_conn.get(f"whois_text:{dname}")


def rec_whois_text(dname, whois_text):
    redis_conn.setex(f"whois_text:{dname}", EXPIRED_RECORD, whois_text)


def check_http_info(dname):
    return redis_conn.get(f"http_info:{dname}")


def rec_http_info(dname, http_info):
    redis_conn.setex(f"http_info:{dname}", EXPIRED_RECORD, http_info)
