import logging

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Настраивает и возвращает логгер."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger

# Другие полезные функции можно добавить здесь
# def format_date(date_obj):
#     ... 