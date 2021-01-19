from config import LIMIT_DOMAINS
from projectexception import DomainsLimitExceeded
import re
from typing import Dict


# TODO доделать валидацию, проверка всех допустимых символов


class Validation:
    """Валидация и проверка колличества доменом"""

    def __init__(self, domains: list):
        """
        Args:
            domains: список доменов
        Attributes:
            domains: список доменов
        """
        self.domains = domains

    def checking_len_domains(self):
        """Проверка количества доменов"""
        if len(self.domains) > LIMIT_DOMAINS:
            raise DomainsLimitExceeded

    def checking_valid_domains(self) -> Dict[str, list]:
        """Разделение валидных и не валидных доменов

        :return:
            Dict[str, list]: словарь валидными и не валидными доменами
        """
        domains = {"domains_valid": [], "domains_not_valid": []}
        for dname in self.domains:
            dname = dname.lower()
            if re.search(
                r"^[a-z\d]{1,1}[a-z\d-]{,61}[a-z\d]{1,1}\.{1,1}(ru|(xn--p1ai))$", dname
            ):
                domains["domains_valid"].append(dname)
            else:
                domains["domains_not_valid"].append(dname)
        return domains
