import re
from typing import Dict, List

from config import LIMIT_DOMAINS
from exceptions import DomainsLimitExceeded


PATTERN = re.compile(r"^[a-z\d]{1,1}[a-z\d-]{,61}[a-z\d]{1,1}\.{1,1}(ru|(xn--p1ai))$")


class Validation:
    """Валидация и проверка колличества доменом"""

    def __init__(self, domains: List[str]):
        """
        Args:
            domains: список доменов
        """
        self.domains = domains

    def checking_len_domains(self) -> None:
        """Проверка количества доменов"""
        if len(self.domains) > LIMIT_DOMAINS:
            raise DomainsLimitExceeded

    def checking_valid_domains(self) -> Dict[str, list]:
        """Валидация доменов

        Return:
            Dict[str, list]: словарь валидными и не валидными доменами
        """
        domains = {"domains_valid": [], "domains_not_valid": []}
        for dname in self.domains:
            dname = dname.lower()
            if PATTERN.search(dname):
                domains["domains_valid"].append(dname)
            else:
                domains["domains_not_valid"].append(dname)

        return domains
