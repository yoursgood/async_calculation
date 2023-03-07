"""Логгер"""
from pathlib import Path
import logging
from datetime import datetime

def initialize_logger(name):
    """Инициализация логгера для логирования в файл
    :return logger: логгер, испоользуемый для записи
    """
    # создание директории
    BASE_DIR = Path(__file__).resolve().parent.parent
    DIR = BASE_DIR / 'logs'
    DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    f_handler = logging.FileHandler(
        filename=f'logs/{datetime.now().strftime("%Y-%m-%d")}_{name}.log'
    )
    f_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '[%(asctime)s] : %(levelname)s : %(message)s',
         "%Y-%m-%d %H:%M:%S"
    )

    f_handler.setFormatter(formatter)
    logger.addHandler(f_handler)

    return logger