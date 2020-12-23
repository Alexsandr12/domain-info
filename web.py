import json

from flask import Flask, request

from controller import ControllerPost, ControllerGet
from config import INDENT, ENSURE_ASCII
from datetime import datetime

app = Flask(__name__)


# TODO проверить все вложенности, возможно ли избавиться
# TODO придумать нормальные названия для всех функцией (find, search)


@app.route("/get_whois_text", methods=["POST"])
def get_whois_text() -> str:
    """Route для вызова метода get_whois_text из controller

    :return:
        str: результат вызова метода
    """
    domains = request.json["domain"]
    use_cache = request.json["use_cache"]
    whois_text_dnames = ControllerPost(
        domains, "get_whois_text", use_cache
    ).forming_response()
    return json.dumps(whois_text_dnames, indent=INDENT, ensure_ascii=ENSURE_ASCII)


@app.route("/get_whois_info", methods=["POST"])
def get_whois_info() -> str:
    """Route для вызова метода get_whois_info из controller

        :return:
            str: результат вызова метода
        """
    domains = request.json["domain"]
    use_cache = request.json["use_cache"]
    whois_info_dnames = ControllerPost(
        domains, "get_whois_info", use_cache
    ).forming_response()
    return json.dumps(whois_info_dnames, indent=INDENT, ensure_ascii=ENSURE_ASCII)


@app.route("/get_http_info", methods=["POST"])
def get_http_info() -> str:
    """Route для вызова метода get_http_info из controller

    :return:
        str: результат вызова метода
    """
    domains = request.json["domain"]
    use_cache = request.json["use_cache"]
    http_info_domains = ControllerPost(
        domains, "get_http_info", use_cache
    ).forming_response()
    return json.dumps(http_info_domains, indent=INDENT, ensure_ascii=ENSURE_ASCII)


@app.route("/get_dns_info", methods=["POST"])
def get_dns_info() -> str:
    """Route для вызова метода get_dns_info из controller

    :return:
        str: результат вызова метода
    """
    domains = request.json["domain"]
    use_cache = request.json["use_cache"]
    dns_info_domains = ControllerPost(
        domains, "get_dns_info", use_cache
    ).forming_response()
    return json.dumps(dns_info_domains, indent=INDENT, ensure_ascii=ENSURE_ASCII)


@app.route("/get_all_info", methods=["POST"])
def get_all_info() -> str:
    """Route для вызова метода get_all_info из controller

    :return:
        str: результат вызова метода
    """
    domains = request.json["domain"]
    use_cache = request.json["use_cache"]
    all_info_domains = ControllerPost(
        domains, "get_all_info", use_cache
    ).forming_response()
    return json.dumps(all_info_domains, indent=INDENT, ensure_ascii=ENSURE_ASCII)


@app.route("/get_servise_status", methods=["GET"])
def get_servise_status() -> str:
    """Запрос статуса подключения к базам данных

    :return:
        str: результат запроса
    """
    servise_status = ControllerGet().check_connect_DB()
    return json.dumps(servise_status, indent=INDENT, ensure_ascii=ENSURE_ASCII)


@app.route("/get_all_cached_domains", methods=["GET"])
def get_all_cached_domains() -> str:
    """Запрос всех закэшированных доменов из redis

    :return:
        str: результат запроса
    """
    all_domains = ControllerGet().get_all_cached_domains()
    return json.dumps(all_domains, ensure_ascii=ENSURE_ASCII)


@app.route("/get_info_from_mariadb", methods=["GET"])
def get_info_from_mariadb() -> str:
    """Запрос всей информации из mariadb

    :return:
        str: результат запроса
    """
    info_from_mariadb = ControllerGet().get_info_from_mariadb()
    return json.dumps(info_from_mariadb, indent=INDENT, ensure_ascii=ENSURE_ASCII)


if __name__ == "__main__":
    app.run()
