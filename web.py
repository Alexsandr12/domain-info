import json

from flask import Flask, request

from controller import Controller
from config import INDENT

app = Flask(__name__)


# TODO проверить все вложенности, возможно ли избавиться
# TODO придумать нормальные названия для всех функцией (find, search)


@app.route("/get_whois_text", methods=["POST"])
def get_whois_text():
    domains = request.json["domain"]
    use_cache = request.json["use_cache"]
    whois_text_dnames = Controller(domains, "get_whois_text", use_cache).forming_response()
    return json.dumps(whois_text_dnames, indent=INDENT, ensure_ascii=False)


@app.route("/get_whois_info", methods=["POST"])
def get_whois_info():
    domains = request.json["domain"]
    use_cache = request.json["use_cache"]
    whois_info_dnames = Controller(domains, "get_whois_info", use_cache).forming_response()
    return json.dumps(whois_info_dnames, indent=INDENT, ensure_ascii=False)


@app.route("/get_http_info", methods=["POST"])
def get_http_info():
    domains = request.json["domain"]
    use_cache = request.json["use_cache"]
    http_info_domains = Controller(domains, "get_http_info", use_cache).forming_response()
    return json.dumps(http_info_domains, indent=INDENT, ensure_ascii=False)


@app.route("/get_dns_info", methods=["POST"])
def get_dns_info():
    domains = request.json["domain"]
    use_cache = request.json["use_cache"]
    dns_info_domains = Controller(domains, "get_dns_info", use_cache).forming_response()
    return json.dumps(dns_info_domains, indent=INDENT, ensure_ascii=False)


@app.route("/get_all_info", methods=["POST"])
def get_all_info():
    domains = request.json["domain"]
    use_cache = request.json["use_cache"]
    all_info_domains = Controller(domains, "get_all_info", use_cache).forming_response()
    return json.dumps(all_info_domains, indent=INDENT, ensure_ascii=False)


if __name__ == "__main__":
    app.run()
