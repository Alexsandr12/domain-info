import logging

logging.basicConfig(level=logging.DEBUG)
logger_client = logging.getLogger("logger_client")
client_handler = logging.FileHandler("client_log.log")
# my_handler.setLevel(logging.DEBUG)
my_format = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
client_handler.setFormatter(my_format)
# logger_db.addHandler(my_handler)
logger_client.addHandler(client_handler)
# logger_db.setLevel(logging.DEBUG)
logger_client.setLevel(logging.DEBUG)

logger_get_all_info = logging.getLogger("logger_method")
get_all_info_handler = logging.FileHandler("logger_get_all_info.log")
get_all_info_handler.setFormatter(my_format)
logger_get_all_info.addHandler(get_all_info_handler)
logger_get_all_info.setLevel(logging.DEBUG)

logger_get_dns_info = logging.getLogger("logger_method")
get_dns_info_handler = logging.FileHandler("logger_get_dns_info.log")
get_dns_info_handler.setFormatter(my_format)
logger_get_dns_info.addHandler(get_dns_info_handler)
logger_get_dns_info.setLevel(logging.DEBUG)

logger_get_http_info = logging.getLogger("logger_method")
get_http_info_handler = logging.FileHandler("logger_get_http_info.log")
get_http_info_handler.setFormatter(my_format)
logger_get_http_info.addHandler(get_http_info_handler)
logger_get_http_info.setLevel(logging.DEBUG)

logger_get_whois_info = logging.getLogger("logger_method")
get_whois_info_handler = logging.FileHandler("logger_get_whois_info.log")
get_whois_info_handler.setFormatter(my_format)
logger_get_whois_info.addHandler(get_whois_info_handler)
logger_get_whois_info.setLevel(logging.DEBUG)

logger_get_whois_text = logging.getLogger("logger_method")
get_whois_text_handler = logging.FileHandler("logger_get_whois_text.log")
get_whois_text_handler.setFormatter(my_format)
logger_get_whois_text.addHandler(get_whois_text_handler)
logger_get_whois_text.setLevel(logging.DEBUG)

"""def rec_logger_method(method, dname, use_cache, response):
    method_handler = logging.FileHandler(f"logger_{method}.log")
    my_format = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    method_handler.setFormatter(my_format)
    logger_method.addHandler(method_handler)
    logger_method.setLevel(logging.DEBUG)
    logger_method.debug(
        f"Метод: {method}, домен: {dname}, use_cache: {use_cache}, return метода : {response}"
    )"""
