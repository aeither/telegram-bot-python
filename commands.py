from telebot import TeleBot
from telebot.types import BotCommand

def register_commands(bot: TeleBot):
    """
    Register bot commands with Telegram.

    Args:
        bot (TeleBot): The TeleBot instance.
    """
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("hello", "Hello"),
    ]
    
    bot.set_my_commands(commands)
