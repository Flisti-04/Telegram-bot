import os
import time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

users = set()
kettle_busy_until = 0

keyboard = ReplyKeyboardMarkup([["☕ Увімкнути чайник"]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_chat.id)
    await update.message.reply_text("Додано в систему ☕", reply_markup=keyboard)

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global kettle_busy_until

    text = update.message.text
    chat_id = update.effective_chat.id

    if text == "☕ Увімкнути чайник":

        now = time.time()

        if now < kettle_busy_until:
            remaining = int(kettle_busy_until - now)
            await update.message.reply_text(f"⚠️ Зайнято! ще {remaining} сек")
            return

        kettle_busy_until = now + 7 * 60  # 7 хв

        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user,
                    text="☕ ЧАЙНИК УВІМКНЕНО! НЕ ВМИКАЙ СВІЙ ⚠️"
                )
            except:
                pass

        await update.message.reply_text("Ок, сигнал відправлено 🚨")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()
