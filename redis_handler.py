import redis
from typing import Union, List

from config import EXPIRED_RECORD
from exceptions import BdErrors

redis_conn = redis.Redis()

# TODO decode для dns_info, чтобы выводились списки, а не строки с записями


def check_connect_redis():
    """Проверка доступа к redis"""
    try:
        redis_conn.ping()
    except redis.exceptions.ConnectionError:
        raise BdErrors


def check_cache_redis(dname: str, method: str) -> Union[str, None]:
    """Запрос данных их кэша по параметрам

    Args:
        dname: домен
        method: название метода

    Return:
        Union[str, None]: данные их кэша редиса или None, если нет данных по передаваемым параметрам
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
        Union[dict, None]: словать с типами записей и их значениями или None
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
        dns_info: ресурсные записи и их значения
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
        raise BdErrors
