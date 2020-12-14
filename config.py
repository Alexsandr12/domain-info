"""web.py"""
INDENT = 4
ENSURE_ASCII = False

"""whois_info.py"""
WHOIS_TIMEOUT = 3
PORT = 43
WHOIS_SERVER = "whois.tcinet.ru"

"""redis_handler.py"""
EXPIRED_RECORD = 3600

"""http_info.py"""
REQTIMEOUT = 5

"""dns_info.py"""
TYPE_RECORDS = ["A", "AAAA", "NS", "TXT", "MX", "CNAME"]
PAYLOAD = 4096
DNS_TIMEOUT = 5
IP_ROOT_DNS = "193.232.128.6"

"""validation.py"""
LIMIT_DOMAINS = 5

"""sql_handler.py"""
HOST = "localhost"
USER = "alexandr"
PASSWORD = "1"
DATABASE = "mysqltest"
