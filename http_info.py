import requests
from typing import Tuple

from config import REQTIMEOUT


def search_http_info(dname: str) -> Tuple[int, str]:
    """Запрос http информации для домена

    Args:
        dname: домен

    Return:
        Tuple[int, str]: кортеж со значением статус кода http запроса и статусом проверки SSL
    """
    try:
        response = requests.get(f"https://{dname}", verify=True, timeout=REQTIMEOUT)
        return response.status_code, "True"
    except requests.exceptions.SSLError:
        response = requests.get(f"http://{dname}", verify=False, timeout=REQTIMEOUT)
        return response.status_code, "False"
