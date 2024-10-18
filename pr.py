import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

API_TOKEN = '7392327533:AAFPU_g9LG4gNksufhVvcB1Hb-_ZisQpI1Q'

# Bot va Dispatcher yaratish
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Foydalanuvchi va bot xabarlarini saqlash uchun lug'at
bot_messages = {}
correct_answer_count = {}

# Koreyscha harflar va qoidalar
korean_letters = [
    {
        "letter": "ㄱ",
        "rules": [
            {"rule": "So'z boshida: ㄱ... - (k)", "question": "ㄱ...?", "correct_answer": 'k'},
            {"rule": "Ikki unli orasida: ...ㄱ... - (g)", "question": "...ㄱ...?", "correct_answer": 'g'},
            {"rule": "So'z oxirida: ...ㄱ - (k)", "question": "...ㄱ?", "correct_answer": 'k'}
        ]
    }
    # Keyingi harflarni shu yerda qo'shish mumkin
]

current_letter_index = 0
current_question_index = 0
general_rule_sent = False  # Umumiy qoida yuborilganini saqlash

# Foydalanuvchi va bot xabarlarini saqlash uchun lug'at
bot_messages = {}

# Foydalanuvchi xabarlarini o'chirish funksiyasi
async def delete_user_message(message):
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print(f"Xatolik: {e}")

# Bot xabarlarini o'chirish funksiyasi
async def clear_previous_bot_messages(chat_id):
    if chat_id in bot_messages and bot_messages[chat_id]:
        try:
            while bot_messages[chat_id]:
                msg_id = bot_messages[chat_id].pop(0)
                await bot.delete_message(chat_id, msg_id)
        except Exception as e:  
            print(f"Xatolik: {e}")

# Botning yangi xabarini saqlash
async def store_bot_message(chat_id, message):
    if chat_id not in bot_messages:
        bot_messages[chat_id] = []
    bot_messages[chat_id].append(message.message_id)

@dp.message(Command('start'))
async def send_welcome(message: Message):
    await clear_previous_bot_messages(message.chat.id)  # Oldingi bot xabarlarini o'chirish
    
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Koreys tilini o`rganish")],
            [types.KeyboardButton(text="Koreyaga ketish")]
        ],
        resize_keyboard=True  # Klaviaturani o'lchamini moslashtirish
    )

    # Bot xabarini yuborish
    welcome_message = await message.answer("Bo'limni tanlang:", reply_markup=keyboard)
    await store_bot_message(message.chat.id, welcome_message)  # Bot xabarini saqlash

# "Koreys tilini o'rganish" bo'limi uchun funksiya
@dp.message(lambda message: message.text == "Koreys tilini o`rganish")
async def learn_korean(message: Message):
    await clear_previous_bot_messages(message.chat.id)  # Oldingi bot xabarlarini o'chirish
    await delete_user_message(message)  # Oldingi foydalanuvchi xabarini o'chirish
    # Daraja tugmalari klaviaturasini yaratish
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Boshlang'ich daraja")],
            [types.KeyboardButton(text="O'rta daraja")],
            [types.KeyboardButton(text="Yuqori daraja")],
            [types.KeyboardButton(text="Bosh menyu")]  # Orqaga qaytish tugmasi
        ],
        resize_keyboard=True  # Klaviaturani o'lchamini moslashtirish
    )
    
    # Bo'limni tanlash xabarini yuborish
    learn_message = await message.answer("Qaysi darajani tanlaysiz?", reply_markup=keyboard)
    await store_bot_message(message.chat.id, learn_message)  # Bot xabarini saqlash

# "Koreyaga ketish" bo'limi uchun funksiya
@dp.message(lambda message: message.text == "Koreyaga ketish")
async def travel_section(message: Message):
    await clear_previous_bot_messages(message.chat.id)  # Oldingi bot xabarlarini o'chirishS
    await delete_user_message(message)  # Oldingi foydalanuvchi xabarini o'chirish
    # Havola bilan tugma yaratish
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Bosh menyu")]
        ],
        resize_keyboard=True  # Klaviaturani o'lchamini moslashtirish
    )

    travel_message = await message.answer("Koreyaga ketish bo'limiga xush kelibsiz!\nOrqaga qaytish uchun tugmani bosing:", reply_markup=keyboard)
    await store_bot_message(message.chat.id, travel_message)  # Bot xabarini saqlash

# "Orqaga qaytish" tugmasi uchun logika
@dp.message(lambda message: message.text == 'Bosh menyu')
async def back_to_main_menu(message: Message):
    await clear_previous_bot_messages(message.chat.id)  # Oldingi bot xabarlarini o'chirish
    await delete_user_message(message)  # Oldingi foydalanuvchi xabarini o'chirish

    # "Bo'limni tanlang:" menyusini qaytarish
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Koreys tilini o`rganish")],
            [types.KeyboardButton(text="Koreyaga ketish")]
        ],
        resize_keyboard=True  # Klaviaturani o'lchamini moslashtirish
    )

    back_message = await message.answer("Bo'limni tanlang:", reply_markup=keyboard)
    await store_bot_message(message.chat.id, back_message)  # Bot xabarini saqlash

# Savol berish funksiyasi
async def ask_question(message: types.Message):
    global current_question_index

    # Joriy harf va savolni tanlash
    letter_data = korean_letters[current_letter_index]
    
    # Savollar orasidan random tanlab olish
    current_question_index = random.randint(0, len(letter_data["rules"]) - 1)
    question_data = letter_data["rules"][current_question_index]

    # Savolni yuborish
    question_message = await message.answer(question_data["question"])
    await store_bot_message(message.chat.id, question_message)

    return question_data

# Boshlang'ich daraja uchun savol berish
@dp.message(lambda message: message.text == "Boshlang'ich daraja")
async def start_beginner_level(message: types.Message):
    global correct_answer_count, general_rule_sent
    await delete_user_message(message)  # Foydalanuvchi xabarini darhol o'chirish
    correct_answer_count[message.chat.id] = 0  # To'g'ri javoblar sonini noldan boshlaymiz
    await clear_previous_bot_messages(message.chat.id)  # Avvalgi bot xabarlarini tozalash

    # Umumiy qoida yuborish
    if not general_rule_sent:  # Umumiy qoida yuborilmagan bo'lsa
        letter_data = korean_letters[current_letter_index]
        general_rule = f"Koreyscha harf: {letter_data['letter']} - k,g\n" \
                       f"• {letter_data['rules'][0]['rule']}\n" \
                       f"• {letter_data['rules'][1]['rule']}\n" \
                       f"• {letter_data['rules'][2]['rule']}"
        rule_message = await message.answer(general_rule)
        await store_bot_message(message.chat.id, rule_message)
        general_rule_sent = True  # Umumiy qoida yuborilganini belgilash

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Bosh menyu")]  # "Bosh menyu" tugmasi qo'shildi
        ],
        resize_keyboard=True  # Klaviaturani o'lchamini moslashtirish
    )

    await ask_question(message)  # Birinchi savolni beramiz
    await message.answer("Yuqoridagi savolga javob bering", reply_markup=keyboard)  # "Savol tayyor!" deb xabar berish

# Foydalanuvchi javobini tekshirish va yangi savol berish
@dp.message()
async def handle_user_response(message: types.Message):
    global current_question_index, current_letter_index, correct_answer_count, general_rule_sent

    # "Bosh menyu" tugmasini tekshirish
    if message.text == "Bosh menyu":
        return await back_to_main_menu(message)  # Bosh menyuga qaytish

    question_data = korean_letters[current_letter_index]["rules"][current_question_index]

    # Avvalgi barcha xabarlarni tozalash
    await delete_user_message(message)
    await clear_previous_bot_messages(message.chat.id)

    # Agar message.chat.id `correct_answer_count`da mavjud bo'lmasa, uni 0 ga teng qilib o'rnatamiz
    if message.chat.id not in correct_answer_count:
        correct_answer_count[message.chat.id] = 0

    if message.text.lower() == question_data["correct_answer"].lower():
        correct_answer_count[message.chat.id] += 1

        # Keyingi savolga o'tamiz
        current_question_index = random.randint(0, len(korean_letters[current_letter_index]["rules"]) - 1)
        
        await ask_question(message)  # Foydalanuvchi to'g'ri javob bergan bo'lsa, keyingi savol beriladi
    else:
        # Noto'g'ri javob bo'lsa, qoida va savolni qayta yuborish
        incorrect_message = await message.answer(f"❌ Qoida: {question_data['rule']}")
        await store_bot_message(message.chat.id, incorrect_message)

        # Savolni qayta yuborish
        await ask_question(message)


# Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
