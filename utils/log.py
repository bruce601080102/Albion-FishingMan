import logging
import logging.config


class LogHandler:
    def __init__(self, log_level='INFO', service='CardTesting'):
        self.log_level = log_level
        self.service = service
        self.set_logging()

    def set_logging(self):
        logging.config.dictConfig(config=self._get_logging_config())

    def _get_logging_config(self):
        return {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "normal": {  # the name of formatter
                    "format": "%(asctime)s|%(levelname)s|{}|%(name)s|[%(pathname)s, %(lineno)s] : %(message)s ".format(self.service)
                }
            },
            "handlers": {
                "console1": {  # the name of handler
                    # emit to sys.stderr(default)
                    "class": "logging.StreamHandler",
                    "formatter": "normal",  # use the above "normal" formatter
                }
            },
            "loggers": {
                "INIT": {  # the name of logger
                    # use the above "console1" and "console2" handler
                    "handlers": ["console1"],
                    "level": self.log_level  # logging level
                },
                "SERVICE": {
                    "handlers": ["console1"],
                    "level": self.log_level
                },
                "KERNEL": {
                    "handlers": ["console1"],
                    "level": self.log_level
                }
            }
        }

    def getlogger(self, type):
        return logging.getLogger(type)

    def request_logging(self, logger, request, req_json):
        try:
            log_info = {
                "method": request.method,
                "path": request.path,
                "ip": request.remote_addr,
                "headers": request.headers,
                "full_path": request.full_path,
                "mac:": req_json["mac"],
                "timestamp": req_json["timestamp"],
                "data_version": req_json["data_version"]
            }
            logger.info(log_info)
        except:
            logger.error("request error")


if __name__ == '__main__':
    log_handler = LogHandler(service='Fishingman')
    init_logger = log_handler.getlogger('INIT')
    init_logger.info("success log")
    
    log_handler.service = "set1"
    log_handler.log_level = "ERROR"
    log_handler.set_logging()
    init_logger = log_handler.getlogger('INIT')
    init_logger.error("success log")
    
