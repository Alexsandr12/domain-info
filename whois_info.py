import socket

from config import TIMEOUT, PORT, WHOIS_SERVER


def get_whois_text(dname: str) -> str:
    """Получаем whois доменов с ответственного whois-сервера.

    Args:
        dname: имя домена.

    Returns:
        str: информация whois о домене.
    """
    response = bytes()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(TIMEOUT)
        sock.connect((WHOIS_SERVER, PORT))
        sock.send(f"{dname}\r\n".encode())
        while True:
            try:
                data = sock.recv(4096)
            except socket.timeout:
                raise Exception

            if data:
                response += data
            else:
                break

    return response.decode("utf-8", "replace")


def get_whois_info(whois_text):
    if "created" not in whois_text:
        return 'Домен не зарегистрирован'
    whois_text = whois_text.split("\n")
    whois_info = {}
    number_server = 0
    whois_text = whois_text[5:-5]
    for whois in whois_text:
        whois = whois.split(":", maxsplit=1)
        if whois[0] != "nserver":
            whois_info[whois[0]] = whois[1].strip()
        else:
            number_server += 1
            whois_info[f"nserver {number_server}"] = whois[1].strip()
    return whois_info
