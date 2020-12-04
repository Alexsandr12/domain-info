import idna
from config import LIMIT_DOMAINS


def encoding_domains(domains):
    encode_domains = []
    for dname in domains:
        dname = dname.encode("idna").decode("utf-8")
        encode_domains.append(dname)
    return encode_domains


def decode_domain(dname):
    dname = idna.decode(dname)
    return dname


class MyException(Exception):
    GETTING_DNS_INFO_ERROR = "GETTING_DNS_INFO_ERROR"
    GETTING_HTTP_INFO_ERROR = "GETTING_HTTP_INFO_ERROR"
    DOMAIN_NOT_REGISTRED = "DOMAIN_NOT_REGISTRED"
    DOMAINS_LIMIT_EXCEEDED = f"DOMAINS_LIMIT_EXCEEDED: {LIMIT_DOMAINS}"
    GETTING_WHOIS_TEXT_ERROR = "GETTING_WHOIS_TEXT_ERROR"
