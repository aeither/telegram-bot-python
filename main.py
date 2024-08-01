import os
import telebot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Replace 'TELEGRAM_BOT_TOKEN' with the token you received from BotFather
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = ("Привет! Добро пожаловать в CATCHING THE CASH 😺\n"
                    "Отныне ты — директор криптобиржи.\n"
                    "Какой? Выбирай сам. Тапай по экрану, собирай монеты, "
                    "качай пассивный доход, разрабатывай собственную стратегию дохода.\n"
                    "Мы в свою очередь оценим это во время листинга токена, даты которого ты узнаешь совсем скоро.\n"
                    "Про друзей не забывай — зови их в игру и получайте вместе ещё больше монет!")

    # Создание кнопки для запуска Mini App
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="Играть в 1 клик 😺", web_app=WebAppInfo(url="https://graceful-pika-90363b.netlify.app/"))
    markup.add(button)

    # Отправка сообщения с кнопкой
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)

bot.polling()
