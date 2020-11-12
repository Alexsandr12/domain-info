import requests

from config import REQTIMEOUT


def get_http_info(dname):
    try:
        response = requests.get(f"https://{dname}", verify=True, timeout=REQTIMEOUT)
        return [response.status_code, 'True']
    except requests.exceptions.SSLError:
        response = requests.get(f"http://{dname}", verify=False, timeout=REQTIMEOUT)
        return [response.status_code, 'False']

