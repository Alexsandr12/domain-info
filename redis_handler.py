import redis
from typing import Union, List

from config import EXPIRED_RECORD
from exceptions import RedisError

redis_conn = redis.Redis()


def check_connect_redis() -> None:
    """Проверка доступа к redis"""
    try:
        redis_conn.ping()
    except redis.exceptions.ConnectionError:
        raise RedisError


def check_cache_redis(dname: str, method: str) -> Union[str, None]:
    """Поиск данных в кэш

    Args:
        dname: домен
        method: название метода

    Return:
        Union[str, None]: результаты поиска
    """
    if cache := redis_conn.get(f"{method}:{dname}"):
        return cache.decode("utf-8", "replace")
    return None


def rec_redis(dname: str, method: str, info: str):
    """Запись передаваемых данных

    Args:
        dname: домен
        method: название метода
        info: передаваемые данные
    """
    redis_conn.setex(f"{method}:{dname}", EXPIRED_RECORD, info)


def check_dns_info(dname: str, method: str) -> Union[dict, None]:
    """Запрос из кэша dns-info по домену

    Args:
        dname: домен
        method: название метода

    Return:
        Union[dict, None]: словать с типами ns записей и их значениями / None
    """
    if dns_info := redis_conn.hgetall(f"{method}:{dname}"):
        dns_info_decode = {}
        for type_record, val_record in dns_info.items():
            dns_info_decode[type_record.decode("utf-8", "replace")] = val_record.decode(
                "utf-8", "replace"
            )
        return dns_info_decode
    return None


def rec_dns_info(dname: str, method: str, dns_info: dict):
    """Запись dns-info домена

    Args:
        dname: домен
        method: название метода
        dns_info: ns записи и их значения
    """
    for type_record, val_record in dns_info.items():
        redis_conn.hset(f"{method}:{dname}", type_record, str(val_record))
    redis_conn.expire(f"{method}:{dname}", EXPIRED_RECORD)


def get_all_key() -> List[str]:
    """Запрос всех ключей их кэша

    Return:
        List[str]: список со всеми включами
    """
    try:
        return [key.decode("utf-8", "replace") for key in redis_conn.scan_iter()]
    except redis.exceptions.ConnectionError:
        raise RedisError
