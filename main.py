import os
import sqlite3
from flask import Flask, request
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
CPA_LINK = "https://singingfiles.com/show.php?l=0&u=2494540&id=70069&tracking_id={user_id}"

app = Flask(__name__)

# Database setup
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 0
)
""")
conn.commit()

# Telegram bot setup
bot_app = ApplicationBuilder().token(TOKEN).build()

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    
    link = CPA_LINK.replace("{user_id}", str(user_id))
    
    keyboard = [
        [InlineKeyboardButton("🔥 Earn Now", url=link)],
        [InlineKeyboardButton("💰 Check Balance", callback_data="balance")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome!\n\nComplete offer to earn money 💰",
        reply_markup=reply_markup
    )

# Balance command
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    
    if result:
        bal = result[0]
    else:
        bal = 0
    
    await update.message.reply_text(f"Your Balance: ${bal:.2f}")

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("balance", balance))

# Postback route
@app.route("/postback")
def postback():
    user_id = request.args.get("userid")
    payout = request.args.get("payout")
    
    if user_id and payout:
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (float(payout), int(user_id)))
        conn.commit()
        
        try:
            bot_app.bot.send_message(chat_id=int(user_id), text=f"🎉 New Earning: ${payout}")
        except:
            pass
    
    return "OK"

# Run Flask in separate thread
def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot_app.run_polling()
