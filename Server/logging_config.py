import logging.config

# https://stackoverflow.com/questions/7507825/where-is-a-complete-example-of-logging-config-dictconfig

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)-8s [%(threadName)s] %(name)s : %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },

    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}

def setup_logging():
    logging.config.dictConfig(LOGGING)

if __name__ == "__main__":
    setup_logging()

    logging.debug("Debug message")
    logging.info("Info message")
    logging.warning("Warning message")
    logging.error("Error message")
    logging.critical("Critical message")