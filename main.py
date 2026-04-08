import os
import telebot

# Получаем токен из Railway Variables
TOKEN = os.getenv("8709005198:AAG0SB65EJZR6leqzNpCL3RYpi8_7_ipeKo")

# Создаём бота
bot = telebot.TeleBot(TOKEN)

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Бот работает ✅")

# Ответ на любые сообщения
@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.send_message(message.chat.id, message.text)

# Запуск
bot.polling()
