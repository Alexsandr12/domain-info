import requests

from whois_info import get_whois_text, get_whois_info
from http_info import get_http_info
from dns_info import get_dns_records
from redis_handler import check_cache_redis, rec_redis, check_dns_info, rec_dns_info
from utilits import encoding_domains, decode_domain, MyException
from sql_handler import add_data_in_mariadb
from validation import Validation


# TODO dns_info запись в редис как строку
# TODO 2 класса, один работает с доменами, другой только методы
# TODO  либо отдельный модуль для redis либо внутри текущих модулей
# TODO добавить условие актуальности редис


class Controller:
    def __init__(self, domains, method):
        self.domains_puny = encoding_domains(domains)
        self.method = method

    def forming_response(self):
        response = {}
        try:
            domains = self.validation_domains()
        except MyException as err:
            return err.DOMAINS_LIMIT_EXCEEDED
        for dname in domains["domains_valid"]:
            response_from_nethod = self.get_response_from_method(dname)
            dname = decode_domain(dname)
            response[dname] = response_from_nethod
        if domains["domains_not_valid"]:
            response["Invalid domain names"] = domains["domains_not_valid"]
        return response

    def validation_domains(self):
        Validation(self.domains_puny).checking_len_domains()
        return Validation(self.domains_puny).checking_valid_domains()

    def get_response_from_method(self, dname):
        if self.method == "get_whois_text":
            response = self.whois_text(dname)
        elif self.method == "get_whois_info":
            response = self.whois_info(dname)
        elif self.method == "get_http_info":
            response = self.http_info(dname)
        elif self.method == "get_dns_info":
            response = self.dns_info(dname)
        elif self.method == "get_all_info":
            response = self.get_all_info_domains(dname)
        return response

    def whois_text(self, dname):
        whois_text = check_cache_redis(dname, self.method)
        if whois_text is None:
            try:
                whois_text = get_whois_text(dname)
            except MyException as err:
                add_data_in_mariadb(dname, self.method, False)
                return err.GETTING_WHOIS_TEXT_ERROR
            rec_redis(dname, self.method, whois_text)
            add_data_in_mariadb(dname, self.method, True)
        return whois_text

    def whois_info(self, dname):
        whois_text = self.whois_text(dname)
        if whois_text == "GETTING_WHOIS_TEXT_ERROR":
            return whois_text
        try:
            whois_info = get_whois_info(whois_text)
            add_data_in_mariadb(dname, self.method, True)
        except MyException as err:
            whois_info = err.DOMAIN_NOT_REGISTRED
            add_data_in_mariadb(dname, self.method, False)
        return whois_info

    def http_info(self, dname):
        http_info = check_cache_redis(dname, self.method)
        if http_info is None:
            http_info = self.forming_response_http(dname)
            rec_redis(dname, self.method, http_info)
        self.forming_http_method_mariadb(dname, http_info)
        return http_info

    def forming_response_http(self, dname):
        try:
            http_info = get_http_info(dname)
            return f"code: {http_info[0]}, https: {http_info[1]}"
        except requests.exceptions.RequestException:
            return MyException.GETTING_HTTP_INFO_ERROR

    def forming_http_method_mariadb(self, dname, http_info):
        if MyException.GETTING_HTTP_INFO_ERROR in http_info:
            add_data_in_mariadb(dname, self.method, False)
        else:
            add_data_in_mariadb(dname, self.method, True)

    def dns_info(self, dname):
        dns_info = check_dns_info(dname, self.method)
        if not dns_info:
            try:
                dns_info = get_dns_records(dname)
            except MyException as err:
                add_data_in_mariadb(dname, self.method, False)
                return err.GETTING_DNS_INFO_ERROR
        add_data_in_mariadb(dname, self.method, True)
        rec_dns_info(dname, self.method, dns_info)
        return dns_info

    def get_all_info_domains(self, dname):
        all_info = {}
        all_info["whois_text"] = self.whois_text(dname)
        all_info["whois_info"] = self.whois_info(dname)
        all_info["http_info"] = self.http_info(dname)
        all_info["dns_info"] = self.dns_info(dname)
        return all_info
