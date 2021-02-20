from typing import List, Dict

import dns.name
import dns.message
import dns.query
import dns.resolver

from exceptions import GettingDnsInfoError
from config import TYPE_RECORDS, PAYLOAD, DNS_TIMEOUT, IP_ROOT_DNS


def search_dns_records(dname: str) -> Dict[str, list]:
    """Получение ресурсных записей для домена с ответственного DNS-сервера

    Args:
        dname: домен
    Return:
        Dict[str, list]: словарь с типами записей и их значениями
    """
    records_of_dname = {}
    ip_nserver = get_ip_of_dns(dname)

    for type_record in TYPE_RECORDS:
        query = dns.message.make_query(
            dname, dns.rdatatype.from_text(type_record), payload=PAYLOAD
        )
        response = dns.query.udp(query, ip_nserver, timeout=DNS_TIMEOUT)
        values_record = parsing_values_record(response)
        records_of_dname[type_record] = values_record

    if not records_of_dname["NS"]:
        raise GettingDnsInfoError

    return records_of_dname


def get_ip_of_dns(dname: str) -> str:
    """Получение IP адреса DNS сервера домена

    Args:
        dname: домен

    Return:
        str: ip адрес DNS сервера домена
    """
    dns_of_dname = get_dns_of_dname(dname)

    rrset_ip_of_dns = dns.resolver.resolve(dns_of_dname)
    ip_addresses_of_dns = rrset_ip_of_dns.response.answer[0]

    return str(ip_addresses_of_dns[0])


def get_dns_of_dname(dname: str) -> str:
    """Получение DNS-сервера домена c ответственного dns зоны

    Args:
        dname: домен
    Return:
        str: DNS-сервер домена
    """
    query = dns.message.make_query(
        dname, dns.rdatatype.from_text("ns"), payload=PAYLOAD
    )
    response = dns.query.udp(
        query, IP_ROOT_DNS, one_rr_per_rrset=True, timeout=DNS_TIMEOUT
    )
    rrset_ns = response.authority[0]
    if "IN NS" not in str(rrset_ns):
        raise GettingDnsInfoError
    dns_of_dname = str(rrset_ns[0])

    return dns_of_dname


def parsing_values_record(response: dns.message.QueryMessage) -> List[str]:
    """Парсинг значений ресурсной записи

    Args:
        response: значения ресурсной записи
    Return:
        List[str]: список значений ресурсной записи
    """
    valid_values_record = []
    if response.answer:
        values_record = response.answer[0]
        for value in values_record:
            valid_value = str(value).strip('"')
            valid_values_record.append(valid_value)

    return valid_values_record
