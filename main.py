"""Telegram-бот-анкета.

Механика: /start -> кнопка "Подать заявку" -> форма из 4 полей ->
проверка (4 нумерованных строки одним сообщением) -> подтверждение.

Все тексты — нейтральные заглушки. Замени их на свои в блоке "Тексты".
"""

import logging
import os
import re

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN не задан. Скопируй .env.example в .env и впиши токен.")

logging.basicConfig(level=logging.INFO)

# --- Тексты (замени на свои) ---------------------------------------------
WELCOME = """🎉 Добро пожаловать на ежедневный розыгрыш 5000 голды от Standoff 2!

🥇 Мы — команда разработчиков Axlebolt, и каждый день выбираем одного счастливчика, который получает 5000 голды на свой аккаунт просто за то, что он с нами.

📊 Почему это честно и безопасно:
• Мы уже вручили более 180.000+ голды за последнее время.
• Победители определяются, проверкой модератора, если он проникнется вашей историей то 5000 голды - ваши

🎰 Готов испытать удачу? Оставить анкету можно здесь 👇"""

BUTTON_APPLY = "🎁 Подать заявку"

FORM_INTRO = """📝 Отлично! Давай заполним короткую анкету — это займёт всего минуту.
Мы просим всего несколько данных, чтобы:
✔ Убедиться, что ты реальный игрок, а не бот.
✔ Узнать твоё мнение об игре — нам важно делать её лучше.

🔒 О безопасности: мы не требуем оплаты/предоплаты, паспортов, банковской информации.
📖 Анкета скидывается на проверку реальному человеку, а не боту. У нас только один модератор - @So2_Anketa
НЕ ВЕДИТЕСЬ НА ФЕЙКОВ!!!

1️⃣ Как тебя зовут?
(можно игровое имя)

2️⃣ Сколько тебе лет?
(это нужно, чтобы понимать аудиторию и делать игру удобнее для всех возрастов)

3️⃣ Почему именно ты заслуживаешь того, чтобы выиграть 5000 голды?
(напиши честно, почему ты заслужил получить в прокачку)

4️⃣ Как давно ты играешь Standoff 2, что тебе нравится, а что хотел бы улучшить?
(нам очень интересно мнение разных людей)

📖 Отправь анкету прямо сюда, в чат с ботом:
✍ Пример анкеты:
1) Данил
2) 12
3) я давно играю в стендоф хочу нож
4) уже 2 года хотелось бы поменьше читеров

✅ Если ваша анкета заинтересует нас, то вам напишет @So2_Anketa
НЕ ВЕДИТЕСЬ НА ФЕЙКОВ!!!"""

ANSWER_ACCEPTED = """🎉 Спасибо! Твоя анкета принята!
⚡ Если анкета заинтересует, то тебе напишет модератор - @So2_Anketa
✍ Если захочешь изменить ответы — нажми кнопку ниже."""

BUTTON_REDO = "Пересдать анкету"

ANSWER_INVALID = """🔴 Не удалось распознать анкету.

📖 Отправь её одним сообщением, по одному ответу на строку, например:

1) Имя
2) Возраст
3) Почему ты заслуживаешь получить прокачку
4) Как давно играешь в Standoff 2"""
# -------------------------------------------------------------------------

_FORM_LINE = re.compile(r"^\s*\d+\s*[.)\-]\s*")


def _form_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(BUTTON_APPLY, callback_data="form_start")]]
    )


def _redo_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(BUTTON_REDO, callback_data="form_start")]]
    )


async def _post_init(app: Application) -> None:
    await app.bot.delete_webhook()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["state"] = None
    await update.message.reply_text(WELCOME, reply_markup=_form_keyboard())


async def form_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    context.user_data["state"] = "form"
    await update.callback_query.message.reply_text(FORM_INTRO)


def _has_4_answers(text: str) -> bool:
    return sum(1 for line in text.splitlines() if _FORM_LINE.match(line)) >= 4


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get("state") != "form":
        return
    text = update.message.text or ""
    if _has_4_answers(text):
        context.user_data["state"] = None
        await update.message.reply_text(ANSWER_ACCEPTED, reply_markup=_redo_keyboard())
    else:
        await update.message.reply_text(ANSWER_INVALID)


def main() -> None:
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(_post_init)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(form_start, pattern="^form_start$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()