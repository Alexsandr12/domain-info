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
from sql_handler import (
    rec_method_status_mariadb,
    check_connect_mariadb,
    get_all_data_mariadb,
)
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

# TODO в методе get_response_from_method что такое  global response_dname
# TODO переделать исключения.
# TODO исправить servise на service
# TODO убрать проверку подключения бд из модулей
# TODO исправить mariadb на mysql

class ControllerGet:
    """Методы для get запросов"""

    def check_connect_db(self) -> Dict[str, str]:
        """Получение и формирование инфы о статусе подключения от баз данных

        :return:
            dict: словарь со статусом соединения и ошибкой, если она имеется
        """
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
            if servise_status.get("error"):
                servise_status["error"] = err.DB_ERROR
            else:
                servise_status["error"] = err.MARIADB_BD_ERROR

        return servise_status

    def get_all_cached_domains(self) -> Union[str, List[str]]:
        """Получение всех закэшированных доменов из redis

        :return:
            Union[str, List[str]]: сообщение о ошибке соединения с базой данных или список с доменами
        """
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

        return list(set(all_cached_domains))

    def get_info_from_mariadb(self) -> Union[str, Dict[str, list]]:
        """Получение всей информации из mariadb

        :return:
            Union[str, Dict[str:list]]: сообщение о ошибке соединения с базой данных или словарь с доменами и списками
            записей из db для домена
        """
        try:
            check_connect_mariadb()
        except MyException as err:
            return err.MARIADB_BD_ERROR

        info_from_mariadb = defaultdict(list)
        mariadb_all_data = get_all_data_mariadb()
        for mariadb_record in mariadb_all_data:
            mariadb_record = list(mariadb_record)
            dname = decode_domain(mariadb_record[1])
            datetime = mariadb_record[2]
            info_from_mariadb[dname].append(
                {
                    "id": mariadb_record[0],
                    "data": f"{datetime.year}.{datetime.month}.{datetime.day}",
                    "time": f"{datetime.hour}:{datetime.minute}:{datetime.second}",
                    "method": mariadb_record[3],
                    "status": mariadb_record[4] == 0,
                }
            )

        return info_from_mariadb


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

    def forming_response(self) -> Union[str, str, dict]:
        """Основной модуль, проверяет подключение к бд и валидацию доменов,
        если ошибки нет, собирает ответ для клиента

        :return:
            Union[str, str, dict]: ошибка подключения к базам данных/ошибка колличества передаваемых доменов/
            словарь с валидными доменами и ответом методов, и невалидными доменами
        """
        try:
            check_connect_mariadb()
            check_connect_redis()
        except MyException as err:
            logger_client.exception(
                f"Запрос клиента: метод: {self.method}, домены: {self.domains}, use_cache: {self.use_cache}. "
                f"Ответ: {err.GENERAL_ERROR}"
            )
            return err.GENERAL_ERROR

        try:
            domains = self._validation_domains()
        except MyException as err:
            logger_client.exception(
                f"Запрос клиента: метод: {self.method}, домены: {self.domains}, use_cache: {self.use_cache}. "
                f"Ответ: {err.DOMAINS_LIMIT_EXCEEDED}"
            )
            return err.DOMAINS_LIMIT_EXCEEDED

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

        :return:
            dict: словарь с валидными и не валидными доменами
        """
        validator = Validation(self.domains_puny)
        validator.checking_len_domains()
        return validator.checking_valid_domains()

    def _collecting_response_from_method(self, domains: list) -> dict:
        """Сбор ответов от методов для доменов

        :param
            domains: список доменов

        :return:
            dict: словарь с доменами и ответом методов
        """
        response = {}
        for dname in domains:
            response_dname = self._get_response_from_method(dname)
            dname = decode_domain(dname)
            response[dname] = response_dname

        return response

    def _get_response_from_method(self, dname: str) -> Union[str, dict]:
        """Ответ от методов для домена

        :param
            dname: домен

        :return:
            Union[str, dict]: ответ от методов get_whois_text, get_http_info/
            ответы от методов get_whois_info, get_dns_info, get_all_info
        """
        response_dname = self.methods_map[self.method](dname)
        self.logger_map[self.method].debug(
                f"Метод: {self.method}, домен: {dname}, use_cache: {self.use_cache}, "
                f"return метода : {response_dname}"
                )

        return response_dname

    def _get_whois_text(self, dname: str) -> str:
        """Запрос whois текста для домена из кэша или из функции

        :param
            dname: домен

        :return:
            str: ошибка функции получения whois текста/ whois текст из кэша или ответ от функции
        """
        whois_text = None
        if self.use_cache:
            whois_text = check_cache_redis(dname, "get_whois_text")
        if whois_text is None:
            try:
                whois_text = search_whois_text(dname)
            except MyException as err:
                rec_method_status_mariadb(dname, "get_whois_text", False)
                return err.GETTING_WHOIS_TEXT_ERROR
            rec_redis(dname, "get_whois_text", whois_text)
            rec_method_status_mariadb(dname, "get_whois_text", True)

        return whois_text

    def _get_whois_info(self, dname: str) -> Union[str, dict]:
        """Запрос whois информации для домена

        :param
            dname: домен

        :return:
            Union[str, dict]: ошибка получения whois текста/ словарь с пунктами whois и их значениями для домена
        """
        whois_text = self._get_whois_text(dname)
        if whois_text == MyException.GETTING_WHOIS_TEXT_ERROR:
            return whois_text
        try:
            whois_info = parsing_whois_text(whois_text)
            rec_method_status_mariadb(dname, "get_whois_info", True)
        except MyException as err:
            whois_info = err.DOMAIN_NOT_REGISTRED
            rec_method_status_mariadb(dname, "get_whois_info", False)
        return whois_info

    def _get_http_info(self, dname: str) -> str:
        """Запрос http инфо по домену в кэше, если нет то в функции

        :param
            dname: домен

        :return:
            str: http инфо из кэша или ответ от функции
        """
        http_info = None
        if self.use_cache:
            http_info = check_cache_redis(dname, "get_http_info")
        if http_info is None:
            http_info = self._forming_response_http_info(dname)
            rec_redis(dname, "get_http_info", http_info)
        self._rec_http_info_mariadb(dname, http_info)
        return http_info

    def _forming_response_http_info(self, dname: str) -> Union[str, str]:
        """Формулировка ответа от функции поиска http информации

        :param
            dname: домен

        :return:
            Union[str, str]: ответ от функции/ ошибка поиска http информации
        """
        try:
            status_code, ssl_verify = search_http_info(dname)
            return f"code: {status_code}, https: {ssl_verify}"
        except requests.exceptions.RequestException:
            return MyException.GETTING_HTTP_INFO_ERROR

    def _rec_http_info_mariadb(self, dname: str, http_info: str):
        """Запись данных в mariadb

        :param
            dname: домен
            http_info: http информация по домену
        """
        if MyException.GETTING_HTTP_INFO_ERROR in http_info:
            rec_method_status_mariadb(dname, "get_http_info", False)
        else:
            rec_method_status_mariadb(dname, "get_http_info", True)

    def _get_dns_info(self, dname: str) -> Union[str, dict]:
        """Запрос dns записей для домена из кэша или из функции

        :param
            dname:домен

        :return:
            Union[str, dict]: ошибка функции поиска dns записей для домена/
            словать с типами ресурсных записей и их значениями для доменов
        """
        dns_info = None
        if self.use_cache == "True":
            dns_info = check_dns_info(dname, "get_dns_info")
        if not dns_info:
            try:
                dns_info = search_dns_records(dname)
            except MyException as err:
                rec_method_status_mariadb(dname, "get_dns_info", False)
                return err.GETTING_DNS_INFO_ERROR
        rec_method_status_mariadb(dname, "get_dns_info", True)
        rec_dns_info(dname, "get_dns_info", dns_info)
        return dns_info

    def _get_all_info_domains(self, dname: str) -> dict:
        """Сбор информации для домена из всех post методов

        :param
            dname: домен

        :return:
            dict: словарь с методами и из ответами
        """
        all_info = {}
        all_info["whois_text"] = self._get_whois_text(dname)
        all_info["whois_info"] = self._get_whois_info(dname)
        all_info["http_info"] = self._get_http_info(dname)
        all_info["dns_info"] = self._get_dns_info(dname)
        return all_info
