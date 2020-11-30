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
from utilits import encoding_domains, decode_domain, MyException
from sql_handler import add_data_in_mariadb
from validation import Validation


# TODO dns_info запись в редис как строку
# TODO 2 класса, один(self, domains, methods) формирует ответ, записывает в sql и get методы, второй(dname) получает данные из других модулей
# TODO  переименовать все dnames в domains
# TODO отдельный модуль для валидации


class Controller:
    def __init__(self, domains):
        self.domains_puny = encoding_domains(domains)

    def forming_response(self, method):
        try:
            domains = self.validation_domains()
        except MyException as err:
            return err.DOMAINS_LIMIT_EXCEEDED
        if method is 'get_whois_text':
            response = self.whois_text(domains["domains_valid"])
        elif method is 'get_whois_info':
            response = self.whois_info(domains["domains_valid"])
        elif method is "get_http_info":
            response = self.http_info(domains["domains_valid"])
        elif method is 'get_dns_info':
            response = self.dns_info(domains["domains_valid"])
        elif method is 'get_all_info':
            response = self.get_all_info_domains(domains["domains_valid"])
        if domains['domains_not_valid']:
            response['Invalid domain names'] = domains['domains_not_valid']
        return response

    def validation_domains(self):
        Validation(self.domains_puny).checking_len_domains()
        return Validation(self.domains_puny).checking_correct_domains()

    def whois_dname(self, dname):
        whois_text = check_whois_text(dname)
        if whois_text is None:
            whois_text = get_whois_text(dname)
            rec_whois_text(dname, whois_text)
        else:
            whois_text = whois_text.decode("utf-8", "replace")
        return whois_text

    def whois_text(self, domains):
        whois_text_domains = {}
        for dname in domains:
            whois_text = self.whois_dname(dname)
            dname = decode_domain(dname)
            whois_text_domains[dname] = whois_text
        return whois_text_domains

    def whois_info(self, domains):
        whois_info_domains = {}
        for dname in domains:
            whois_text = self.whois_dname(dname)
            try:
                whois_info = get_whois_info(whois_text)
                add_data_in_mariadb(dname, "get_whois_info", True)
            except MyException as err:
                whois_info = err.DOMAIN_NOT_REGISTRED
                add_data_in_mariadb(dname, "get_whois_info", False)
            dname = decode_domain(dname)
            whois_info_domains[dname] = whois_info
        return whois_info_domains

    def http_info(self, domains):
        http_info_domains = {}
        for dname in domains:
            http_info = check_http_info(dname)
            if http_info is None:
                http_info = self.forming_response_http(dname)
                rec_http_info(dname, http_info)
            else:
                http_info = http_info.decode("utf-8", "replace")
            Controller.forming_http_method_mariadb(self, dname, http_info)
            dname = decode_domain(dname)
            http_info_domains[dname] = http_info
        return http_info_domains

    def forming_response_http(self, dname):
        try:
            http_info = get_http_info(dname)
            return f"code: {http_info[0]}, https: {http_info[1]}"
        except requests.exceptions.RequestException:
            return MyException.GETTING_HTTP_INFO_ERROR

    def forming_http_method_mariadb(self, dname, http_info):
        if MyException.GETTING_HTTP_INFO_ERROR in http_info:
            add_data_in_mariadb(dname, "get_http_info", False)
        else:
            add_data_in_mariadb(dname, "get_http_info", True)

    def dns_info(self, domains):
        dns_info_domains = {}
        for dname in domains:
            records_of_dname = self.get_records_of_dname(dname)
            dname = decode_domain(dname)
            dns_info_domains[dname] = records_of_dname
        return dns_info_domains

    def get_records_of_dname(self, dname):
        try:
            records_of_dname = get_dns_records(dname)
            add_data_in_mariadb(dname, "get_dns_info", True)
        except MyException as err:
            add_data_in_mariadb(dname, "get_dns_info", False)
            return err.GETTING_DNS_INFO_ERROR
        return records_of_dname

    def get_all_info_domains(self, domains):
        all_info = {}
        whois_text_domains = self.whois_text(domains)
        whois_info_domains = self.whois_info(domains)
        http_info_domains = self.http_info(domains)
        dns_info_domains = self.dns_info(domains)
        for dname in domains:
            dname = decode_domain(dname)
            all_info[dname] = {
                "whois_text": whois_text_domains[dname],
                "whois_info": whois_info_domains[dname],
                "http_info": http_info_domains[dname],
                "dns_info": dns_info_domains[dname],
            }
        return all_info
