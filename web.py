import json

from flask import Flask, request

from controller import Controller
from config import INDENT

app = Flask(__name__)


# TODO правильная запись в редис?
# TODO проверить все вложенности, возможно ли избавиться
# TODO придумать нормальные названия для всех функцией (find, search)
# TODO сделать все сервисные ошибки для вывода клиенту


@app.route("/get_whois_text", methods=["POST", "GET"])
def get_whois_text():
    dnames = request.json["domain"]
    whois_text_dnames = Controller(dnames).whois_text()
    return json.dumps(whois_text_dnames, indent=INDENT, ensure_ascii=False)


@app.route("/get_whois_info", methods=["POST", "GET"])
def get_whois_info():
    dnames = request.json["domain"]
    whois_info_dnames = Controller(dnames).whois_info()
    return json.dumps(whois_info_dnames, indent=INDENT, ensure_ascii=False)


@app.route("/get_http_info", methods=["POST", "GET"])
def get_http_info():
    dnames = request.json["domain"]
    http_info_dnames = Controller(dnames).http_info()
    return json.dumps(http_info_dnames, indent=INDENT, ensure_ascii=False)


@app.route("/get_dns_info", methods=["POST", "GET"])
def get_dns_info():
    dnames = request.json["domain"]
    dns_info_domains = Controller(dnames).dns_info()
    return json.dumps(dns_info_domains, indent=INDENT, ensure_ascii=False)


@app.route("/get_all_info", methods=["POST", "GET"])
def get_all_info():
    dnames = request.json["domain"]
    all_info_domains = Controller(dnames).get_all_info_domains()
    return json.dumps(all_info_domains, indent=INDENT, ensure_ascii=False)


if __name__ == "__main__":
    app.run()
