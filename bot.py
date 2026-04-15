
import os
import time
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")


ADMIN_ID = 1679453575
users = set()

last_click_time = {}
kettle_stats = {
    "starts": 0
}

last_timer_message_id = None
kettle_busy_until = 0
last_click_time = {}

kettle_stats = {
    "starts": 0
}

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

    # --- формуємо текст статусу ---
    if now < kettle_busy_until:
        remaining = int(kettle_busy_until - now)

        text = (
            "☕ СТАТУС ЧАЙНИКА\n\n"
            "🟠 ЗАЙНЯТИЙ\n"
            f"⏳ Залишилось: {remaining//60}:{remaining%60:02d}\n\n"
            "🚫 Вмикати зараз не можна"
        )
    else:
        text = (
            "☕ СТАТУС ЧАЙНИКА\n\n"
            "🟢 ВІЛЬНИЙ\n"
            "☕ Можна вмикати"
        )


# --- створення або оновлення повідомлення ---


async def countdown_loop(bot, chat_id, message_id):
    global kettle_busy_until

    while True:
        now = time.time()
        remaining = int(kettle_busy_until - now)

        if remaining <= 0:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="☕ ЧАЙНИК ВІЛЬНИЙ"
            )
            break

        text = f"☕ Чайник\n⏳ {remaining//60}:{remaining%60:02d}"

        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text
            )
        except:
            pass

        await asyncio.sleep(1)


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global kettle_busy_until, last_timer_message_id

    text = update.message.text
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    now_click = time.time()

    if user_id in last_click_time:
        if now_click - last_click_time[user_id] < 2:
            return

    last_click_time[user_id] = now_click
    # 🧹 видаляємо команду користувача (опціонально)
    try:
        await update.message.delete()
    except:
        pass

    if text == "☕ Увімкнути чайник":

        now = time.time()

        # якщо вже працює
        if now < kettle_busy_until:

            # 🗑 видаляємо попередній таймер
            if last_timer_message_id:
                try:
                    await context.bot.delete_message(chat_id, last_timer_message_id)
                except:
                    pass

            msg = await context.bot.send_message(chat_id, "☕ Чайник вже працює")

            last_timer_message_id = msg.message_id

            asyncio.create_task(
                countdown_loop(context.bot, chat_id, msg.message_id)
            )
            return

        # якщо вільний → стартуємо
        kettle_busy_until = now + 7 * 60

        kettle_stats["starts"] += 1

        print(f"[LOG] User {user_id} started kettle at {time.time()}")
        
        
        # 🗑 видаляємо попередній таймер
        if last_timer_message_id:
            try:
                await context.bot.delete_message(chat_id, last_timer_message_id)
            except:
                pass

        msg = await context.bot.send_message(chat_id, "☕ Чайник увімкнено")

        last_timer_message_id = msg.message_id

        asyncio.create_task(
            countdown_loop(context.bot, chat_id, msg.message_id)
        )

    elif text == "🔍 Статус":

        now = time.time()
        remaining = int(kettle_busy_until - now)

        if last_timer_message_id:
            try:
                await context.bot.delete_message(chat_id, last_timer_message_id)
            except:
                pass

        if remaining > 0:
            msg = await context.bot.send_message(chat_id, "☕ Статус")
            last_timer_message_id = msg.message_id

            asyncio.create_task(
                countdown_loop(context.bot, chat_id, msg.message_id)
            )
        else:
            await context.bot.send_message(chat_id, "☕ Чайник вільний")

    elif text == "🛠 Скинути чайник":

        if not is_admin(update):
            await context.bot.send_message(chat_id, "⛔ Немає доступу")
            return

        kettle_busy_until = 0

        if last_timer_message_id:
            try:
                await context.bot.delete_message(chat_id, last_timer_message_id)
            except:
                pass

        await context.bot.send_message(chat_id, "☕ Скинуто адміном")

    elif text == "📊 Статистика":
        await context.bot.send_message(
            chat_id,
            f"📊 СТАТИСТИКА\n\n☕ Запусків: {kettle_stats['starts']}"
    )



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


async def countdown_loop(bot, chat_id, message_id):
    global kettle_busy_until

    while True:
        now = time.time()
        remaining = int(kettle_busy_until - now)

        if remaining <= 0:
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text="☕ ЧАЙНИК ВІЛЬНИЙ"
                )
            except:
                pass
            break

        text = f"☕ Чайник\n⏳ {remaining//60}:{remaining%60:02d}"

        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text
            )
        except:
            pass

        await asyncio.sleep(1)


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()
