
import os
import time
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

status_message_id = None
status_chat_id = None
ADMIN_ID = 1679453575
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
    "Система активна ☕",
    reply_markup=keyboard
)




async def update_status(bot, chat_id):
    global status_chat_id, status_message_id, kettle_busy_until

    now = time.time()

    if now < kettle_busy_until:
        remaining = int(kettle_busy_until - now)
        text = (
            "☕ СТАТУС ЧАЙНИКА\n\n"
            "🟠 ЗАЙНЯТИЙ\n"
            f"⏳ {remaining//60}:{remaining%60:02d}"
        )
    else:
        text = (
            "☕ СТАТУС ЧАЙНИКА\n\n"
            "🟢 ВІЛЬНИЙ"
        )

    if status_message_id is None:
        msg = await bot.send_message(chat_id, text)
        status_chat_id = chat_id
        status_message_id = msg.message_id
    else:
        await bot.edit_message_text(
            chat_id=status_chat_id,
            message_id=status_message_id,
            text=text
        )
        except:
            pass

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global kettle_busy_until

    text = update.message.text
    chat_id = update.effective_chat.id

    if text == "☕ Увімкнути чайник":

        now = time.time()

        if now < kettle_busy_until:
            await update_status(context.bot, chat_id)
            return
        
        kettle_busy_until = now + 7 * 60

        msg = await update.message.reply_text("☕ Чайник увімкнено\n⏳ 7:00")

        status_chat_id = chat_id
        status_message_id = msg.message_id        
        asyncio.create_task(
            countdown_global(context.bot)
)
        await update_status(context.bot, chat_id)
        
        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user,
                    text="⚠️ ЧАЙНИК УВІМКНЕНО!"
                )
            except:
                pass

    elif text == "🔍 Статус":
        await update_status(context.bot, chat_id)

    elif text == "🛠 Скинути чайник":

        if not is_admin(update):
            await update.message.reply_text("⛔ Немає доступу")
            return

        kettle_busy_until = 0
        await update.message.reply_text("☕ Скинуто адміном")

async def countdown_global(bot):
    global kettle_busy_until

    while True:
        now = time.time()

        if now >= kettle_busy_until:
            kettle_busy_until = 0

            if status_chat_id and status_message_id:
                try:
                    await bot.edit_message_text(
                        chat_id=status_chat_id,
                        message_id=status_message_id,
                        text="☕ СТАТУС ЧАЙНИКА\n\n🟢 ВІЛЬНИЙ\n☕ Можна вмикати"
                    )
                except:
                    pass
            break

        await update_status(bot, status_chat_id)

        await asyncio.sleep(1)


async def countdown_message(bot, chat_id, message_id, seconds):
    end_time = time.time() + seconds

    last_text = None

    while True:
        remaining = int(end_time - time.time())

        if remaining <= 0:
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text="☕ ЧАЙНИК ВІЛЬНИЙ ✅"
                )
            except Exception as e:
                print("Final edit error:", e)
            break

        mins = remaining // 60
        secs = remaining % 60

        text = f"☕ Чайник\n⏳ {mins}:{secs:02d}"

        # оновлюємо тільки якщо змінилось
        if text != last_text:
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=text
                )
                last_text = text
            except Exception as e:
                print("Edit error:", e)

        await asyncio.sleep(1)


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()
