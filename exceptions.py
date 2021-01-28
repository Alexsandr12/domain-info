from config import LIMIT_DOMAINS


class GettingDnsInfoError(Exception):
    text_err = "GETTING_DNS_INFO_ERROR"


class GettingHttpInfoError(Exception):
    text_err = "GETTING_HTTP_INFO_ERROR"


class DomainsNotRegistred(Exception):
    text_err = "DOMAIN_NOT_REGISTRED"


class DomainsLimitExceeded(Exception):
    text_err = f"DOMAINS_LIMIT_EXCEEDED: {LIMIT_DOMAINS}"


class GettingWhoisTextError(Exception):
    text_err = "GETTING_WHOIS_TEXT_ERROR"


class BdErrors(Exception):
    MYSQL_ERROR = "MARIADB_BD_CONNECT_ERROR"
    REDIS_ERROR = "REDIS_CONNECT_ERROR"
    DB_ERROR = "DB_CONNECT_ERROR"


class GeneralError(Exception):
    text_err = "GENERAL_ERROR"
