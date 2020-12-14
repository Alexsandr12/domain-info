import logging


logging.basicConfig(level=logging.DEBUG)
logger_expenses = logging.getLogger("controller")
client_log = logging.FileHandler("client_log.log")
# my_handler.setLevel(logging.DEBUG)
my_format = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
client_log.setFormatter(my_format)
# logger_db.addHandler(my_handler)
logger_expenses.addHandler(client_log)
# logger_db.setLevel(logging.DEBUG)
logger_expenses.setLevel(logging.DEBUG)
