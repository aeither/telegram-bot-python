import telebot
import yt_dlp
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text

    if "http" in text:
        bot.reply_to(message, "⏳ جاري التحميل...")

        ydl_opts = {
            'outtmpl': 'video.mp4',
            'format': 'best'
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([text])

            with open('video.mp4', 'rb') as video:
                bot.send_video(message.chat.id, video)

            os.remove('video.mp4')

        except Exception as e:
            bot.reply_to(message, f"❌ حصل خطأ: {e}")

    else:
        bot.reply_to(message, "ابعت لينك فيديو بس 🎥")

bot.remove_webhook()
bot.infinity_polling()
