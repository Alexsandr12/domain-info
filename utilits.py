import idna


def encoding_domain(dname):
    dname = dname.encode("idna").decode("utf-8")
    return dname


def decode_domain(dname):
    dname = idna.decode(dname)
    return dname


class MyException(Exception):
    GETTING_DNS_INFO_ERROR = "GETTING_DNS_INFO_ERROR"
    GETTING_HTTP_INFO_ERROR = "GETTING_HTTP_INFO_ERROR"
    DOMAIN_NOT_REGISTRED = "DOMAIN_NOT_REGISTRED"
