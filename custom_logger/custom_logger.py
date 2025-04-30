import logging

def get_logger(name="calendar_bot", level=logging.DEBUG):
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger  # Prevent adding handlers multiple times

    logger.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    return logger
