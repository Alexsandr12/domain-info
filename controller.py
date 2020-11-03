import json

from whois_info import get_whois_text, get_whois_info
from redis_handler import check_whois_text, rec_whois_text, check_http_info, rec_http_info
from http_info import get_http_info


def whois_dname(dname):
    whois_text = check_whois_text(dname)
    if whois_text is None:
        whois_text = get_whois_text(dname)
        rec_whois_text(dname, whois_text)
    else:
        whois_text = whois_text.decode("utf-8", "replace")
    return whois_text


def whois_text(dnames):
    whois_text_dnames = {}
    for dname in dnames:
        whois_text = whois_dname(dname)
        whois_text_dnames[dname] = whois_text
    return whois_text_dnames


def whois_info(dnames):
    whois_info_dnames = {}
    for dname in dnames:
        whois_text = whois_dname(dname)
        whois_info = get_whois_info(whois_text)
        whois_info_dnames[dname] = whois_info
    return whois_info_dnames


def http_info(dnames):
    http_info_dnames = {}
    for dname in dnames:
        http_info = check_http_info(dname)
        if http_info is None:
            http_info = get_http_info(dname)
            rec_http_info(dname, http_info)
        else:
            http_info = http_info.decode("utf-8", "replace")
        http_info_dnames[dname] = http_info
    return http_info_dnames
