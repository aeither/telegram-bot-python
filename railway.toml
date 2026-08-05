import telebot
from telebot import types
import json
import os
from datetime import datetime, timedelta

# توکن اختصاصی ربات شما
TOKEN = '8857262027:AAGUB9VgDiTZhoKCBLNSmnXY9c-yxCN9_Qw'
bot = telebot.TeleBot(TOKEN)

DATA_FILE = 'bot_database.json'

default_db = {
    "admin_id": 8567832426,
    "admins": [8567832426],
    "channel_link": "https://t.me/ST_VPN_Official",
    "support_id": "@Rahnemani",
    "card_number": "6037997000000000",
    "card_holder": "نام صاحب حساب",
    "force_channels": [],
    "products": {
        "1": {
            "name": "🔹 ۱ ماهه (۳۰ گیگ)",
            "price": "110,000 تومان",
            "days": 30,
            "configs": []
        },
        "2": {
            "name": "🔹 ۱ ماهه (۵۰ گیگ)",
            "price": "160,000 تومان",
            "days": 30,
            "configs": []
        }
    },
    "user_services": {}
}

def load_db():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_db, f, ensure_ascii=False, indent=4)
        return default_db
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if "admins" not in data:
            data["admins"] = [data.get("admin_id", 8567832426)]
        if "force_channels" not in data:
            data["force_channels"] = []
        return data

def save_db(db):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

db = load_db()
user_states = {}

def is_admin(user_id):
    return user_id in db.get("admins", [db["admin_id"]])

def extract_channel_username(channel_str):
    channel_str = channel_str.strip()
    if channel_str.startswith("https://t.me/"):
        channel_str = channel_str.replace("https://t.me/", "")
    elif channel_str.startswith("http://t.me/"):
        channel_str = channel_str.replace("http://t.me/", "")
    elif channel_str.startswith("t.me/"):
        channel_str = channel_str.replace("t.me/", "")
    
    channel_str = channel_str.split('/')[0]
    
    if not channel_str.startswith("@"):
        channel_str = "@" + channel_str
    return channel_str

def check_user_joined_all(user_id):
    channels = db.get("force_channels", [])
    not_joined = []
    
    for ch in channels:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ['left', 'kicked', 'banned']:
                not_joined.append(ch)
        except Exception:
            # اگر ربات در کانال ادمین نباشد یا آیدی اشتباه باشد، جهت عدم اختلال نادیده گرفته می‌شود
            pass
            
    return not_joined

def build_force_join_markup(not_joined_channels):
    markup = types.InlineKeyboardMarkup()
    for index, ch in enumerate(not_joined_channels, start=1):
        clean_username = ch.replace("@", "")
        markup.add(types.InlineKeyboardButton(f"📢 عضویت در کانال {index}", url=f"https://t.me/{clean_username}"))
    markup.add(types.InlineKeyboardButton("✅ بررسی و تایید عضویت", callback_data="check_join"))
    return markup

def build_main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("💳 خرید اشتراک"),
        types.KeyboardButton("🎁 اکانت تست رایگان"),
        types.KeyboardButton("📊 حساب کاربری"),
        types.KeyboardButton("📱 آموزش اتصال"),
        types.KeyboardButton("💬 پشتیبانی")
    )
    return markup

def build_admin_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📢 مدیریت جوین اجباری"),
        types.KeyboardButton("👥 مدیریت کاربران و کانفیگ‌ها"),
        types.KeyboardButton("➕ افزودن ادمین جدید"),
        types.KeyboardButton("📋 لیست ادمین‌ها"),
        types.KeyboardButton("➕ افزودن کانفیگ به انبار"),
Telegram
ST VPN ⚡️ | اینترنت بدون مرز
​🚀 ST VPN | تجربه سرعت و امنیت واقعی
🌐 مخصوص یوتیوب، اینستاگرام، وب‌گردی و گیمینگ
🔒 سرورهای اختصاصی با پینگ پایین
🛡 ضمانت کامل و پشتیبانی تا آخرین...
VIEW CHANNEL
types.KeyboardButton("📦 مشاهده موجودی انبار"),
        types.KeyboardButton("➕ ساخت تعرفه جدید"),
        types.KeyboardButton("✏️ ویرایش نام و قیمت تعرفه‌ها"),
        types.KeyboardButton("❌ حذف یک تعرفه"),
        types.KeyboardButton("💳 تنظیم شماره کارت"),
        types.KeyboardButton("🔙 خروج از پنل مدیریت")
    )
    return markup

def build_cancel_menu():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton("🔙 بازگشت"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_states.pop(message.from_user.id, None)
    user_id = message.from_user.id
    
    # بررسی جوین اجباری برای کاربران غیر ادمین
    if not is_admin(user_id):
        not_joined = check_user_joined_all(user_id)
        if not_joined:
            text = (
                "⚠️ جهت استفاده از ربات، ابتدا باید در کانال‌های زیر عضو شوید:\n\n"
                "پس از عضویت در کانال‌ها، روی دکمه «✅ بررسی و تایید عضویت» کلیک کنید."
            )
            bot.send_message(message.chat.id, text, reply_markup=build_force_join_markup(not_joined), parse_mode="Markdown")
            return

    first_name = message.from_user.first_name
    welcome_text = (
        f"سلام {first_name} عزیز! 👋\n"
        "به ربات فروش خودکار ST VPN خوش آمدید! ⚡️\n\n"
        "🌐 جهت خرید آنی سرویس یا مدیریت حساب، از دکمه‌های زیر استفاده کنید 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=build_main_menu(), parse_mode="Markdown")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if is_admin(message.from_user.id):
        user_states.pop(message.from_user.id, None)
        bot.send_message(message.chat.id, "⚙️ پنل مدیریت ربات:", reply_markup=build_admin_menu(), parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ شما دسترسی به پنل مدیریت ندارید.")

@bot.message_handler(content_types=['photo'])
def handle_receipt_photo(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id in user_states and user_states[user_id].startswith('waiting_receipt_'):
        prod_key = user_states[user_id].split('_')[-1]
        prod = db["products"].get(prod_key)

        if not prod or len(prod["configs"]) == 0:
            bot.send_message(chat_id, "❌ متأسفانه موجودی این سرویس تمام شده است. مبلغ واریزی را پیگیری کنید.", reply_markup=build_main_menu())
            del user_states[user_id]
            return

        photo_id = message.photo[-1].file_id
        
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ تایید و تحویل سرویس", callback_data=f"approve_{user_id}_{prod_key}"),
            types.InlineKeyboardButton("❌ رد پرداخت", callback_data=f"reject_{user_id}")
        )

        admin_msg = (
            f"📥 فیش واریزی جدید دریافت شد!\n\n"
            f"👤 خریدار: [{message.from_user.first_name}](tg://user?id={user_id})\n"
            f"🆔 شناسه کاربری: {user_id}\n"
            f"📦 سرویس درخواستی: {prod['name']}\n"
            f"💰 مبلغ: {prod['price']}"
        )
        
        for adm in db.get("admins", [db["admin_id"]]):
            try:
                bot.send_photo(adm, photo_id, caption=admin_msg, reply_markup=markup, parse_mode="Markdown")
            except Exception:
                pass
        
        bot.send_message(chat_id, "✅ فیش واریزی شما برای ادمین ارسال شد.\n⏳ پس از بررسی و تایید، کانفیگ به‌صورت خودکار همینجا برای شما ارسال می‌شود.", reply_markup=build_main_menu())
        del user_states[user_id]

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
# دکمه عمومی بازگشت
    if text == "🔙 بازگشت" or text == "🔙 خروج از پنل مدیریت":
        user_states.pop(user_id, None)
        if is_admin(user_id):
            bot.send_message(chat_id, "به پنل اصلی مدیریت بازگشتید.", reply_markup=build_admin_menu())
        else:
            bot.send_message(chat_id, "به منوی اصلی بازگشتید.", reply_markup=build_main_menu())
        return

    # بررسی جوین اجباری برای کاربران عادی قبل از پردازش دکمه‌ها
    if not is_admin(user_id):
        not_joined = check_user_joined_all(user_id)
        if not_joined:
            msg_text = (
                "⚠️ جهت استفاده از ربات، ابتدا باید در کانال‌های زیر عضو شوید:\n\n"
                "پس از عضویت در کانال‌ها، روی دکمه «✅ بررسی و تایید عضویت» کلیک کنید."
            )
            bot.send_message(chat_id, msg_text, reply_markup=build_force_join_markup(not_joined), parse_mode="Markdown")
            return

    # پردازش حالت‌های ورودی ادمین
    if is_admin(user_id) and user_id in user_states:
        state = user_states[user_id]
        
        if state == 'add_force_channel':
            ch_username = extract_channel_username(text)
            if ch_username not in db["force_channels"]:
                db["force_channels"].append(ch_username)
                save_db(db)
                bot.send_message(chat_id, f"✅ کانال {ch_username} به لیست جوین اجباری اضافه شد.\n\n⚠️ نکته: حتماً ربات را در این کانال ادمین کنید.", reply_markup=build_admin_menu(), parse_mode="Markdown")
            else:
                bot.send_message(chat_id, "⚠️ این کانال قبلاً در لیست وجود دارد.", reply_markup=build_admin_menu())
            del user_states[user_id]
            return

        elif state.startswith('add_configs_'):
            prod_key = state.split('_')[-1]
            new_configs = [line.strip() for line in text.split('\n') if line.strip()]
            db["products"][prod_key]["configs"].extend(new_configs)
            save_db(db)
            bot.send_message(chat_id, f"✅ تعداد {len(new_configs)} کانفیگ جدید اضافه شد.", reply_markup=build_admin_menu())
            del user_states[user_id]
            return

        elif state == 'add_new_tariff':
            parts = [p.strip() for p in text.split('|')]
            if len(parts) == 3 and parts[2].isdigit():
                new_key = str(max([int(k) for k in db["products"].keys()] + [0]) + 1)
                db["products"][new_key] = {
                    "name": parts[0],
                    "price": parts[1],
                    "days": int(parts[2]),
                    "configs": []
                }
                save_db(db)
                bot.send_message(chat_id, f"✅ تعرفه {parts[0]} ساخته شد.", reply_markup=build_admin_menu(), parse_mode="Markdown")
            else:
                bot.send_message(chat_id, "❌ فرمت ورودی اشتباه است. دوباره تلاش کنید یا بازگشت را بزنید.", reply_markup=build_cancel_menu())
                return
            del user_states[user_id]
            return

        elif state.startswith('edit_tariff_'):
            prod_key = state.split('_')[-1]
            parts = [p.strip() for p in text.split('|')]
            if len(parts) == 2:
                db["products"][prod_key]["name"] = parts[0]
                db["products"][prod_key]["price"] = parts[1]
                save_db(db)
                bot.send_message(chat_id, "✅ اطلاعات تعرفه به روزرسانی شد.", reply_markup=build_admin_menu())
            else:
                bot.send_message(chat_id, "❌ فرمت اشتباه است. دوباره تلاش کنید یا بازگشت را بزنید.", reply_markup=build_cancel_menu())
                return
            del user_states[user_id]
            return

        elif state == 'set_card_info':
            parts = [p.strip() for p in text.split('|')]
            if len(parts) == 2:
                db["card_number"] = parts[0]
db["card_holder"] = parts[1]
                save_db(db)
                bot.send_message(chat_id, "✅ اطلاعات شماره کارت ذخیره شد.", reply_markup=build_admin_menu())
            else:
                bot.send_message(chat_id, "❌ فرمت اشتباه است. دوباره تلاش کنید یا بازگشت را بزنید.", reply_markup=build_cancel_menu())
                return
            del user_states[user_id]
            return

        elif state == 'add_new_admin':
            if text.isdigit():
                new_admin_id = int(text)
                if new_admin_id not in db["admins"]:
                    db["admins"].append(new_admin_id)
                    save_db(db)
                    bot.send_message(chat_id, f"✅ کاربر {new_admin_id} با موفقیت به عنوان ادمین اضافه شد.", reply_markup=build_admin_menu(), parse_mode="Markdown")
                else:
                    bot.send_message(chat_id, "⚠️ این کاربر در حال حاضر ادمین است.", reply_markup=build_admin_menu())
            else:
                bot.send_message(chat_id, "❌ شناسه کاربری باید عدد باشد. دوباره ارسال کنید یا بازگشت را بزنید.", reply_markup=build_cancel_menu())
                return
            del user_states[user_id]
            return

        elif state.startswith('extend_user_'):
            target_id = state.split('_')[-1]
            if text.isdigit():
                add_days = int(text)
                if target_id in db["user_services"]:
                    curr_expire = datetime.strptime(db["user_services"][target_id]["expire_date"], "%Y-%m-%d %H:%M:%S")
                    if curr_expire < datetime.now():
                        curr_expire = datetime.now()
                    new_expire = curr_expire + timedelta(days=add_days)
                    db["user_services"][target_id]["expire_date"] = new_expire.strftime("%Y-%m-%d %H:%M:%S")
                    save_db(db)
                    bot.send_message(chat_id, f"✅ سرویس کاربر {target_id} به مدت {add_days} روز تمدید شد.", reply_markup=build_admin_menu(), parse_mode="Markdown")
                    try:
                        bot.send_message(target_id, f"🎉 اشتراک شما به مدت {add_days} روز توسط ادمین تمدید شد.")
                    except Exception:
                        pass
            else:
                bot.send_message(chat_id, "❌ تعداد روز باید عدد باشد.", reply_markup=build_cancel_menu())
                return
            del user_states[user_id]
            return

    # منوی ادمین
    if is_admin(user_id):
        if text == "📢 مدیریت جوین اجباری":
            channels = db.get("force_channels", [])
            markup = types.InlineKeyboardMarkup()
            
            msg_text = "📢 تنظیمات جوین اجباری:\n\n"
            if channels:
                msg_text += "📋 کانال‌های فعال:\n"
                for ch in channels:
                    msg_text += f"▫️ {ch}\n"
                    markup.add(types.InlineKeyboardButton(f"❌ حذف کانال {ch}", callback_data=f"del_fch_{ch}"))
            else:
                msg_text += "ℹ️ هیچ کانالی در لیست جوین اجباری ثبت نشده است."
                
            markup.add(types.InlineKeyboardButton("➕ افزودن کانال جدید", callback_data="add_fch"))
            bot.send_message(chat_id, msg_text, reply_markup=markup, parse_mode="Markdown")
            return

        elif text == "👥 مدیریت کاربران و کانفیگ‌ها":
            if not db["user_services"]:
                bot.send_message(chat_id, "ℹ️ در حال حاضر هیچ کاربری سرویس فعال ندارد.", reply_markup=build_admin_menu())
                return
            
            bot.send_message(chat_id, "👥 لیست کاربران و کانفیگ‌های فعال:", parse_mode="Markdown")
            for uid, serv in db["user_services"].items():
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("➕ تمدید اشتراک", callback_data=f"ext_usr_{uid}"),
types.InlineKeyboardButton("❌ حذف سرویس", callback_data=f"rem_usr_{uid}")
                )
                msg_text = (
                    f"👤 شناسه کاربر: {uid}\n"
                    f"📦 سرویس: {serv['plan']}\n"
                    f"⏳ تاریخ انقضا: {serv['expire_date']}\n\n"
                    f"🔗 کانفیگ:\n{serv['config']}"
                )
                bot.send_message(chat_id, msg_text, reply_markup=markup, parse_mode="Markdown")
            return

        elif text == "➕ افزودن ادمین جدید":
            user_states[user_id] = 'add_new_admin'
            bot.send_message(chat_id, "🆔 لطفاً شناسه عددی (Numeric ID) کاربر مورد نظر جهت اضافه شدن به ادمین‌ها را ارسال کنید:", reply_markup=build_cancel_menu(), parse_mode="Markdown")
            return

        elif text == "📋 لیست ادمین‌ها":
            adm_text = "📋 لیست ادمین‌های فعال:\n\n"
            for adm in db.get("admins", [db["admin_id"]]):
                adm_text += f"▫️ {adm}\n"
            bot.send_message(chat_id, adm_text, reply_markup=build_admin_menu(), parse_mode="Markdown")
            return

        elif text == "➕ افزودن کانفیگ به انبار":
            markup = types.InlineKeyboardMarkup()
            for key, prod in db["products"].items():
                markup.add(types.InlineKeyboardButton(f"{prod['name']} (موجودی: {len(prod['configs'])})", callback_data=f"add_conf_{key}"))
            bot.send_message(chat_id, "انتخاب تعرفه جهت شارژ کانفیگ:", reply_markup=markup)
            return

        elif text == "📦 مشاهده موجودی انبار":
            inventory_text = "📦 گزارش موجودی انبار:\n\n"
            for key, prod in db["products"].items():
                inventory_text += f"▫️ {prod['name']} ({prod['price']}): {len(prod['configs'])} عدد\n"
            bot.send_message(chat_id, inventory_text, reply_markup=build_admin_menu(), parse_mode="Markdown")
            return

        elif text == "➕ ساخت تعرفه جدید":
            user_states[user_id] = 'add_new_tariff'
            msg = "📝 فرمت ساخت تعرفه جدید:\nعنوان محصول | قیمت | تعداد روز\n\nمثال:\n🔹 ۳ ماهه (۹۰ گیگ) | 280,000 تومان | 90"
            bot.send_message(chat_id, msg, reply_markup=build_cancel_menu(), parse_mode="Markdown")
            return

        elif text == "✏️ ویرایش نام و قیمت تعرفه‌ها":
            markup = types.InlineKeyboardMarkup()
            for key, prod in db["products"].items():
                markup.add(types.InlineKeyboardButton(f"ویرایش: {prod['name']}", callback_data=f"edit_tar_{key}"))
            bot.send_message(chat_id, "تعرفه مورد نظر را انتخاب کنید:", reply_markup=markup)
            return

        elif text == "❌ حذف یک تعرفه":
            markup = types.InlineKeyboardMarkup()
            for key, prod in db["products"].items():
                markup.add(types.InlineKeyboardButton(f"🗑 حذف: {prod['name']}", callback_data=f"del_tar_{key}"))
            bot.send_message(chat_id, "تعرفه مورد نظر برای حذف را انتخاب کنید:", reply_markup=markup)
            return

        elif text == "💳 تنظیم شماره کارت":
            user_states[user_id] = 'set_card_info'
            msg = "💳 فرمت تنظیم شماره کارت:\nشماره کارت | نام صاحب حساب\n\nمثال:\n6037997000000000 | علی محمدی"
            bot.send_message(chat_id, msg, reply_markup=build_cancel_menu(), parse_mode="Markdown")
            return

    # منوی کاربر عادی
    if text == "💳 خرید اشتراک":
        markup = types.InlineKeyboardMarkup()
        for key, prod in db["products"].items():
            stock = len(prod['configs'])
            status = f"{prod['price']}" if stock > 0 else "❌ اتمام موجودی"
            markup.add(types.InlineKeyboardButton(f"{prod['name']} - {status}", callback_data=f"buy_{key}"))
        bot.send_message(chat_id, "🛒 لطفاً تعرفه مورد نظر خود را انتخاب کنید:", reply_markup=markup, parse_mode="Markdown")

    elif text == "🎁 اکانت تست رایگان":
        bot.send_message(chat_id, f"🎁 جهت دریافت اکانت تست به پشتیبانی پیام دهید:\n👉 {db['support_id']}", reply_markup=build_main_menu())
elif text == "📊 حساب کاربری":
        str_user_id = str(user_id)
        if str_user_id in db["user_services"]:
            serv = db["user_services"][str_user_id]
            expire_date = datetime.strptime(serv["expire_date"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() > expire_date:
                bot.send_message(chat_id, "⚠️ اشتراک شما منقضی شده است.", reply_markup=build_main_menu())
            else:
                remaining = expire_date - datetime.now()
                bot.send_message(chat_id, f"👤 اشتراک فعال شما:\n\n📦 سرویس: {serv['plan']}\n⏳ زمان باقی‌مانده: {remaining.days} روز\n\n🔗 لینک اتصال:\n{serv['config']}", reply_markup=build_main_menu(), parse_mode="Markdown")
        else:
            bot.send_message(chat_id, f"👤 شناسه کاربری: {user_id}\n📦 شما هیچ سرویس فعالی ندارید.", reply_markup=build_main_menu(), parse_mode="Markdown")

    elif text == "📱 آموزش اتصال":
        bot.send_message(chat_id, f"📱 آموزش‌های اتصال:\n👉 {db['channel_link']}", reply_markup=build_main_menu())

    elif text == "💬 پشتیبانی":
        bot.send_message(chat_id, f"💬 پشتیبانی:\n👉 {db['support_id']}", reply_markup=build_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data

    if data == "check_join":
        not_joined = check_user_joined_all(user_id)
        if not_joined:
            bot.answer_callback_query(call.id, "❌ شما هنوز در تمام کانال‌ها عضو نشده‌اید!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "✅ عضویت شما تایید شد!", show_alert=False)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            first_name = call.from_user.first_name
            welcome_text = (
                f"سلام {first_name} عزیز! 👋\n"
                "به ربات فروش خودکار ST VPN خوش آمدید! ⚡️\n\n"
                "🌐 جهت خرید آنی سرویس یا مدیریت حساب، از دکمه‌های زیر استفاده کنید 👇"
            )
            bot.send_message(call.message.chat.id, welcome_text, reply_markup=build_main_menu(), parse_mode="Markdown")
        return

    elif data == "add_fch":
        user_states[user_id] = 'add_force_channel'
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📢 لطفاً آیدی کانال را همراه با @ ارسال کنید (مثلاً @ST_VPN_Official یا لینک کانال):", reply_markup=build_cancel_menu())
        return

    elif data.startswith("del_fch_"):
        ch_to_del = data.replace("del_fch_", "")
        if ch_to_del in db["force_channels"]:
            db["force_channels"].remove(ch_to_del)
            save_db(db)
            bot.answer_callback_query(call.id, "کانال حذف شد")
            bot.send_message(call.message.chat.id, f"🗑 کانال {ch_to_del} از لیست جوین اجباری حذف شد.", reply_markup=build_admin_menu(), parse_mode="Markdown")
        return

    elif data.startswith("add_conf_"):
        prod_key = data.split("_")[-1]
        user_states[user_id] = f"add_configs_{prod_key}"
        prod = db["products"][prod_key]
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"📝 لطفاً کانفیگ‌های جدید {prod['name']} را ارسال کنید (هر خط یک کانفیگ).", reply_markup=build_cancel_menu(), parse_mode="Markdown")
        return

    elif data.startswith("edit_tar_"):
        prod_key = data.split("_")[-1]
        user_states[user_id] = f"edit_tariff_{prod_key}"
        prod = db["products"][prod_key]
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"📝 مشخصات جدید برای {prod['name']}:\nفرمت: عنوان جدید | قیمت جدید", reply_markup=build_cancel_menu(), parse_mode="Markdown")
        return

    elif data.startswith("del_tar_"):
        prod_key = data.split("_")[-1]
if prod_key in db["products"]:
            del db["products"][prod_key]
            save_db(db)
            bot.answer_callback_query(call.id, "حذف شد!")
            bot.send_message(call.message.chat.id, "🗑 تعرفه با موفقیت حذف گردید.", reply_markup=build_admin_menu())
        return

    elif data.startswith("ext_usr_"):
        target_id = data.split("_")[-1]
        user_states[user_id] = f"extend_user_{target_id}"
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"⏳ چند روز قصد دارید به سرویس کاربر {target_id} اضافه کنید؟ (عدد بفرستید):", reply_markup=build_cancel_menu(), parse_mode="Markdown")
        return

    elif data.startswith("rem_usr_"):
        target_id = data.split("_")[-1]
        if target_id in db["user_services"]:
            del db["user_services"][target_id]
            save_db(db)
            bot.answer_callback_query(call.id, "حذف شد")
            bot.send_message(call.message.chat.id, f"🗑 سرویس کاربر {target_id} با موفقیت حذف شد.", reply_markup=build_admin_menu(), parse_mode="Markdown")
        return

    elif data.startswith("buy_"):
        prod_key = data.split("_")[-1]
        prod = db["products"][prod_key]

        if len(prod["configs"]) == 0:
            bot.answer_callback_query(call.id, "❌ موجودی این سرویس تمام شده است.", show_alert=True)
            return

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💳 پرداخت و ارسال فیش", callback_data=f"pay_{prod_key}"))

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            text=f"🛒 فاکتور سفارش:\n\n📦 سرویس: {prod['name']}\n💰 مبلغ: {prod['price']}\n\nجهت دریافت شماره کارت و پرداخت روی دکمه زیر کلیک کنید:",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif data.startswith("pay_"):
        prod_key = data.split("_")[-1]
        prod = db["products"][prod_key]
        
        user_states[user_id] = f"waiting_receipt_{prod_key}"

        card_info = (
            f"💳 اطلاعات پرداخت:\n\n"
            f"📦 سرویس: {prod['name']}\n"
            f"💰 مبلغ قابل واریز: {prod['price']}\n\n"
            f"🔹 شماره کارت:\n{db.get('card_number', 'تنظیم نشده')}\n"
            f"👤 به نام: {db.get('card_holder', 'تنظیم نشده')}\n\n"
            f"⚠️ راهنما: لطفاً مبلغ را واریز کرده و عکس فیش واریزی را همینجا در چت ارسال کنید."
        )
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, card_info, reply_markup=build_cancel_menu(), parse_mode="Markdown")

    elif data.startswith("approve_"):
        parts = data.split("_")
        target_user_id = int(parts[1])
        prod_key = parts[2]
        prod = db["products"].get(prod_key)

        if not prod or len(prod["configs"]) == 0:
            bot.answer_callback_query(call.id, "❌ انبار خالی است! کانفیگ موجود نیست.", show_alert=True)
            return

        delivered_config = prod["configs"].pop(0)
        expire_time = datetime.now() + timedelta(days=prod["days"])

        db["user_services"][str(target_user_id)] = {
            "plan": prod["name"],
            "expire_date": expire_time.strftime("%Y-%m-%d %H:%M:%S"),
            "config": delivered_config
        }
        save_db(db)

        bot.send_message(
            target_user_id,
            f"🎉 پرداخت شما تایید شد!\n\n"
            f"📦 سرویس: {prod['name']}\n"
            f"⏳ اعتبار: {prod['days']} روز\n\n"
            f"🔗 لینک اختصاصی شما:\n{delivered_config}\n\n"
            f"⚠️ این لینک از انبار خارج شد و فقط مخصوص شماست.",
            parse_mode="Markdown"
        )

        bot.edit_message_caption(caption="✅ این پرداخت تایید شد و سرویس به کاربر تحویل گردید.", chat_id=call.message.chat.id, message_id=call.message.id)
