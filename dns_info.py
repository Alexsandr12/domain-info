from typing import List, Dict

import dns.name
import dns.message
import dns.query
import dns.flags
import dns.resolver

from projectexception import GettingDnsInfoError
from config import TYPE_RECORDS, PAYLOAD, DNS_TIMEOUT, IP_ROOT_DNS

"""domain = 'reg.ru'
name_server = '8.8.8.8'
ADDITIONAL_RDCLASS = 65535

domain = dns.name.from_text(domain)
if not domain.is_absolute():
    domain = domain.concatenate(dns.name.root)

request = dns.message.make_query(domain, dns.rdatatype.ANY)
request.flags |= dns.flags.AD
request.find_rrset(request.additional, dns.name.root, ADDITIONAL_RDCLASS,
                   dns.rdatatype.OPT, create=True, force_unique=True)
response = dns.query.udp(request, name_server)


print(response.answer)
print(response.additional)
print(response.authority)

answers = dns.resolver.query("dnspython.org")
for rdata in answers.response.answer:
    print(rdata[0])"""

# TODO посмотреть с Женьком принты, как упростить или сделать понятнее получение данных из rrset


def search_dns_records(dname: str) -> Dict[str, list]:
    """Поиск ресурсных записей для домена с ответственного DNS-сервера

    Args:
        dname: домен
    Return:
        Dict[str, list]: словать с типами записей и их значениями
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
    if records_of_dname["NS"]:
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
    for ip_adresses_of_dns in rrset_ip_of_dns.response.answer:
        return str(ip_adresses_of_dns[0])


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


def parsing_values_record(response: str) -> List[str]:
    """Парсинг значений ресурсной записи

    Args:
        response: значения ресурсной записи
    Return:
        List[str]: список значений ресурсной записи
    """
    values_record = []
    if response.answer:
        # TODO вынести с отдельну переменную response.answer[0]
        for answer in response.answer[0]:
            answer = str(answer).strip('"')
            values_record.append(answer)
    return values_record
