import os
import telebot
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup
import time
import schedule

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load environment variables
load_dotenv()

# Replace 'TELEGRAM_BOT_TOKEN' with the token you received from BotFather
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

CHAT_ID = '1900576053'

bot = telebot.TeleBot(TOKEN)
# Создание объекта бота
def get_artist_info():
    url = "https://www.energyfm.ru/playlist"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        # Найдите нужные элементы на странице, которые содержат информацию об артисте и времени
        playlist_items = soup.find_all('div', class_='playlist__item')[:5]

        # Для каждого элемента плейлиста
        arts = []
        for item in playlist_items:
            artist = item.find('div', class_='player__subtitle').text.strip()
            time_played = item.find('div',
                class_='playlist__time').text.strip()
            arts.append(f"Artist: {artist}, Time: {time_played}")

        send_email(
            'mr.ramzeng@gmail.com', 'ENERGY_BOT', '\n'.join(arts)
        )
        bot.send_message(CHAT_ID, '\n'.join(arts))

# Отслеживание изменений в плейлисте
last_playlist = None

schedule.every().hour.at(":12").do(get_artist_info)

# Основной цикл
while True:
    try:
        # schedule.run_pending()
        get_artist_info()
    except Exception as e:
        print(f"Произошла ошибка: {e}")

    # Проверка каждые 60 секунд
    # time.sleep(1)
    time.sleep(120)
