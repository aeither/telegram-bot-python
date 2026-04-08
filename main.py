import os
import telebot
from telebot import types
import yt_dlp

TOKEN = os.getenv("8709005198:AAEIw9YwBKi1iRYn2oQlw_8CR_OWe9XD3ms")
bot = telebot.TeleBot(TOKEN)

# Простая база "платных" пользователей
paid_users = set()

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("📥 Скачать видео")
    btn2 = types.KeyboardButton("💰 Купить доступ")
    btn3 = types.KeyboardButton("ℹ️ Помощь")

    markup.add(btn1, btn2, btn3)

    bot.send_message(
        message.chat.id,
        "Привет 👋\nЯ бот для скачивания видео.\nВыбери действие:",
        reply_markup=markup
    )

# ---------------- HELP ----------------
@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(
        message.chat.id,
        "📌 Как пользоваться:\n"
        "1. Нажми 'Скачать видео'\n"
        "2. Отправь ссылку\n\n"
        "Поддержка: YouTube, TikTok, Instagram и др."
    )

# ---------------- BUY ----------------
@bot.message_handler(func=lambda m: m.text == "💰 Купить доступ")
def buy(message):
    bot.send_message(
        message.chat.id,
        "💳 Для теста введи команду /pay\n"
        "После этого доступ откроется."
    )

@bot.message_handler(commands=['pay'])
def pay(message):
    paid_users.add(message.chat.id)
    bot.send_message(message.chat.id, "✅ Доступ активирован!")

# ---------------- DOWNLOAD BUTTON ----------------
@bot.message_handler(func=lambda m: m.text == "📥 Скачать видео")
def ask_link(message):
    bot.send_message(message.chat.id, "Отправь ссылку на видео 🎥")

# ---------------- DOWNLOAD LOGIC ----------------
@bot.message_handler(content_types=['text'])
def handle_link(message):
    url = message.text

    # Проверка доступа
    if message.chat.id not in paid_users:
        bot.send_message(message.chat.id, "❌ Сначала купите доступ.")
        return

    bot.send_message(message.chat.id, "⏳ Скачиваю видео...")

    try:
        ydl_opts = {
            'outtmpl': 'video.mp4',
            'format': 'mp4'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open("video.mp4", "rb") as video:
            bot.send_video(message.chat.id, video)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

# ---------------- RUN ----------------
bot.polling()
