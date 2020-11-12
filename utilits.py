import idna


def encoding_domain(dname):
    dname = dname.encode("idna").decode("utf-8")
    return dname


def decode_domain(dname):
    dname = idna.decode(dname)
    return dname


