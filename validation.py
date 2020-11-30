from config import LIMIT_DOMAINS
from utilits import MyException

# TODO доделать валидацию, проверка всех допустимых символов


class Validation:
    def __init__(self, domains):
        self.domains = domains

    def checking_len_domains(self):
        if len(self.domains) > LIMIT_DOMAINS:
            raise MyException

    def checking_correct_domains(self):
        domains = {"domains_valid": [], "domains_not_valid": []}
        for dname in self.domains:
            if ".ru" in dname or ".xn--p1ai" in dname:
                domains["domains_valid"].append(dname)
            else:
                domains["domains_not_valid"].append(dname)
        return domains
