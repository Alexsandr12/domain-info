import idna
from typing import List


def encoding_domains(domains: list) -> List[str]:
    """Кодирование доменов в punycode

    Args:
        domains: список доменов
    Return:
        List[str]: списов доменов в punycode
    """
    encode_domains = []
    for dname in domains:
        dname = dname.encode("idna").decode("utf-8")
        encode_domains.append(dname)
    return encode_domains


def decode_domain(dname: str) -> str:
    """Декодирование домена из punycode

    Args:
        dname: домен в punycode
    Return:
        str: домен
    """
    dname = idna.decode(dname)
    return dname


def get_request_data(request_dict: dict) -> tuple:
    """Формирует параметры для post-запросов.

    Args:
        request_dict: данные переданные в post-запрос
    Return:
        tuple: параметры для post-запросов
    """
    return request_dict["domain"], request_dict.get("use_cache", "True")
