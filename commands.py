import logging
import json
import os
from datetime import datetime
import asyncio
import pytz

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ─── تنظیمات ───────────────────────────────────────────────
TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
DATA_FILE = "users.json"
TIMEZONE = "Asia/Tehran"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── مراحل مکالمه ──────────────────────────────────────────
WAITING_CHANNEL, WAITING_MESSAGE, WAITING_HOUR = range(3)

# ─── ذخیره و بارگذاری داده ─────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── شروع ──────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("✅ ادمینم کردی؟ چک کن!", callback_data="check_admin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 سلام!\n\n"
        "برای استفاده از من، لطفاً ابتدا:\n"
        "1️⃣ منو در کانال یا گروهت به عنوان **ادمین** اضافه کن\n"
        "2️⃣ بعد دکمه زیر رو بزن تا چک کنم ✅\n\n"
        "⚠️ مطمئن شو که به من اجازه ارسال پیام داده شده.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ─── چک ادمین ──────────────────────────────────────────────
async def check_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "✅ خوش اومدی!\n\n"
        "حالا **آیدی** کانال یا گروهت رو برام بفرست.\n\n"
        "مثال:\n`@mychannel` یا `-1001234567890`",
        parse_mode="Markdown"
    )
    return WAITING_CHANNEL

# ─── دریافت آیدی کانال ─────────────────────────────────────
async def receive_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id = update.message.text.strip()
    context.user_data["channel_id"] = channel_id

    # چک کن ربات ادمین هست یا نه
    try:
        bot_member = await context.bot.get_chat_member(channel_id, context.bot.id)
        if bot_member.status not in ["administrator", "creator"]:
            await update.message.reply_text(
                "❌ من هنوز ادمین این کانال/گروه نیستم!\n\n"
                "ابتدا منو ادمین کن، بعد دوباره آیدی رو بفرست."
            )
            return WAITING_CHANNEL
    except Exception:
        await update.message.reply_text(
            "❌ نتونستم این کانال/گروه رو پیدا کنم!\n\n"
            "مطمئن شو:\n"
            "• آیدی درسته\n"
            "• منو ادمین کردی\n\n"
            "دوباره امتحان کن:"
        )
        return WAITING_CHANNEL

    await update.message.reply_text(
        f"✅ کانال/گروه `{channel_id}` تأیید شد!\n\n"
        "حالا **متن پیامی** که هر روز باید ارسال بشه رو بنویس:",
        parse_mode="Markdown"
    )
    return WAITING_MESSAGE

# ─── دریافت متن پیام ───────────────────────────────────────
async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["message_text"] = update.message.text
    await update.message.reply_text(
        "📝 پیام ذخیره شد!\n\n"
        "حالا **ساعت ارسال** رو بفرست (به وقت تهران).\n\n"
        "فرمت: `HH:MM`\n"
        "مثال: `08:30` یا `00:00`",
        parse_mode="Markdown"
    )
    return WAITING_HOUR

# ─── دریافت ساعت ───────────────────────────────────────────
async def receive_hour(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time_str = update.message.text.strip()

    # اعتبارسنجی فرمت ساعت
    try:
        hour, minute = map(int, time_str.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
    except (ValueError, AttributeError):
        await update.message.reply_text(
            "❌ فرمت ساعت اشتباهه!\n\n"
            "لطفاً به این شکل بنویس: `HH:MM`\n"
            "مثال: `08:30`",
            parse_mode="Markdown"
        )
        return WAITING_HOUR

    user_id = str(update.effective_user.id)
    channel_id = context.user_data["channel_id"]
    message_text = context.user_data["message_text"]

    # ذخیره اطلاعات
    data = load_data()
    data[user_id] = {
        "channel_id": channel_id,
        "message_text": message_text,
        "hour": hour,
        "minute": minute,
        "active": True
    }
    save_data(data)

    # اضافه کردن job به scheduler
    scheduler = context.application.bot_data.get("scheduler")
    if scheduler:
        job_id = f"job_{user_id}"
        # حذف job قبلی اگه وجود داشت
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        
        tz = pytz.timezone(TIMEZONE)
        scheduler.add_job(
            send_daily_message,
            "cron",
            hour=hour,
            minute=minute,
            timezone=tz,
            id=job_id,
            args=[context.application, user_id]
        )

    await update.message.reply_text(
        f"🎉 همه چیز تنظیم شد!\n\n"
        f"📢 کانال/گروه: `{channel_id}`\n"
        f"⏰ ساعت ارسال: `{hour:02d}:{minute:02d}` (تهران)\n"
        f"📝 پیام: {message_text}\n\n"
        f"هر روز ساعت {hour:02d}:{minute:02d} پیام ارسال میشه.\n"
        f"برای توقف بنویس: /stop",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# ─── ارسال پیام روزانه ──────────────────────────────────────
async def send_daily_message(app, user_id: str):
    data = load_data()
    user_data = data.get(user_id)
    if not user_data or not user_data.get("active"):
        return

    try:
        await app.bot.send_message(
            chat_id=user_data["channel_id"],
            text=user_data["message_text"]
        )
        logger.info(f"پیام برای کاربر {user_id} ارسال شد")
    except Exception as e:
        logger.error(f"خطا در ارسال پیام برای {user_id}: {e}")

# ─── توقف ──────────────────────────────────────────────────
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()

    if user_id in data and data[user_id].get("active"):
        data[user_id]["active"] = False
        save_data(data)

        # حذف job
        scheduler = context.application.bot_data.get("scheduler")
        if scheduler:
            job_id = f"job_{user_id}"
            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)

        await update.message.reply_text(
            "⏹ ربات متوقف شد!\n\n"
            "دیگه پیامی ارسال نمیشه.\n"
            "برای شروع دوباره /start بزن."
        )
    else:
        await update.message.reply_text(
            "ℹ️ هیچ تایمر فعالی وجود نداره.\n"
            "برای شروع /start بزن."
        )

# ─── لغو مکالمه ────────────────────────────────────────────
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ عملیات لغو شد.\n"
        "هر وقت خواستی /start بزن."
    )
    return ConversationHandler.END

# ─── بارگذاری jobها از فایل ─────────────────────────────────
def restore_jobs(scheduler, app):
    data = load_data()
    tz = pytz.timezone(TIMEZONE)
    for user_id, info in data.items():
        if info.get("active"):
            job_id = f"job_{user_id}"
            scheduler.add_job(
                send_daily_message,
                "cron",
                hour=info["hour"],
                minute=info["minute"],
                timezone=tz,
                id=job_id,
                args=[app, user_id]
            )
    logger.info(f"{len(data)} job بازیابی شد")

# ─── اجرای اصلی ────────────────────────────────────────────
def main():
    app = Application.builder().token(TOKEN).build()

    # Scheduler
    scheduler = AsyncIOScheduler()
    app.bot_data["scheduler"] = scheduler

    # ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(check_admin_callback, pattern="^check_admin$")],
        states={
            WAITING_CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_channel)],
            WAITING_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message)],
            WAITING_HOUR: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_hour)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(conv_handler)

    # بازیابی jobها و شروع scheduler
    scheduler.start()
    restore_jobs(scheduler, app)

    logger.info("ربات شروع به کار کرد...")
    app.run_polling()

if __name__ == "__main__":
    main()
