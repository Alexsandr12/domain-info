import requests

from whois_info import get_whois_text, get_whois_info
from http_info import get_http_info
from dns_info import get_dns_records
from redis_handler import (
    check_cache_redis,
    rec_redis,
    check_dns_info,
    rec_dns_info,
    check_connect_redis,
    get_all_key,
)
from sql_handler import add_data_in_mariadb, check_connect_mariadb, get_all_data
from utilits import encoding_domains, decode_domain, MyException
from validation import Validation
from logger import (
    logger_client,
    logger_get_all_info,
    logger_get_dns_info,
    logger_get_http_info,
    logger_get_whois_info,
    logger_get_whois_text,
)


# TODO попробовать сделать отдельный метод для sql и redis
# TODO доделать логер для всех модулей


class ControllerGet:
    def check_connect_DB(self):
        servise_status = {"status": "successful"}
        try:
            check_connect_redis()
        except MyException as err:
            servise_status["status"] = "error"
            servise_status["error"] = err.REDIS_ERROR
        try:
            check_connect_mariadb()
        except MyException as err:
            servise_status["status"] = "error"
            if servise_status.get("error") is None:
                servise_status["error"] = err.SQL_BD_ERROR
            else:
                servise_status["error"] = err.DB_ERROR
        return servise_status

    def get_all_cached_domains(self):
        try:
            check_connect_redis()
        except MyException as err:
            return err.REDIS_ERROR
        all_cached_domains = []
        all_key_redis = get_all_key()
        for key in all_key_redis:
            key = key.split(":")
            dname = decode_domain(key[1])
            all_cached_domains.append(dname)
        all_cached_domains = set(all_cached_domains)
        return list(all_cached_domains)

    def get_info_from_sql(self):
        try:
            check_connect_mariadb()
        except MyException as err:
            return err.SQL_BD_ERROR
        info_from_sql = {}
        sql_all_data = get_all_data()
        for sql_data in sql_all_data:
            sql_data = list(sql_data)
            if sql_data[4] == 0:
                sql_data[4] = False
            else:
                sql_data[4] = True
            dname = decode_domain(sql_data[1])
            if info_from_sql.get(dname) is None:
                info_from_sql[dname] = []
            info_from_sql[dname].append(
                {
                    "id": sql_data[0],
                    "data": f"{sql_data[2].year}.{sql_data[2].month}.{sql_data[2].day}",
                    "time": f"{sql_data[2].hour}:{sql_data[2].minute}:{sql_data[2].second}",
                    "method": sql_data[3],
                    "status": sql_data[4],
                }
            )
        return info_from_sql


class ControllerPost:
    def __init__(self, domains, method, use_cache):
        self.domains = domains
        self.domains_puny = encoding_domains(domains)
        self.method = method
        self.use_cache = use_cache

    def forming_response(self):
        try:
            check_connect_mariadb()
            check_connect_redis()
        except MyException as err:
            logger_client.exception(
                f"Запрос клиента: метод: {self.method}, домены: {self.domains}, use_cache: {self.use_cache}. Ответ: {err.GENERAL_ERROR}"
            )
            return err.GENERAL_ERROR
        response = {}
        try:
            domains = self.validation_domains()
        except MyException as err:
            logger_client.exception(
                f"Запрос клиента: метод: {self.method}, домены: {self.domains}, use_cache: {self.use_cache}. Ответ: {err.DOMAINS_LIMIT_EXCEEDED}"
            )
            return err.DOMAINS_LIMIT_EXCEEDED
        for dname in domains["domains_valid"]:
            response_from_nethod = self.get_response_from_method(dname)
            dname = decode_domain(dname)
            response[dname] = response_from_nethod
        if domains["domains_not_valid"]:
            response["Invalid domain names"] = domains["domains_not_valid"]
        logger_client.debug(
            f"Запрос клиента: метод: {self.method}, домены: {self.domains}, use_cache: {self.use_cache}. Ответ: {response}"
        )
        return response

    def validation_domains(self):
        Validation(self.domains_puny).checking_len_domains()
        return Validation(self.domains_puny).checking_valid_domains()

    def get_response_from_method(self, dname):
        if self.method == "get_whois_text":
            response = self.whois_text(dname)
            logger_get_whois_text.debug(
                f"Метод: {self.method}, домен: {dname}, use_cache: {self.use_cache}, return метода : {response}"
            )
        elif self.method == "get_whois_info":
            response = self.whois_info(dname)
            logger_get_whois_info.debug(
                f"Метод: {self.method}, домен: {dname}, use_cache: {self.use_cache}, return метода : {response}"
            )
        elif self.method == "get_http_info":
            response = self.http_info(dname)
            logger_get_http_info.debug(
                f"Метод: {self.method}, домен: {dname}, use_cache: {self.use_cache}, return метода : {response}"
            )
        elif self.method == "get_dns_info":
            response = self.dns_info(dname)
            logger_get_dns_info.debug(
                f"Метод: {self.method}, домен: {dname}, use_cache: {self.use_cache}, return метода : {response}"
            )
        elif self.method == "get_all_info":
            response = self.get_all_info_domains(dname)
            logger_get_all_info.debug(
                f"Метод: {self.method}, домен: {dname}, use_cache: {self.use_cache}, return метода : {response}"
            )
        # rec_logger_method(self.method, dname, self.use_cache, response)
        return response

    def whois_text(self, dname):
        whois_text = None
        if self.use_cache == "True":
            whois_text = check_cache_redis(dname, "get_whois_text")
        if whois_text is None:
            try:
                whois_text = get_whois_text(dname)
            except MyException as err:
                add_data_in_mariadb(dname, "get_whois_text", False)
                return err.GETTING_WHOIS_TEXT_ERROR
            rec_redis(dname, "get_whois_text", whois_text)
            add_data_in_mariadb(dname, "get_whois_text", True)
        return whois_text

    def whois_info(self, dname):
        whois_text = self.whois_text(dname)
        if whois_text == MyException.GETTING_WHOIS_TEXT_ERROR:
            return whois_text
        try:
            whois_info = get_whois_info(whois_text)
            add_data_in_mariadb(dname, "get_whois_info", True)
        except MyException as err:
            whois_info = err.DOMAIN_NOT_REGISTRED
            add_data_in_mariadb(dname, "get_whois_info", False)
        return whois_info

    def http_info(self, dname):
        http_info = None
        if self.use_cache == "True":
            http_info = check_cache_redis(dname, "get_http_info")
        if http_info is None:
            http_info = self.forming_response_http(dname)
            rec_redis(dname, "get_http_info", http_info)
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
            add_data_in_mariadb(dname, "get_http_info", False)
        else:
            add_data_in_mariadb(dname, "get_http_info", True)

    def dns_info(self, dname):
        dns_info = None
        if self.use_cache == "True":
            dns_info = check_dns_info(dname, "get_dns_info")
        if not dns_info:
            try:
                dns_info = get_dns_records(dname)
            except MyException as err:
                add_data_in_mariadb(dname, "get_dns_info", False)
                return err.GETTING_DNS_INFO_ERROR
        add_data_in_mariadb(dname, "get_dns_info", True)
        rec_dns_info(dname, "get_dns_info", dns_info)
        return dns_info

    def get_all_info_domains(self, dname):
        all_info = {}
        all_info["whois_text"] = self.whois_text(dname)
        all_info["whois_info"] = self.whois_info(dname)
        all_info["http_info"] = self.http_info(dname)
        all_info["dns_info"] = self.dns_info(dname)
        return all_info
