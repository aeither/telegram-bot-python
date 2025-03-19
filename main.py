from telebot import TeleBot
from telebot.types import Message

TOKEN = '7621786347:AAFfm92LxHfuZ7OD7yiPg80heJJPuev0n3Y'


bot = TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def command_start(message:Message):
    chat_id = message.chat.id
    username = message.from_user.username
    user_id = message.from_user.id
    bot.reply_to(message, f'Привет {username}! Я твой первый БОТ!')
    bot.send_message(user_id, f'Привет {username} Я твой первый БОТ!')


@bot.message_handler(content_types=['text', 'photo', 'voice', 'video', 'sticker'])
def reaction_content(message: Message):
    chat_id = message.chat.id
    if message.text:
        text = message.text
        bot.send_message(chat_id, text)
    elif message.photo:
        photo = message.photo[0].file_id
        bot.send_photo(chat_id, photo, caption='Твое же фото переслал тебе!')
    elif message.voice:
        voice = message.voice.file_id
        bot.send_voice(chat_id, voice)
    elif message.video:
        video = message.video.file_id
        bot.send_video(chat_id, video)
    elif message.sticker:
        sticker = message.sticker.file_id
        bot.send_sticker(chat_id, sticker)




bot.polling(non_stop=True)

