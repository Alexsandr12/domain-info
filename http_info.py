import requests

from config import REQTIMEOUT


def get_http_info(dname):
    dname = dname.encode("idna").decode("utf-8")
    try:
        response = requests.get(f"https://{dname}", verify=True, timeout=REQTIMEOUT)
        http_info = f"code: {response.status_code}, https: True"
        return http_info
    except requests.exceptions.SSLError:
        response = requests.get(f"http://{dname}", verify=False, timeout=REQTIMEOUT)
        http_info = f"code: {response.status_code}, https: False"
        return http_info
    except requests.exceptions.RequestException:
        return "ошибка получения данных"
