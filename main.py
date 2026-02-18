import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from fuzzywuzzy import fuzz

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5329758526
AUTHOR_CONTACT = "@The_Yin"

logging.basicConfig(level=logging.INFO)

VIDEO_DATABASE = {
    "the last of us": {
        "name": "The Last of Us",
        "series": {
            "1": "placeholder",
            "2": "placeholder",
        }
    },
    "resident evil": {
        "name": "Resident Evil 2",
        "series": {
            "1": "placeholder",
        }
    }
}

def is_admin(user_id):
    return user_id == ADMIN_ID

def find_best_match(query):
    query = query.lower().strip()
    if query in VIDEO_DATABASE:
        return query
    best_match = None
    best_ratio = 0
    for game in VIDEO_DATABASE.keys():
        ratio = fuzz.token_sort_ratio(query, game)
        if ratio > best_ratio and ratio > 60:
            best_ratio = ratio
            best_match = game
    return best_match

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🎮 **ВИДЕО КУПЛИНОВА**\n\n"
        f"Автор: @kupilnov_official\n\n"
        f"Напиши название игры, например:\n"
        f"• The Last of Us\n"
        f"• Resident Evil 2\n\n"
        f"✅ Я понимаю опечатки!\n"
        f"❓ Нет видео? Пиши {AUTHOR_CONTACT}",
        parse_mode='Markdown'
    )

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Доступ запрещён")
        return
    await update.message.reply_text(
        "🛠 **Админ-панель**\n\n"
        "📥 Отправь любое видео — получишь file_id",
        parse_mode='Markdown'
    )

async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if update.message.video:
        file_id = update.message.video.file_id
        await update.message.reply_text(f"✅ `{file_id}`", parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    game_key = find_best_match(query)
    if not game_key:
        await update.message.reply_text(f"❌ Не найдено. Попробуй другое название или напиши {AUTHOR_CONTACT}")
        return
    game = VIDEO_DATABASE[game_key]
    buttons = []
    for series in game["series"].keys():
        buttons.append([InlineKeyboardButton(f"🎬 Серия {series}", callback_data=f"{game_key}|{series}")])
    await update.message.reply_text(
        f"🎮 **{game['name']}**",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    game_key, series_num = query.data.split('|')
    file_id = VIDEO_DATABASE[game_key]["series"][series_num]
    if file_id != "placeholder":
        await query.message.reply_video(
            video=file_id,
            caption=f"{VIDEO_DATABASE[game_key]['name']} – Серия {series_num}"
        )
    else:
        await query.message.reply_text("⏳ Видео скоро появится!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.VIDEO, get_file_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()

if __name__ == "__main__":
    main()
