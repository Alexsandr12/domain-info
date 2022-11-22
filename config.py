import os
from dotenv import load_dotenv

load_dotenv(".env")

"""web"""
INDENT = 4
ENSURE_ASCII = False

"""whois info"""
WHOIS_TIMEOUT = 10
PORT = 43
WHOIS_SERVER = "whois.reg.ru"

"""redis"""
EXPIRED_RECORD = 3600

"""http info"""
REQTIMEOUT = 5

"""dns info"""
TYPE_RECORDS = {"A", "AAAA", "NS", "TXT", "MX", "CNAME"}
PAYLOAD = 4096
DNS_TIMEOUT = 5
IP_ROOT_DNS = "193.232.128.6"

"""validation"""
LIMIT_DOMAINS = 5

"""sql"""
DSN = f"dbname={os.getenv('DATABASE')} " \
      f"user={os.getenv('USER')} " \
      f"password={os.getenv('PASSWORD')} " \
      f"host={os.getenv('HOST')}"
