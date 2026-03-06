import os
import telebot
from dotenv import load_dotenv
import requests

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "ðŸš€ PolyBot Live! Commands: /poly /oscars")

@bot.message_handler(commands=['poly'])
def poly_top(message):
    try:
        r = requests.get('https://gamma.api.polymarket.com/markets?active=true&limit=10&sort=volume', timeout=10)
        data = r.json()
        msg = "ðŸ† TOP 10 POLYMARKET VALUE BETS:\n\n"
        count = 0
        for m in data:
            yes = m.get('yes_price', 0.5)
            value_yes = max(0, 1 - yes - 0.15)
            value_no = max(0, yes - 0.15)
            if max(value_yes, value_no) > 0 and count < 5:
                side = 'YES' if value_yes > value_no else 'NO'
                vol = m.get('volume24hrs', 0)
                msg += f"â€¢ {m['question'][:50]}...\n  {side}: {max(value_yes,value_no):.1%} Vol ${vol:,.0f}\n\n"
                count += 1
        bot.reply_to(message, msg or "No high value bets now.")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['oscars'])
def oscars(message):
    bot.reply_to(message, "ðŸ“½ï¸ OSCARS Sinners: Yes 18% (72% value) RECOMMEND! Vol $23M [page:3]\np olymarket.com/event/oscars-2026-best-picture-winner")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)

if __name__ == '__main__':
    bot.polling()
