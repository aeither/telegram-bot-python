import os
import time
import telebot
from dotenv import load_dotenv
from commands import register_commands

# Load environment variables
load_dotenv()

# Replace 'TELEGRAM_BOT_TOKEN' with the token you received from BotFather
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
try:
    bot = telebot.TeleBot(TOKEN)
    register_commands(bot)

   @bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    msg = bot.send_message(message.chat.id, "Please enter your access code:")
    bot.register_next_step_handler(msg, validate_code)

def validate_code(message):
    if message.text in VALID_CODES:
        bot.send_message(message.chat.id, "✓ Code valid! You can now link your MT5 account.")
    else:
        bot.send_message(message.chat.id, "✗ Invalid code. Try again.")

    @bot.message_handler(func=lambda msg: True)
    def echo_all(message):
        """
        Echo all incoming text messages back to the user.

        Args:
            message (telebot.types.Message): The message object.
        """
        bot.reply_to(message, message.text)

    # Remove webhook to avoid conflicts with polling
    bot.delete_webhook(drop_pending_updates=True)
    bot.polling()

except Exception as e:
    print(f"CRITICAL ERROR: Failed to initialize bot with provided token. Error: {e}")
    print("The application will hang to prevent a restart loop. Please fix the TELEGRAM_BOT_TOKEN environment variable.")
    while True:
        time.sleep(3600)
