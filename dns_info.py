import dns.name
import dns.message
import dns.query
import dns.flags
import dns.resolver
from utilits import MyException
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
# TODO подумать как записать в redis словать с данными


def get_dns_of_dname(dname):
    query = dns.message.make_query(
        dname, dns.rdatatype.from_text("ns"), payload=PAYLOAD
    )
    response = dns.query.udp(
        query, IP_ROOT_DNS, one_rr_per_rrset=True, timeout=DNS_TIMEOUT
    )
    rrset_ns = response.authority[0]
    if "IN NS" not in str(rrset_ns):
        raise MyException
    dns_of_dname = str(rrset_ns[0])
    return dns_of_dname


def get_ip_of_dns(dname):
    dns_of_dname = get_dns_of_dname(dname)
    answers = dns.resolver.resolve(dns_of_dname)
    for rdata in answers.response.answer:
        return str(rdata[0])


def get_dns_records(dname: str):
    records_of_dname = {}
    ip_nserver = get_ip_of_dns(dname)
    for type_record in TYPE_RECORDS:
        query = dns.message.make_query(
            dname, dns.rdatatype.from_text(type_record), payload=PAYLOAD
        )
        response = dns.query.udp(query, ip_nserver, timeout=DNS_TIMEOUT)
        values_record = get_records_from_response(response)
        records_of_dname[type_record] = values_record
    if records_of_dname["NS"] is None:
        raise MyException
    return records_of_dname


def get_records_from_response(response):
    values_record = []
    if not response.answer:
        values_record = None
    else:
        for answer in response.answer[0]:
            answer = str(answer).strip('"')
            values_record.append(answer)
    return values_record
