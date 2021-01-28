from config import LIMIT_DOMAINS


class GettingDnsInfoError(Exception):
    TEXT_MESSAGE = "GETTING_DNS_INFO_ERROR"


class GettingHttpInfoError(Exception):
    TEXT_MESSAGE = "GETTING_HTTP_INFO_ERROR"


class DomainsNotRegistred(Exception):
    TEXT_MESSAGE = "DOMAIN_NOT_REGISTRED"


class DomainsLimitExceeded(Exception):
    TEXT_MESSAGE = f"DOMAINS_LIMIT_EXCEEDED: {LIMIT_DOMAINS}"


class GettingWhoisTextError(Exception):
    TEXT_MESSAGE = "GETTING_WHOIS_TEXT_ERROR"


class MySqlError(Exception):
    TEXT_MESSAGE = "MARIADB_BD_CONNECT_ERROR"


class RedisError(Exception):
    TEXT_MESSAGE = "REDIS_CONNECT_ERROR"


class DbError(Exception):
    TEXT_MESSAGE = "DB_CONNECT_ERROR"


class GeneralError(Exception):
    TEXT_MESSAGE = "GENERAL_ERROR"
