import socket
from typing import Dict

from config import WHOIS_TIMEOUT, PORT, WHOIS_SERVER
from projectexception import GettingWhoisTextError, DomainsNotRegistred


def search_whois_text(dname: str) -> str:
    """Получаем whois домена с ответственного whois-сервера.

    Args:
        dname: имя домена.

    Returns:
        str: информация whois о домене.
    """
    response = bytes()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(WHOIS_TIMEOUT)
        sock.connect((WHOIS_SERVER, PORT))
        sock.send(f"{dname}\r\n".encode())
        while True:
            try:
                data = sock.recv(4096)
            except socket.timeout:
                raise GettingWhoisTextError

            if data:
                response += data
            else:
                break

    return response.decode("utf-8", "replace")


def parsing_whois_text(whois_text: str) -> Dict[str, str]:
    """Парсинг whois текста

    Args:
        whois_text: whois текст

    Return:
        Dict[str, str]: словарь с полями whois и их значениями
    """
    if "created" not in whois_text:
        raise DomainsNotRegistred
    whois_text = whois_text.split("\n")
    whois_info = {}
    number_server = 0
    interested_info_whois_text = whois_text[5:-5]
    for whois_string in interested_info_whois_text:
        whois_string = whois_string.split(":", maxsplit=1)
        if whois_string[0] != "nserver":
            whois_info[whois_string[0]] = whois_string[1].strip()
        else:
            number_server += 1
            whois_info[f"nserver {number_server}"] = whois_string[1].strip()
    return whois_info
