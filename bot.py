ADMIN_ID = 1679453575
import os
import time
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

users = set()
kettle_busy_until = 0

keyboard = ReplyKeyboardMarkup(
    [
        ["☕ Увімкнути чайник", "🔍 Статус"],
        ["🛠 Скинути чайник"]
    ],
    resize_keyboard=True
)

def is_admin(update):
    return update.effective_user.id == ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_chat.id)

    user_id = update.effective_user.id

    await update.message.reply_text(
        f"Система активна ☕\nТвій ID: {user_id}"
    )


def get_status_text():
    now = time.time()

    if now < kettle_busy_until:
        remaining = int(kettle_busy_until - now)
        return f"☕ Чайник УВІМКНЕНО\n⏳ {remaining//60}:{remaining%60:02d}"
    else:
        return "☕ Чайник ВІЛЬНИЙ ✅"


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global kettle_busy_until

    text = update.message.text
    chat_id = update.effective_chat.id

    if text == "☕ Увімкнути чайник":

        now = time.time()

        if now < kettle_busy_until:
            await update.message.reply_text(get_status_text())
            return

        kettle_busy_until = now + 7 * 60

        msg = await update.message.reply_text("☕ Чайник увімкнено\n⏳ 7:00")

        asyncio.create_task(
            countdown_message(context.bot, chat_id, msg.message_id, 7*60)
        )

        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user,
                    text="⚠️ ЧАЙНИК УВІМКНЕНО!"
                )
            except:
                pass

    elif text == "🔍 Статус":
        await update.message.reply_text(get_status_text())


elif text == "🛠 Скинути чайник":

    if not is_admin(update):
        await update.message.reply_text("⛔ Немає доступу")
        return

    global kettle_busy_until
    kettle_busy_until = 0

    await update.message.reply_text("☕ Скинуто адміном")


async def countdown_message(bot, chat_id, message_id, seconds):
    while seconds >= 0:
        mins = seconds // 60
        secs = seconds % 60

        text = f"☕ Чайник\n⏳ {mins}:{secs:02d}"

        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text)
        except:
            pass

        await asyncio.sleep(1)
        seconds -= 1


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()
