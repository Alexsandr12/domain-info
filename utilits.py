import idna


def encoding_domains(domains):
    encode_domains = []
    for dname in domains:
        dname = dname.encode("idna").decode("utf-8")
        encode_domains.append(dname)
    return encode_domains


def decode_domain(dname):
    dname = idna.decode(dname)
    return dname
