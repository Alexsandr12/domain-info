import dns.name
import dns.message
import dns.query
import dns.flags
import dns.resolver


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

"""

"""answers = dns.resolver.query("dnspython.org")
for rdata in answers.response.answer:
    print(rdata[0])"""

# TODO посмотреть с Женьком принты, как упростить или сделать понятнее получение данных из rrset
# TODO сделать формирование ответа в контроллере, подумать как записать в redis словать с данными
# TODO ДОБАВИЛ dname = dns.name.from_text(dname, idna_codec=None), возможно не нужно, проверить записи отдельно для idn


def get_ip_of_dns_domain(dname):
    dname = dns.name.from_text(dname, idna_codec='IDNA2008Codec')
    query = dns.message.make_query(dname, dns.rdatatype.from_text('ns'), payload=4096)
    response = dns.query.udp(query, '193.232.128.6', one_rr_per_rrset=True, timeout=10)
    rrset_with_ip = response.additional[0]
    ip_of_dns = str(rrset_with_ip[0])
    """print(type(response))
    print(type(rrset_with_ip))
    print(type(rrset_with_ip[0]))"""
    return ip_of_dns


def _make_dns_query(dname: str):
    records_of_dname = {}
    type_of_records = ['A', 'AAAA', 'NS', 'TXT', 'MX', 'CNAME']
    ip_nserver = get_ip_of_dns_domain(dname)
    for type_record in type_of_records:
        dname = dns.name.from_text(dname, idna_codec='IDNA2008Codec')
        query = dns.message.make_query(dname, dns.rdatatype.from_text(type_record), payload=4096)
        response = dns.query.udp(query, ip_nserver, timeout=3)
        values_record = forming_data_from_response(response)
        records_of_dname[type_record] = values_record
    return records_of_dname


def forming_data_from_response(response):
    values_record = []
    if not response.answer:
        values_record.append(None)
    else:
        for answer in response.answer[0]:
            answer = str(answer).strip('"')
            values_record.append(answer)
    return values_record


print(_make_dns_query('xn--80ax.xn--p1ai'))

