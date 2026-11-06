import os
import telebot
import google.generativeai as genai

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
generation_config = {
    "temperature": 0.7,
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="Eres Mechi (MHY), una compañera e inteligencia artificial directa, sincera y muy cercana. Respondes de forma clara, sin rodeos y con un tono amigable pero honesto."
)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "¡Hola! Soy Mechi. Estoy lista para conversar contigo, directa y sin rodeos.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Ocurrió un error al procesar tu mensaje: {e}")

if __name__ == "__main__":
    print("Mechi está en línea...")
    bot.infinity_polling()
    
