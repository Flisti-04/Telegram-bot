import os
import time
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

users = set()
kettle_busy_until = 0

keyboard = ReplyKeyboardMarkup([["☕ Увімкнути чайник"]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_chat.id)
    await update.message.reply_text("Додано в систему ☕", reply_markup=keyboard)


async def countdown_message(bot, chat_id, message_id, seconds):
    while seconds >= 0:
        mins = seconds // 60
        secs = seconds % 60

        text = f"☕ Чайник увімкнено\n⏳ {mins}:{secs:02d}\nНЕ ВМИКАЙ СВІЙ ⚠️"

        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text
            )
        except:
            pass

        await asyncio.sleep(1)
        seconds -= 1


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global kettle_busy_until

    text = update.message.text
    chat_id = update.effective_chat.id

    if text == "☕ Увімкнути чайник":

        now = time.time()

        if now < kettle_busy_until:
            remaining = int(kettle_busy_until - now)
            await update.message.reply_text(f"⚠️ Зайнято ще {remaining//60}:{remaining%60:02d}")
            return

        kettle_busy_until = now + 7 * 60

        # повідомлення з таймером
        msg = await update.message.reply_text("☕ Чайник увімкнено\n⏳ 7:00\nНЕ ВМИКАЙ СВІЙ ⚠️")

        # запускаємо таймер
        asyncio.create_task(
            countdown_message(context.bot, update.effective_chat.id, msg.message_id, 7*60)
        )

        # повідомляємо всіх
        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user,
                    text="☕ УВАГА! ЧАЙНИК УВІМКНЕНО ⚠️"
                )
            except:
                pass


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()
