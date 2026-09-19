# -*- coding: utf-8 -*-
"""
Единый логгер для всего бота.
Пишет одновременно в консоль и в файл logs/bot.log с ротацией.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# Папка для логов
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "bot.log")
os.makedirs(LOG_DIR, exist_ok=True)

# Формат: время | уровень | модуль | сообщение
FORMAT = "%(asctime)s | %(levelname)-7s | %(name)-12s | %(message)s"
DATE_FMT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """
    Возвращает логгер с заданным именем.
    Все логгеры используют одни и те же хендлеры (не дублируются).
    """
    logger = logging.getLogger(name)

    # Если уже настроен — не добавляем хендлеры повторно
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter(FORMAT, datefmt=DATE_FMT)

    # 1. Консоль
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # 2. Файл с ротацией: максимум 5 МБ × 3 файла
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Корневой логгер для бота
log = get_logger("bot")