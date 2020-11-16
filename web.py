import json

from flask import Flask, request

from controller import whois_text, whois_info, http_info, dns_info, get_all_info_domains
from config import INDENT

app = Flask(__name__)


# TODO правильная запись в редис?
# TODO проверить все вложенности, возможно ли избавиться
# TODO придумать нормальные названия для всех функцией
# TODO сделать все сервисные ошибки для вывода клиенту


@app.route("/get_whois_text", methods=["POST", "GET"])
def get_whois_text():
    dnames = request.json["domain"]
    whois_text_dnames = whois_text(dnames)
    return json.dumps(whois_text_dnames, indent=INDENT, ensure_ascii=False)


@app.route("/get_whois_info", methods=["POST", "GET"])
def get_whois_info():
    dnames = request.json["domain"]
    whois_info_dnames = whois_info(dnames)
    return json.dumps(whois_info_dnames, indent=INDENT, ensure_ascii=False)


@app.route("/get_http_info", methods=["POST", "GET"])
def get_http_info():
    dnames = request.json["domain"]
    http_info_dnames = http_info(dnames)
    return json.dumps(http_info_dnames, indent=INDENT, ensure_ascii=False)


@app.route("/get_dns_info", methods=["POST", "GET"])
def get_dns_info():
    dnames = request.json["domain"]
    dns_info_domains = dns_info(dnames)
    return json.dumps(dns_info_domains, indent=INDENT, ensure_ascii=False)


@app.route("/get_all_info", methods=["POST", "GET"])
def get_all_info():
    dnames = request.json["domain"]
    all_info_domains = get_all_info_domains(dnames)
    return json.dumps(all_info_domains, indent=INDENT, ensure_ascii=False)


if __name__ == "__main__":
    app.run()
