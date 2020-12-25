import requests
from typing import List

from config import REQTIMEOUT


def search_http_info(dname: str) -> List[str]:
    """Запрос http информации для домена

    :param
        dname: домен

    :return:
        List[str, str]: списков со значением статус кода http запроса и статусом проверки SSL
    """
    try:
        response = requests.get(f"https://{dname}", verify=True, timeout=REQTIMEOUT)
        return [response.status_code, "True"]
    except requests.exceptions.SSLError:
        response = requests.get(f"http://{dname}", verify=False, timeout=REQTIMEOUT)
        return [response.status_code, "False"]
