import requests
from typing import Dict, List, Union

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

class ControllerGet:
    """ Методы для get запросов"""

    def check_connect_DB(self) -> Dict[str, str]:
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
            if servise_status.get("error") is None:
                servise_status["error"] = err.MARIADB_BD_ERROR
            else:
                servise_status["error"] = err.DB_ERROR
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
        all_cached_domains = set(all_cached_domains)
        return list(all_cached_domains)

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
        info_from_mariadb = {}
        mariadb_all_data = get_all_data_mariadb()
        for mariadb_record in mariadb_all_data:
            mariadb_record = list(mariadb_record)
            val_success_field_record = self.analysis_success_field_record(
                mariadb_record[4]
            )
            dname = decode_domain(mariadb_record[1])
            if info_from_mariadb.get(dname) is None:
                info_from_mariadb[dname] = []
            info_from_mariadb[dname].append(
                {
                    "id": mariadb_record[0],
                    "data": f"{mariadb_record[2].year}.{mariadb_record[2].month}.{mariadb_record[2].day}",
                    "time": f"{mariadb_record[2].hour}:{mariadb_record[2].minute}:{mariadb_record[2].second}",
                    "method": mariadb_record[3],
                    "status": val_success_field_record,
                }
            )
        return info_from_mariadb

    def analysis_success_field_record(self, success_field: int) -> bool:
        """Проверка значения статуса метода

        :param
            success_field: 0 или 1

        :return:
            bool: статус выполнения метода
        """
        if success_field == 0:
            return False
        else:
            return True


class ControllerPost:
    """Методы для пост запросов"""

    def __init__(self, domains: list, method: str, use_cache: str):
        """
        Args:
            domains: список доменов
            method: метод
            use_cache: True или False, нужна ли проверка в данных в кэше
        Attributes:
            domains: список доменов
            domains_puny: список доменов в кодировке punycode
            method: метод
            use_cache: True или False, нужна ли проверка в данных в кэше
        """
        self.domains = domains
        self.domains_puny = encoding_domains(domains)
        self.method = method
        self.use_cache = use_cache

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
            domains = self.validation_domains()
        except MyException as err:
            logger_client.exception(
                f"Запрос клиента: метод: {self.method}, домены: {self.domains}, use_cache: {self.use_cache}. "
                f"Ответ: {err.DOMAINS_LIMIT_EXCEEDED}"
            )
            return err.DOMAINS_LIMIT_EXCEEDED
        response = self.collecting_response_from_method(domains["domains_valid"])
        if domains["domains_not_valid"]:
            response["Invalid domain names"] = domains["domains_not_valid"]
        logger_client.debug(
            f"Запрос клиента: метод: {self.method}, домены: {self.domains}, use_cache: {self.use_cache}. "
            f"Ответ: {response}"
        )
        return response

    def validation_domains(self) -> Dict[str, list]:
        """Вызов методов для проверки валидации доменов

        :return:
            dict: словарь с валидными и не валидными доменами
        """
        Validation(self.domains_puny).checking_len_domains()
        return Validation(self.domains_puny).checking_valid_domains()

    def collecting_response_from_method(self, domains: list) -> dict:
        """Сбор ответов от методов для доменов

        :param
            domains: список доменов

        :return:
            dict: словарь с доменами и ответом методов
        """
        response = {}
        for dname in domains:
            response_dname = self.get_response_from_method(dname)
            dname = decode_domain(dname)
            response[dname] = response_dname
        return response

    def get_response_from_method(self, dname: str) -> Union[str, dict]:
        """Ответ от методов для домена

        :param
            dname: домен

        :return:
            Union[str, dict]: ответ от методов get_whois_text, get_http_info/
            ответы от методов get_whois_info, get_dns_info, get_all_info
        """
        global response_dname
        if self.method == "get_whois_text":
            response_dname = self.get_whois_text(dname)
            logger_get_whois_text.debug(
                f"Метод: {self.method}, домен: {dname}, use_cache: {self.use_cache}, "
                f"return метода : {response_dname}"
            )
        elif self.method == "get_whois_info":
            response_dname = self.get_whois_info(dname)
            logger_get_whois_info.debug(
                f"Метод: {self.method}, домен: {dname}, use_cache: {self.use_cache}, "
                f"return метода : {response_dname}"
            )
        elif self.method == "get_http_info":
            response_dname = self.get_http_info(dname)
            logger_get_http_info.debug(
                f"Метод: {self.method}, домен: {dname}, use_cache: {self.use_cache}, "
                f"return метода : {response_dname}"
            )
        elif self.method == "get_dns_info":
            response_dname = self.get_dns_info(dname)
            logger_get_dns_info.debug(
                f"Метод: {self.method}, домен: {dname}, use_cache: {self.use_cache}, "
                f"return метода : {response_dname}"
            )
        elif self.method == "get_all_info":
            response_dname = self.get_all_info_domains(dname)
            logger_get_all_info.debug(
                f"Метод: {self.method}, домен: {dname}, use_cache: {self.use_cache}, "
                f"return метода : {response_dname}"
            )
        # rec_logger_method(self.method, dname, self.use_cache, response)
        return response_dname

    def get_whois_text(self, dname: str) -> Union[str, str]:
        """Запрос whois текста для домена из кэша или из функции

        :param
            dname: домен

        :return:
            Union[str, str]: ошибка функции получения whois текста/ whois текст из кэша или ответ от функции
        """
        whois_text = None
        if self.use_cache == "True":
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

    def get_whois_info(self, dname: str) -> Union[str, dict]:
        """Запрос whois информации для домена

        :param
            dname: домен

        :return:
            Union[str, dict]: ошибка получения whois текста/ словарь с пунктами whois и их значениями для домена
        """
        whois_text = self.get_whois_text(dname)
        if whois_text == MyException.GETTING_WHOIS_TEXT_ERROR:
            return whois_text
        try:
            whois_info = parsing_whois_text(whois_text)
            rec_method_status_mariadb(dname, "get_whois_info", True)
        except MyException as err:
            whois_info = err.DOMAIN_NOT_REGISTRED
            rec_method_status_mariadb(dname, "get_whois_info", False)
        return whois_info

    def get_http_info(self, dname: str) -> str:
        """Запрос http инфо по домену в кэше, если нет то в функции

        :param
            dname: домен

        :return:
            str: http инфо из кэша или ответ от функции
        """
        http_info = None
        if self.use_cache == "True":
            http_info = check_cache_redis(dname, "get_http_info")
        if http_info is None:
            http_info = self.forming_response_http_info(dname)
            rec_redis(dname, "get_http_info", http_info)
        self.rec_http_info_mariadb(dname, http_info)
        return http_info

    def forming_response_http_info(self, dname: str) -> Union[str, str]:
        """Формулировка ответа от функции поиска http информации

        :param
            dname: домен

        :return:
            Union[str, str]: ответ от функции/ ошибка поиска http информации
        """
        try:
            http_info = search_http_info(dname)
            return f"code: {http_info[0]}, https: {http_info[1]}"
        except requests.exceptions.RequestException:
            return MyException.GETTING_HTTP_INFO_ERROR

    def rec_http_info_mariadb(self, dname: str, http_info: str):
        """Запись данных в mariadb

        :param
            dname: домен
            http_info: http информация по домену
        """
        if MyException.GETTING_HTTP_INFO_ERROR in http_info:
            rec_method_status_mariadb(dname, "get_http_info", False)
        else:
            rec_method_status_mariadb(dname, "get_http_info", True)

    def get_dns_info(self, dname: str) -> Union[str, dict]:
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

    def get_all_info_domains(self, dname: str) -> dict:
        """Сбор информации для домена из всех post методов

        :param
            dname: домен

        :return:
            dict: словарь с методами и из ответами
        """
        all_info = {}
        all_info["whois_text"] = self.get_whois_text(dname)
        all_info["whois_info"] = self.get_whois_info(dname)
        all_info["http_info"] = self.get_http_info(dname)
        all_info["dns_info"] = self.get_dns_info(dname)
        return all_info
