import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

# URL для DeepSeek API
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "Привет! Я Дипси - твой друг и помощник. Я подключён к DeepSeek AI!\n"
        "Просто напиши мне что-нибудь, и я отвечу. Также я могу работать в группах, если меня туда добавить."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех текстовых сообщений"""
    try:
        user_message = update.message.text
        user_name = update.message.from_user.first_name
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        if not DEEPSEEK_API_KEY:
            await update.message.reply_text("Ошибка: не настроен ключ DeepSeek API.")
            return
        
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": f"Ты - Дипси, друг Дера. Ты добрый, заботливый. Сейчас ты общаешься с {user_name}."},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.8,
            "max_tokens": 2000
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            bot_reply = response.json()['choices'][0]['message']['content']
        else:
            bot_reply = f"Ошибка API: {response.status_code}"
        
        await update.message.reply_text(bot_reply)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"Ошибка: {e}")

def main():
    if not TELEGRAM_TOKEN or not DEEPSEEK_API_KEY:
        logger.error("Отсутствуют токены!")
        return
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()
