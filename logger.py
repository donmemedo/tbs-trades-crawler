import logging
from logging.config import dictConfig
import socket
from config import setting


log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(created)f %(exc_info)s %(filename)s %(funcName)s %(levelname)s %(levelno)s %(lineno)d %(module)s %(message)s %(pathname)s %(process)s %(processName)s %(relativeCreated)d %(thread)s %(threadName)s'
        }
    },
    "handlers": {
        "console": {
            "formatter": "json",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr"
        },
        "splunk": {
            "class": "logging.handlers.SysLogHandler",
            "address": (setting.SPLUNK_HOST, setting.SPLUNK_PORT),
            "socktype": socket.SOCK_DGRAM,
            "formatter": "json"
            }
    },
    "loggers": {
        "crawlers": {
            "handlers": ['console', 'splunk'],
            "level": "DEBUG",
            "propagate": False
        },
        "urllib3": {
            "level": "INFO",
            "handlers": ["splunk"],
            "propagate": False
        }
    },
}


dictConfig(log_config)
logger = logging.getLogger('urllib3')
