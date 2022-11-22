import logging


class MyLogger:
    """Класс для создания логгеров"""
    MY_FORMAT = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    def create_logger(self, name: str) -> logging.Logger:
        """Создает логгер

        Args:
            name: Имя логгера
        Returns:
            logging.Logger: созданный логгер
        """
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(f"{name}.log")
        handler.setFormatter(self.MY_FORMAT)
        logger.addHandler(handler)

        return logger


log = MyLogger()

logger_client = log.create_logger("logger_client")
logger_get_all_info = log.create_logger("logger_get_all_info")
logger_get_dns_info = log.create_logger("logger_get_dns_info")
logger_get_http_info = log.create_logger("logger_get_http_info")
logger_get_whois_info = log.create_logger("logger_get_whois_info")
logger_get_whois_text = log.create_logger("logger_get_whois_text")
