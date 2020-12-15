import logging

# TODO почему функция дублирует логи

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

logger_method = logging.getLogger(f"logger_method")

def rec_logger_method(method, dname, use_cache, response):
    method_handler = logging.FileHandler(f"logger_{method}.log")
    my_format = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    method_handler.setFormatter(my_format)
    logger_method.addHandler(method_handler)
    logger_method.setLevel(logging.DEBUG)
    logger_method.debug(
        f"Метод: {method}, домен: {dname}, use_cache: {use_cache}, return метода : {response}"
    )
