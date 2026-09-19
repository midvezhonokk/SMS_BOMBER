# -*- coding: utf-8 -*-
"""
Все секреты и настройки бота в одном месте.
Читает из .env файла.
"""

import os
from dotenv import load_dotenv

# Загружаем .env из текущей папки
load_dotenv()


def _get_int(name: str, default=None):
    """Безопасно читает целое число из env. Пустое значение → default."""
    val = os.environ.get(name)
    if val is None or val.strip() == "":
        return default
    return int(val)


def _get_str(name: str, default=None):
    val = os.environ.get(name)
    if val is None or val.strip() == "":
        return default
    return val


# ===== Telegram =====
TOKEN = _get_str("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в .env")

ADMIN_CHAT_ID = _get_int("ADMIN_CHAT_ID")
ADMIN_CHAT_ID1 = _get_int("ADMIN_CHAT_ID1")
VOXDOX_CHAT_ID = _get_int("VOXDOX_CHAT_ID")
GROUP_ID = _get_int("GROUP_ID")

# ===== ЮKassa =====
YOOKASSA_SHOP_ID = _get_str("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = _get_str("YOOKASSA_SECRET_KEY")

# ===== Вебхук =====
WEBHOOK_HOST = _get_str("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = _get_int("WEBHOOK_PORT", 8080)

# ===== Бизнес-настройки =====
PRICE = _get_int("PRICE", 100)
THREADS_LIMIT = _get_int("THREADS_LIMIT", 200)
VIP_DAYS = _get_int("VIP_DAYS", 30)

# ===== Пути к файлам (на будущее, когда будем переезжать на БД) =====
CHAT_IDS_FILE = "chat_ids.txt"
CHATS_IDS_FILE = "vip_id.txt"
NUM_FILE = "num.txt"
WL_FILE = "numWL.txt"