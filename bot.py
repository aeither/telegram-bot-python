import telebot
import json
import os
from datetime import datetime, timedelta

# ========== ТОКЕН ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ==========
TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
DATA_FILE = 'finance_data.json'

# ========== РАБОТА С ДАННЫМИ ==========
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_user_data(user_id):
    data = load_data()
    if user_id not in data:
        data[user_id] = {
            'balance': 0,
            'transactions': [],
            'budget': None,
            'goals': {}
        }
        save_data(data)
    return data[user_id]

def save_user_data(user_id, user_data):
    data = load_data()
    data[user_id] = user_data
    save_data(data)

def get_month_stats(transactions):
    current_month = datetime.now().strftime("%m")
    month_income = 0
    month_expense = 0
    for t in transactions:
        if t['date'][3:5] == current_month:
            if t['type'] == 'income':
                month_income += t['amount']
            else:
                month_expense += t['amount']
    return month_income, month_expense

def get_category_stats(transactions):
    stats = {}
    for t in transactions:
        if t['type'] == 'expense':
            cat = t['category']
            stats[cat] = stats.get(cat, 0) + t['amount']
    return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    get_user_data(user_id)
    
    text = (
        "🌟 *Добро пожаловать в Финансового Помощника!* 🌟\n\n"
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Я помогу тебе контролировать доходы и расходы.\n\n"
        "📌 *Команды:*\n"
        "/balance - баланс 💰\n"
        "/history - история 📜\n"
        "/stats - статистика 📊\n"
        "/week - статистика за неделю 📅\n"
        "/month - статистика за месяц 📆\n"
        "/set_budget - бюджет 🎯\n"
        "/check_budget - проверить бюджет ⚠️\n"
        "/goal - поставить цель 🏆\n"
        "/goals - мои цели 🎯\n"
        "/delete_last - удалить последнюю 🗑️\n"
        "/reset - сбросить всё 🔄\n"
        "/help - помощь 📖\n\n"
        "💡 *Как записывать:* `+1000 Зарплата` или `-500 Продукты`"
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_command(message):
    text = (
        "📖 *Все команды:*\n\n"
        "/balance - баланс\n"
        "/history - последние 10 операций\n"
        "/stats - расходы по категориям\n"
        "/week - статистика за неделю\n"
        "/month - статистика за месяц\n"
        "/set_budget - установить бюджет\n"
        "/check_budget - проверить бюджет\n"
        "/goal - поставить цель (формат: Цель|Сумма)\n"
        "/goals - список целей\n"
        "/delete_last - удалить последнюю операцию\n"
        "/reset - сбросить все данные\n\n"
        "💡 *Быстрая запись:* +1000 Зарплата или -500 Продукты"
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = str(message.from_user.id)
    user_data = get_user_data(user_id)
    bal = user_data['balance']
    
    if bal >= 0:
        bot.reply_to(message, f"💰 *Баланс:* ✅ {bal} руб.", parse_mode='Markdown')
    else:
        bot.reply_to(message, f"💰 *Баланс:* ❌ {bal} руб.", parse_mode='Markdown')

@bot.message_handler(commands=['history'])
def history(message):
    user_id = str(message.from_user.id)
    user_data = get_user_data(user_id)
    transactions = user_data['transactions']
    
    if not transactions:
        bot.reply_to(message, "📭 *История пуста*", parse_mode='Markdown')
        return
    
    text = "📋 *Последние операции:*\n\n"
    for t in transactions[-10:]:
        sign = "➕" if t['type'] == 'income' else "➖"
        text += f"{sign} {t['amount']} | {t['category']}\n   📅 {t['date']}\n\n"
    
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['stats'])
def stats(message):
    user_id = str(message.from_user.id)
    user_data = get_user_data(user_id)
    stats = get_category_stats(user_data['transactions'])
    
    if not stats:
        bot.reply_to(message, "📊 *Нет данных*", parse_mode='Markdown')
        return
    
    text = "📊 *Расходы по категориям:*\n\n"
    total = sum(stats.values())
    
    for cat, amount in list(stats.items())[:10]:
        percent = (amount / total * 100) if total > 0 else 0
        text += f"📌 {cat}: {amount} руб. ({percent:.0f}%)\n"
    
    text += f"\n💰 *Всего:* {total} руб."
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['week'])
def week_stats(message):
    user_id = str(message.from_user.id)
    user_data = get_user_data(user_id)
    
    week_ago = datetime.now() - timedelta(days=7)
    week_income = 0
    week_expense = 0
    
    for t in user_data['transactions']:
        t_date = datetime.strptime(t['date'], "%d.%m.%Y %H:%M")
        if t_date >= week_ago:
            if t['type'] == 'income':
                week_income += t['amount']
            else:
                week_expense += t['amount']
    
    text = (
        f"📅 *Статистика за неделю*\n\n"
        f"✅ Доходы: +{week_income} руб.\n"
        f"❌ Расходы: -{week_expense} руб.\n"
        f"📈 Итог: {week_income - week_expense} руб."
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['month'])
def month_stats(message):
    user_id = str(message.from_user.id)
    user_data = get_user_data(user_id)
    month_income, month_expense = get_month_stats(user_data['transactions'])
    
    text = (
        f"📆 *Статистика за месяц*\n\n"
        f"✅ Доходы: +{month_income} руб.\n"
        f"❌ Расходы: -{month_expense} руб.\n"
        f"📈 Итог: {month_income - month_expense} руб."
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['set_budget'])
def set_budget(message):
    bot.reply_to(message, "🎯 *Установи бюджет на месяц*\nОтправь сумму, например: `50000`", parse_mode='Markdown')
    bot.register_next_step_handler(message, save_budget)

def save_budget(message):
    user_id = str(message.from_user.id)
    user_data = get_user_data(user_id)
    
    try:
        budget = int(message.text.strip())
        user_data['budget'] = budget
        save_user_data(user_id, user_data)
        bot.reply_to(message, f"✅ *Бюджет:* {budget} руб.", parse_mode='Markdown')
    except:
        bot.reply_to(message, "❌ Отправь число", parse_mode='Markdown')

@bot.message_handler(commands=['check_budget'])
def check_budget(message):
    user_id = str(message.from_user.id)
    user_data = get_user_data(user_id)
    budget = user_data.get('budget')
    
    if not budget:
        bot.reply_to(message, "⚠️ Бюджет не установлен. Используй /set_budget", parse_mode='Markdown')
        return
    
    month_expense = get_month_stats(user_data['transactions'])[1]
    remaining = budget - month_expense
    
    text = (
        f"🎯 *Бюджет:* {budget} руб.\n"
        f"💸 *Потрачено:* {month_expense} руб.\n"
        f"✅ *Осталось:* {remaining} руб."
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['goal'])
def set_goal(message):
    bot.reply_to(message, "🏆 *Поставь цель*\nФормат: `Название|Сумма`\nПример: `Накопить на телефон|30000`", parse_mode='Markdown')
    bot.register_next_step_handler(message, save_goal)

def save_goal(message):
    user_id = str(message.from_user.id)
    user_data = get_user_data(user_id)
    
    try:
        parts = message.text.split('|')
        name = parts[0].strip()
        amount = int(parts[1].strip())
        
        user_data['goals'][name] = {
            'target': amount,
            'saved': 0,
            'created': datetime.now().strftime("%d.%m.%Y")
        }
        save_user_data(user_id, user_data)
        bot.reply_to(message, f"✅ *Цель:* {name} | {amount} руб.", parse_mode='Markdown')
    except:
        bot.reply_to(message, "❌ Формат: `Название|Сумма`", parse_mode='Markdown')

@bot.message_handler(commands=['goals'])
def show_goals(message):
    user_id = str(message.from_user.id)
    user_data = get_user_data(user_id)
    goals = user_data.get('goals', {})
    
    if not goals:
        bot.reply_to(message, "🏆 *Нет целей*. Используй /goal", parse_mode='Markdown')
        return
    
    text = "🏆 *Твои цели:*\n\n"
    for name, goal in goals.items():
        percent = (goal['saved'] / goal['target'] * 100) if goal['target'] > 0 else 0
        text += f"📌 {name}: {goal['saved']}/{goal['target']} руб. ({percent:.0f}%)\n"
    
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['delete_last'])
def delete_last(message):
    user_id = str(message.from_user.id)
    user_data = get_user_data(user_id)
    transactions = user_data['transactions']
    
    if not transactions:
        bot.reply_to(message, "📭 *Нет операций*", parse_mode='Markdown')
        return
    
    last = transactions.pop()
    if last['type'] == 'income':
        user_data['balance'] -= last['amount']
    else:
        user_data['balance'] += last['amount']
    
    save_user_data(user_id, user_data)
    bot.reply_to(message, f"🗑️ *Удалено:* {last['amount']} руб. ({last['category']})", parse_mode='Markdown')

@bot.message_handler(commands=['reset'])
def reset(message):
    bot.reply_to(message, "⚠️ *Уверен?* Отправь `ДА` для подтверждения", parse_mode='Markdown')
    bot.register_next_step_handler(message, confirm_reset)

def confirm_reset(message):
    if message.text.strip().upper() == 'ДА':
        user_id = str(message.from_user.id)
        save_user_data(user_id, {
            'balance': 0,
            'transactions': [],
            'budget': None,
            'goals': {}
        })
        bot.reply_to(message, "✅ *Данные сброшены*", parse_mode='Markdown')
    else:
        bot.reply_to(message, "✅ *Отменено*", parse_mode='Markdown')

# ========== ОБРАБОТКА СООБЩЕНИЙ ==========
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text.strip()
    user_data = get_user_data(user_id)
    
    parts = text.split(maxsplit=1)
    
    if len(parts) == 2 and parts[0][0] in '+-' and parts[0][1:].isdigit():
        amount = int(parts[0][1:])
        category = parts[1]
        
        if parts[0][0] == '+':
            user_data['balance'] += amount
            t_type = 'income'
        else:
            user_data['balance'] -= amount
            t_type = 'expense'
        
        transaction = {
            'type': t_type,
            'amount': amount,
            'category': category,
            'date': datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        user_data['transactions'].append(transaction)
        save_user_data(user_id, user_data)
        
        bot.reply_to(message, f"✅ Записано: {parts[0]} {category}\n💰 Баланс: {user_data['balance']} руб.")
    else:
        bot.reply_to(message, "❓ Не понял. Пиши: +500 Еда или /help")

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("🤖 БОТ ЗАПУЩЕН!")
    bot.polling(none_stop=True)
