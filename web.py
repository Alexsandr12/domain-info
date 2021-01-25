import json

from flask import Flask, request

from controller import ControllerPost, ControllerGet
from config import INDENT, ENSURE_ASCII

app = Flask(__name__)

# TODO поправить описание


@app.route("/get_whois_text", methods=["POST"])
def get_whois_text() -> str:
    """Получене whois текста для доменов

    Return:
        str: json с доменами и whois текстом
    """
    domains = request.json["domain"]
    use_cache = request.json["use_cache"]
    whois_text_dnames = ControllerPost(
        domains, "get_whois_text", use_cache
    ).forming_response()

    return json.dumps(whois_text_dnames, indent=INDENT, ensure_ascii=ENSURE_ASCII)


@app.route("/get_whois_info", methods=["POST"])
def get_whois_info() -> str:
    """Route запроса инфы из controller по передаваемым параметрам

    Return:
        str: ответ за запрос
    """
    domains = request.json["domain"]
    use_cache = request.json["use_cache"]
    whois_info_dnames = ControllerPost(
        domains, "get_whois_info", use_cache
    ).forming_response()

    return json.dumps(whois_info_dnames, indent=INDENT, ensure_ascii=ENSURE_ASCII)


@app.route("/get_http_info", methods=["POST"])
def get_http_info() -> str:
    """Route запроса инфы из controller по передаваемым параметрам

    Return:
        str: ответ за запрос
    """
    domains = request.json["domain"]
    use_cache = request.json["use_cache"]
    http_info_domains = ControllerPost(
        domains, "get_http_info", use_cache
    ).forming_response()

    return json.dumps(http_info_domains, indent=INDENT, ensure_ascii=ENSURE_ASCII)


@app.route("/get_dns_info", methods=["POST"])
def get_dns_info() -> str:
    """Route запроса инфы из controller по передаваемым параметрам

    Return:
        str: ответ за запрос
    """
    domains = request.json["domain"]
    use_cache = request.json["use_cache"]
    dns_info_domains = ControllerPost(
        domains, "get_dns_info", use_cache
    ).forming_response()

    return json.dumps(dns_info_domains, indent=INDENT, ensure_ascii=ENSURE_ASCII)


@app.route("/get_all_info", methods=["POST"])
def get_all_info() -> str:
    """Route запроса инфы из controller по передаваемым параметрам

    Return:
        str: ответ за запрос
    """
    domains = request.json["domain"]
    use_cache = request.json["use_cache"]
    all_info_domains = ControllerPost(
        domains, "get_all_info", use_cache
    ).forming_response()

    return json.dumps(all_info_domains, indent=INDENT, ensure_ascii=ENSURE_ASCII)


@app.route("/get_service_status", methods=["GET"])
def get_service_status() -> str:
    """Запрос статуса подключения к базам данных

    Return:
        str: результат запроса
    """
    service_status = ControllerGet().check_connect_db()

    return json.dumps(service_status, indent=INDENT, ensure_ascii=ENSURE_ASCII)


@app.route("/get_all_cached_domains", methods=["GET"])
def get_all_cached_domains() -> str:
    """Запрос всех закэшированных доменов из redis

    Return:
        str: результат запроса
    """
    all_domains = ControllerGet().get_all_cached_domains()

    return json.dumps(all_domains, ensure_ascii=ENSURE_ASCII)


@app.route("/get_info_from_sql", methods=["GET"])
def get_info_from_sql() -> str:
    """Запрос всей информации из mariadb

    Return:
        str: результат запроса
    """
    info_from_sql = ControllerGet().get_info_from_sql()

    return json.dumps(info_from_sql, indent=INDENT, ensure_ascii=ENSURE_ASCII)


if __name__ == "__main__":
    app.run()
