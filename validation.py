from config import LIMIT_DOMAINS
from utilits import MyException
import re


# TODO доделать валидацию, проверка всех допустимых символов


class Validation:
    def __init__(self, domains):
        self.domains = domains

    def checking_len_domains(self):
        if len(self.domains) > LIMIT_DOMAINS:
            raise MyException

    def checking_valid_domains(self):
        domains = {"domains_valid": [], "domains_not_valid": []}
        for dname in self.domains:
            dname = dname.lower()
            if re.search(r'^[a-z\d]{1,1}[a-z\d-]{,61}[a-z\d]{1,1}\.{1,1}(ru|(xn--p1ai))$', dname):
                domains["domains_valid"].append(dname)
            else:
                domains["domains_not_valid"].append(dname)
        return domains

