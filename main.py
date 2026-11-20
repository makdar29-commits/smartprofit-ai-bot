
import os
from datetime import date

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

keyboard = ReplyKeyboardMarkup(
    [
        ["💡 Идеи заработка", "✍️ Написать текст"],
        ["❓ Задать вопрос", "⭐ Premium"],
    ],
    resize_keyboard=True,
)

users = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я SmartProfit AI 🤖\n\n"
        "Помогаю с идеями заработка, текстами и вопросами.\n"
        "Бесплатно доступно 5 запросов в день.\n\n"
        "Выбери функцию или напиши мне!",
        reply_markup=keyboard,
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    today = str(date.today())

    if user_id not in users or users[user_id]["date"] != today:
        users[user_id] = {"date": today, "count": 0}

    if text == "⭐ Premium":
        await update.message.reply_text(
            "⭐ Premium подписка\n\n"
            "В будущем Premium даст больше запросов, "
            "расширенные функции и приоритет.\n"
            "Цена запуска: 99 грн/месяц."
        )
        return

    if users[user_id]["count"] >= 5:
        await update.message.reply_text(
            "Ты использовал 5 бесплатных запросов на сегодня.\n"
            "Premium скоро откроет больше возможностей ⭐"
        )
        return

    if text == "💡 Идеи заработка":
        prompt = "Предложи 5 реалистичных идей заработка с небольшим бюджетом."
    elif text == "✍️ Написать текст":
        prompt = "Помоги написать текст. Сначала уточни, для чего он."
    elif text == "❓ Задать вопрос":
        prompt = "Я хочу задать вопрос. Попроси меня написать его."
    else:
        prompt = text

    users[user_id]["count"] += 1

    await update.message.reply_text("⏳ Думаю...")

    if not OPENAI_API_KEY:
        answer = (
            "Бот работает! 🟢\n\n"
            "ИИ пока не подключён. Следующим шагом мы подключим "
            "его API-ключ, чтобы я мог отвечать полноценно."
        )
    else:
        try:
            from openai import OpenAI

            ai = OpenAI(api_key=OPENAI_API_KEY)
            response = ai.responses.create(
                model="gpt-4o-mini",
                input=[
                    {
                        "role": "system",
                        "content": "Ты SmartProfit AI. Отвечай по-русски, "
                        "дружелюбно, полезно и понятно."
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            answer = response.output_text
        except Exception:
            answer = "Не удалось получить ответ от ИИ. Попробуй позже."

    await update.message.reply_text(answer)


app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
