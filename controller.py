import requests

from whois_info import get_whois_text, get_whois_info
from http_info import get_http_info
from dns_info import get_dns_records
from redis_handler import (
    check_whois_text,
    rec_whois_text,
    check_http_info,
    rec_http_info,
)
from utilits import encoding_dnames, decode_domain, MyException

# TODO попробовать реализовать класс с записью sql, encode и т.д.


class Controller:
    def __init__(self, dnames):
        self.dnames = encoding_dnames(dnames)

    def whois_dname(self, dname):
        whois_text = check_whois_text(dname)
        if whois_text is None:
            whois_text = get_whois_text(dname)
            rec_whois_text(dname, whois_text)
        else:
            whois_text = whois_text.decode("utf-8", "replace")
        return whois_text

    def whois_text(self):
        whois_text_dnames = {}
        for dname in self.dnames:
            whois_text = Controller.whois_dname(self, dname)
            dname = decode_domain(dname)
            whois_text_dnames[dname] = whois_text
        return whois_text_dnames

    def whois_info(self):
        whois_info_dnames = {}
        for dname in self.dnames:
            whois_text = Controller.whois_dname(self, dname)
            try:
                whois_info = get_whois_info(whois_text)
            except MyException as err:
                whois_info = err.DOMAIN_NOT_REGISTRED
            dname = decode_domain(dname)
            whois_info_dnames[dname] = whois_info
        return whois_info_dnames

    def http_info(self):
        http_info_dnames = {}
        for dname in self.dnames:
            http_info = check_http_info(dname)
            if http_info is None:
                http_info = Controller.forming_response_http(self, dname)
                rec_http_info(dname, http_info)
            else:
                http_info = http_info.decode("utf-8", "replace")
            dname = decode_domain(dname)
            http_info_dnames[dname] = http_info
        return http_info_dnames

    def forming_response_http(self, dname):
        try:
            http_info = get_http_info(dname)
            return f"code: {http_info[0]}, https: {http_info[1]}"
        except requests.exceptions.RequestException:
            return MyException.GETTING_HTTP_INFO_ERROR

    def dns_info(self):
        dns_info_domains = {}
        for dname in self.dnames:
            records_of_dname = Controller.get_records_of_dname(self, dname)
            dname = decode_domain(dname)
            dns_info_domains[dname] = records_of_dname
        return dns_info_domains

    def get_records_of_dname(self, dname):
        try:
            records_of_dname = get_dns_records(dname)
        except MyException as err:
            return err.GETTING_DNS_INFO_ERROR
        return records_of_dname

    def get_all_info_domains(self):
        all_info = {}
        whois_text_dnames = Controller.whois_text(self)
        whois_info_dnames = Controller.whois_info(self)
        http_info_dnames = Controller.http_info(self)
        dns_info_dnames = Controller.dns_info(self)
        for dname in self.dnames:
            dname = decode_domain(dname)
            all_info[dname] = {
                "whois_text": whois_text_dnames[dname],
                "whois_info": whois_info_dnames[dname],
                "http_info": http_info_dnames[dname],
                "dns_info": dns_info_dnames[dname],
            }
        return all_info
