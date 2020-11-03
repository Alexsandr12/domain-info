import redis

from config import EXPIRED_RECORD

redis_conn = redis.Redis()


# TODO хэш - домен, ключ - операция, значение - текст


def check_whois_text(dname):
    return redis_conn.get(f"whois_text_{dname}")


def rec_whois_text(dname, whois_text):
    redis_conn.setex(f"whois_text_{dname}", EXPIRED_RECORD, whois_text)


def check_http_info(dname):
    return redis_conn.get(f"http_info_{dname}")


def rec_http_info(dname, http_info):
    redis_conn.setex(f"http_info_{dname}", EXPIRED_RECORD, http_info)
