import requests
from typing import Dict, List, Union
from collections import defaultdict

from whois_info import search_whois_text, parsing_whois_text
from http_info import search_http_info
from dns_info import search_dns_records
from redis_handler import (
    check_cache_redis,
    rec_redis,
    check_dns_info,
    rec_dns_info,
    check_connect_redis,
    get_all_key,
)
from sql_handler import rec_method_status_sql, check_connect_sql, get_all_data_sql
from utils import encoding_domains, decode_domain
from exceptions import (
    GeneralError,
    DbError,
    RedisError,
    MySqlError,
    GettingWhoisTextError,
    DomainsLimitExceeded,
    DomainsNotRegistred,
    GettingHttpInfoError,
    GettingDnsInfoError,
)
from validation import Validation
from logger import (
    logger_client,
    logger_get_all_info,
    logger_get_dns_info,
    logger_get_http_info,
    logger_get_whois_info,
    logger_get_whois_text,
)


class ControllerGet:
    """Методы для get запросов."""

    @staticmethod
    def check_connect_db() -> Dict[str, str]:
        """Получение и формирование инфы о статусе подключения к базам данных.

        Return:
            dict: словарь со статусом соединения и ошибкой, если она имеется.
        """
        service_status = {"status": "successful"}

        try:
            check_connect_redis()
        except RedisError as err:
            service_status["status"] = "error"
            service_status["error"] = err.TEXT_MESSAGE

        try:
            check_connect_sql()
        except MySqlError as err:
            service_status["status"] = "error"
            if service_status.get("error"):
                service_status["error"] = DbError.TEXT_MESSAGE
            else:
                service_status["error"] = err.TEXT_MESSAGE

        return service_status

    @staticmethod
    def get_all_cached_domains() -> Union[str, List[str]]:
        """Получение всех закэшированных доменов из redis.

        Return:
            Union[str, List[str]]: сообщение о ошибке соединения с базой данных или список с доменами.
        """
        all_cached_domains = []
        try:
            all_key_redis = get_all_key()
        except RedisError as err:
            return err.TEXT_MESSAGE

        for key in all_key_redis:
            method, dname_puny = key.split(":")
            dname = decode_domain(dname_puny)
            all_cached_domains.append(dname)

        return list(set(all_cached_domains))

    @staticmethod
    def get_info_from_sql() -> Union[str, Dict[str, list]]:
        """Получение всей информации из sql

        Return:
            Union[str, Dict[str:list]]: сообщение о ошибке соединения с базой данных или словарь с доменами и списками
            записей из sql для домена
        """
        info_from_sql = defaultdict(list)
        try:
            sql_all_data = get_all_data_sql()
        except MySqlError as err:
            return err.TEXT_MESSAGE

        for sql_record in sql_all_data:
            sql_record = list(sql_record)
            dname = decode_domain(sql_record[1])
            datetime = sql_record[2]
            info_from_sql[dname].append(
                {
                    "id": sql_record[0],
                    "data": f"{datetime.year}.{datetime.month}.{datetime.day}",
                    "time": f"{datetime.hour}:{datetime.minute}:{datetime.second}",
                    "method": sql_record[3],
                    "status": sql_record[4] != 0,
                }
            )

        return info_from_sql


class ControllerPost:
    """Методы для пост запросов"""

    def __init__(self, domains: list, method: str, use_cache: str):
        """
        Args:
            domains: список доменов
            method: метод
            use_cache: True или False, нужна ли проверка в данных в кэше
        """
        self.domains = domains
        self.domains_puny = encoding_domains(domains)
        self.method = method
        self.use_cache = use_cache == "True"
        self.methods_map = {
            "get_whois_text": self._get_whois_text,
            "get_whois_info": self._get_whois_info,
            "get_http_info": self._get_http_info,
            "get_dns_info": self._get_dns_info,
            "get_all_info": self._get_all_info_domains,
        }
        self.logger_map = {
            "get_whois_text": logger_get_whois_text,
            "get_whois_info": logger_get_whois_info,
            "get_http_info": logger_get_http_info,
            "get_dns_info": logger_get_dns_info,
            "get_all_info": logger_get_all_info,
        }

    def forming_response(self) -> Union[str, dict]:
        """Основной модуль, проверка подключения к бд, валидацию доменов,
         сбор инфы для доменов из методов

        Return:
            Union[str, dict]: ошибка подключения к базам данных/ошибка колличества передаваемых доменов/
            словарь с валидными доменами и ответом методов, и невалидными доменами
        """
        try:
            check_connect_sql()
            check_connect_redis()
        except GeneralError as err:
            logger_client.exception(
                f"Запрос клиента: метод: {self.method}, домены: {self.domains}, use_cache: {self.use_cache}. "
                f"Ответ: {err.TEXT_MESSAGE}"
            )
            return err.TEXT_MESSAGE

        try:
            domains = self._validation_domains()
        except DomainsLimitExceeded as err:
            logger_client.exception(
                f"Запрос клиента: метод: {self.method}, домены: {self.domains}, use_cache: {self.use_cache}. "
                f"Ответ: {err.TEXT_MESSAGE}"
            )
            return err.TEXT_MESSAGE

        response = self._collecting_response_from_method(domains["domains_valid"])
        if domains["domains_not_valid"]:
            response["Invalid domain names"] = domains["domains_not_valid"]
        logger_client.debug(
            f"Запрос клиента: метод: {self.method}, домены: {self.domains}, use_cache: {self.use_cache}. "
            f"Ответ: {response}"
        )

        return response

    def _validation_domains(self) -> Dict[str, list]:
        """Вызов методов для проверки валидации доменов

        Return:
            dict: словарь с валидными и не валидными доменами
        """
        validator = Validation(self.domains_puny)
        validator.checking_len_domains()
        return validator.checking_valid_domains()

    def _collecting_response_from_method(self, domains: list) -> dict:
        """Сбор ответов от методов для доменов

        Args:
            domains: список доменов

        Return:
            dict: словарь с доменами и ответом методов
        """
        response = {}
        for dname in domains:
            response_dname = self._get_response_from_method(dname)
            dname = decode_domain(dname)
            response[dname] = response_dname

        return response

    def _get_response_from_method(self, dname: str) -> Union[str, dict]:
        """Получение инфы из методов для домена

        Args:
            dname: домен

        Return:
            Union[str, dict]: ответ от методов
        """
        response_dname = self.methods_map[self.method](dname)
        self.logger_map[self.method].debug(
            f"Метод: {self.method}, домен: {dname}, use_cache: {self.use_cache}, "
            f"return метода : {response_dname}"
        )

        return response_dname

    def _get_whois_text(self, dname: str) -> str:
        """Получение whois text для домена

        Args:
            dname: домен

        Return:
            str: ошибка получения whois текста/ whois text домена
        """
        whois_text = None
        if self.use_cache:
            whois_text = check_cache_redis(dname, "get_whois_text")
        if whois_text is None:
            try:
                whois_text = search_whois_text(dname)
            except GettingWhoisTextError as err:
                rec_method_status_sql(dname, "get_whois_text", False)
                return err.TEXT_MESSAGE
            rec_redis(dname, "get_whois_text", whois_text)
            rec_method_status_sql(dname, "get_whois_text", True)

        return whois_text

    def _get_whois_info(self, dname: str) -> Union[str, dict]:
        """Получение whois info для домена

        Args:
            dname: домен

        Return:
            Union[str, dict]: ошибка получения whois текста/ словарь с пунктами whois и их значениями для домена
        """
        whois_text = self._get_whois_text(dname)
        if whois_text == GettingWhoisTextError.TEXT_MESSAGE:
            return whois_text
        try:
            whois_info = parsing_whois_text(whois_text)
            rec_method_status_sql(dname, "get_whois_info", True)
            return whois_info
        except DomainsNotRegistred as err:
            rec_method_status_sql(dname, "get_whois_info", False)
            return err.TEXT_MESSAGE

    def _get_http_info(self, dname: str) -> str:
        """Получение http инфо по домену

        Args:
            dname: домен

        Return:
            str: ошибка получения http инфо/ http инфо домена
        """
        http_info = None
        if self.use_cache:
            http_info = check_cache_redis(dname, "get_http_info")

        if http_info is None:
            try:
                status_code, ssl_verify = search_http_info(dname)
                http_info = f"code: {status_code}, https: {ssl_verify}"
            except requests.exceptions.RequestException:
                http_info = GettingHttpInfoError.TEXT_MESSAGE
            rec_redis(dname, "get_http_info", http_info)
        self._rec_http_info_sql(dname, http_info)

        return http_info

    @staticmethod
    def _rec_http_info_sql(dname: str, http_info: str):
        """Запись данных в sql

        Args:
            dname: домен
            http_info: http информация по домену
        """
        if GettingHttpInfoError.TEXT_MESSAGE == http_info:
            rec_method_status_sql(dname, "get_http_info", False)
        else:
            rec_method_status_sql(dname, "get_http_info", True)

    def _get_dns_info(self, dname: str) -> Union[str, dict]:
        """Получение dns info для домена

        Args:
            dname:домен

        Return:
            Union[str, dict]: ошибка получения dns info/
            словать с типами ресурсных записей и их значениями для домена
        """
        dns_info = None
        if self.use_cache == "True":
            dns_info = check_dns_info(dname, "get_dns_info")
        if not dns_info:
            try:
                dns_info = search_dns_records(dname)
            except GettingDnsInfoError as err:
                rec_method_status_sql(dname, "get_dns_info", False)
                return err.TEXT_MESSAGE
        rec_method_status_sql(dname, "get_dns_info", True)
        rec_dns_info(dname, "get_dns_info", dns_info)
        return dns_info

    def _get_all_info_domains(self, dname: str) -> dict:
        """Сбор информации для домена из всех post методов

        Args
            dname: домен

        Return:
            dict: словарь с названием метода и его ответом
        """
        return {
            "whois_text": self._get_whois_text(dname),
            "whois_info": self._get_whois_info(dname),
            "http_info": self._get_http_info(dname),
            "dns_info": self._get_dns_info(dname),
        }
