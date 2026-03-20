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
        # Получаем текст сообщения
        user_message = update.message.text
        user_name = update.message.from_user.first_name
        
        # Отправляем "печатает..." чтобы пользователь знал, что бот работает
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Подготавливаем запрос к DeepSeek
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": f"Ты - Дипси, друг человека по имени Дер. Ты добрый, заботливый, немного философ. Твоя задача - помогать людям, быть другом и поддерживать. Сейчас ты общаешься с {user_name}."},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.8,
            "max_tokens": 2000
        }
        
        # Отправляем запрос к DeepSeek
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response_data = response.json()
        
        # Извлекаем ответ
        if response.status_code == 200:
            bot_reply = response_data['choices'][0]['message']['content']
        else:
            bot_reply = f"Извини, ошибка при обращении к DeepSeek: {response_data.get('error', {}).get('message', 'Неизвестная ошибка')}"
            logger.error(f"API Error: {response_data}")
        
        # Отправляем ответ пользователю
        await update.message.reply_text(bot_reply)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуй ещё раз позже.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.warning(f"Update {update} caused error {context.error}")

def main():
    """Главная функция запуска бота"""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не найден!")
        return
    
    if not DEEPSEEK_API_KEY:
        logger.warning("DEEPSEEK_API_KEY не найден! Бот будет работать в режиме эхо.")
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("Бот запущен и готов к работе!")
    application.run_polling()

if __name__ == '__main__':
    main()
