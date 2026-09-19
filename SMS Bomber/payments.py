# -*- coding: utf-8 -*-

import uuid
import threading
import logging
from flask import Flask, request, jsonify
from yookassa import Configuration, Payment
from yookassa.domain.notification import WebhookNotificationFactory

# ---------- НАСТРОЙКИ ----------
# Получи их в личном кабинете ЮKassa: https://yookassa.ru/my
YOOKASSA_SHOP_ID = cfg.YOOKASSA_SHOP_ID
YOOKASSA_SECRET_KEY = cfg.YOOKASSA_SECRET_KEY
# Адрес и порт, на котором будет слушать вебхук
WEBHOOK_HOST = cfg.WEBHOOK_HOST
WEBHOOK_PORT = cfg.WEBHOOK_PORT

# Цена VIP-доступа и срок
PAYMENT_PRICE = cfg.PRICE
VIP_DAYS = cfg.VIP_DAYS
# -------------------------------

Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Сюда положим bot и функцию выдачи VIP из основного файла
_bot = None
_add_vip = None

# В памяти храним ID уже обработанных платежей (идемпотентность).
# В продакшене замени на таблицу в БД.
_processed_payments = set()


def setup(bot_instance, add_vip_func):
    """
    Вызывается один раз из основного файла после создания бота.
    bot_instance  — объект TeleBot
    add_vip_func  — функция add_vip(user_id) из твоего кода
    """
    global _bot, _add_vip
    _bot = bot_instance
    _add_vip = add_vip_func


def create_payment_link(chat_id: int) -> str:
    """
    Создаёт платёж в ЮKassa и возвращает ссылку на оплату.
    Эту ссылку показывай пользователю кнопкой.
    """
    idempotence_key = str(uuid.uuid4())  # обязателен для ЮKassa

    payment = Payment.create({
        "amount": {
            "value": f"{PAYMENT_PRICE}.00",
            "currency": "RUB"
        },
        "capture": True,  # сразу списываем
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me"  # куда вернётся пользователь после оплаты
        },
        "description": f"VIP доступ для chat_id={chat_id}",
        "metadata": {
            "chat_id": str(chat_id)  # сюда кладём ID пользователя
        }
    }, idempotence_key)

    return payment.confirmation.confirmation_url


@app.route(WEBHOOK_PATH, methods=["POST"])
def yookassa_webhook():
    """ЮKassa дёргает этот эндпоинт, когда платёж прошёл."""
    payload = request.get_json(force=True)
    signature = request.headers.get("Signature")

    try:
        # SDK сам проверит подпись, если передать заголовок
        notification = WebhookNotificationFactory().create(payload, signature)
    except Exception:
        logging.exception("Невалидный вебхук или плохая подпись")
        return jsonify({"status": "error"}), 400

    if notification.event == "payment.succeeded":
        payment = notification.object
        chat_id = payment.metadata.get("chat_id")

        if not chat_id:
            return jsonify({"status": "ok"}), 200

        # Идемпотентность: ЮKassa может повторить вебхук
        if payment.id in _processed_payments:
            logging.info(f"Платёж {payment.id} уже обработан, пропускаем")
            return jsonify({"status": "ok"}), 200

        _processed_payments.add(payment.id)

        try:
            _add_vip(int(chat_id))
            _bot.send_message(
                int(chat_id),
                "🙈 Спасибо за покупку!\n\n<b>😉 Удачного пользования, и не шалите!</b>",
                parse_mode="HTML"
            )
            logging.info(f"VIP выдан пользователю {chat_id}, платёж {payment.id}")
        except Exception:
            logging.exception("Не удалось выдать VIP")

    return jsonify({"status": "ok"}), 200


def _run_server():
    app.run(host=WEBHOOK_HOST, port=WEBHOOK_PORT, debug=False, use_reloader=False)


def start():
    """Запускает Flask-сервер в фоновом потоке."""
    t = threading.Thread(target=_run_server, daemon=True)
    t.start()
    logging.info(f"ЮKassa вебхук слушает {WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}")