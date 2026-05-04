import telebot
import time
import threading
import json
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "⚡ Bot 7/24 Aktivdir!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- AYARLAR --- BURANI DƏYİŞ
TOKEN = "8756196909:AAHMJ53ExNhnm7ewDR_Gho01C6_g9R4aPL8" # TƏCİLİ DƏYİŞ @BotFather-dan
ADMIN_ID = 2083084323
YOUTUBE_URL = "https://youtu.be/QHPnYAeUPnU?si=WlqW1xphnaLTLbz9"
REGISTER_URL = "https://1weucj.life/?open=register&p=mlg1"
AVIATOR_URL = "https://1weucj.life/?open=register&p=mlg1"

bot = telebot.TeleBot(TOKEN)
DB_FILE = "database.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

user_db = load_db()

def is_banned(uid):
    return user_db.get(str(uid), {}).get('status') == 'banned'

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    if is_banned(uid):
        bot.send_message(uid, "⛔ Giriş Məhdudlaşdırılıb\n\nDəstək xidməti ilə əlaqə saxlayın.")
        return

    if uid not in user_db:
        user_db[uid] = {'status': 'new', 'name': message.from_user.first_name, 'proofs': 0, 'test_used': False}
        save_db(user_db)

    user_status = user_db[uid].get('status')
    test_used = user_db[uid].get('test_used', False)

    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    # ADMIN ÜÇÜN HƏMİŞƏ DÜYMƏLƏR VAR
    if int(uid) == ADMIN_ID:
        markup.add(telebot.types.InlineKeyboardButton("🧪 Test Siqnalı", callback_data="test_req"))
        markup.add(telebot.types.InlineKeyboardButton("💎 VIP Aktivasiya", callback_data="show_rules"))
    else:
        if not test_used and user_status!= 'vip':
            markup.add(telebot.types.InlineKeyboardButton("🧪 Test Siqnalı", callback_data="test_req"))
        if user_status!= 'vip':
            markup.add(telebot.types.InlineKeyboardButton("💎 VIP Aktivasiya", callback_data="show_rules"))

    msg = (
        f"Xoş gəldiniz, {message.from_user.first_name}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "✈️ AVIATOR PRO SIGNAL\n"
        "Peşəkar Analitik Siqnal Sistemi\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🧪 STANDART PAKET\n"
        "📊 Dəqiqlik: 70%\n"
        "⏱ Gecikmə: 5-10 saniyə\n"
        "🎁 1 pulsuz test siqnalı mövcuddur\n\n"
        "💎 VIP PAKET\n"
        "📊 Dəqiqlik: 95%\n"
        "⚡️ Gecikmə: 0.1 saniyə\n"
        "🎯 Aktivasiya: Pulsuz\n\n"
        f"📌 VIP giriş üçün yeni 1WIN hesabı tələb olunur\n"
        f"👉 Qeydiyyat: {REGISTER_URL}\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(uid, msg, reply_markup=markup, disable_web_page_preview=True)

@bot.callback_query_handler(func=lambda call: True)
def callback_logic(call):
    uid = str(call.message.chat.id)
    if is_banned(uid): return

    user_data = user_db.get(uid, {})
    user_status = user_data.get('status')
    test_used = user_data.get('test_used', False)

    if call.data == "test_req":
        # ADMIN ÜÇÜN LİMİT YOXDU - birbaşa keçir
        if int(uid) == ADMIN_ID:
            try:
                bot.send_message(ADMIN_ID,
                    f"🧪 ADMİN TEST SORĞUSU\n"
                    f"━━━━━━━━━━━━\n"
                    f"Komanda: /test {uid} 14:20-14:22"
                )
                bot.answer_callback_query(call.id, "Admin test sorğusu göndərildi")
            except Exception as e: print(e)
            return

        # USER ÜÇÜN YOXLA: ƏVVƏL TEST ALIB?
        if test_used or user_status in ['test_sent', 'vip']:
            bot.answer_callback_query(call.id, "❌ Siz artıq test siqnalından istifadə etmisiniz", show_alert=True)
            bot.edit_message_text(
                "⚠️ TEST LİMİTİ DOLUB\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "Hər istifadəçi yalnız 1 dəfə test siqnalı ala bilər.\n\n"
                "💎 VIP sistemə keçmək üçün aşağıdakı düymədən istifadə edin.",
                uid, call.message.message_id,
                reply_markup=telebot.types.InlineKeyboardMarkup().add(
                    telebot.types.InlineKeyboardButton("💎 VIP Aktivasiya", callback_data="show_rules")
                )
            )
            return

        try:
            bot.send_message(ADMIN_ID,
                f"🧪 YENİ TEST SORĞUSU\n"
                f"━━━━━━━━━━━━\n"
                f"👤 İstifadəçi: @{call.from_user.username}\n"
                f"🆔 ID: {uid}\n"
                f"📅 Tarix: {time.strftime('%d.%m.%Y %H:%M')}\n"
                f"━━━━━━━━━━━━\n"
                f"Komanda: /test {uid} 14:20-14:22"
            )
            bot.edit_message_text(
                "⏳ Sorğunuz Qəbul Edildi\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "Test siqnalı analitik tərəfindən hazırlanır.\n\n"
                "📲 Proses: Əvvəlcə 'Hazırlıq' bildirişi alacaqsınız.\n"
                "Bildirişdən 10-15 saniyə sonra siqnal göndəriləcək.\n\n"
                "Xahiş olunur gözləmədə qalın.",
                uid, call.message.message_id
            )
        except Exception as e: print(e)

    elif call.data == "show_rules":
        # YOXLA: TEST ETMƏYİB VIP OLA BİLMƏZ
        if not test_used and user_status not in ['test_sent', 'vip', 'awaiting_proof'] and int(uid)!= ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Əvvəlcə test siqnalını yoxlamalısınız", show_alert=True)
            bot.send_message(uid,
                "⚠️ VIP AKTİVASİYA ŞƏRTİ\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "VIP sistemə keçməzdən əvvəl 1 pulsuz test siqnalını yoxlamalısınız.\n\n"
                "🧪 Test siqnalı almaq üçün /start yazın və 'Test Siqnalı' düyməsini seçin.\n\n"
                "Test etdikdən sonra VIP aktivasiya açılacaq."
            )
            return

        user_db[uid]['status'] = 'awaiting_proof'
        user_db[uid]['proofs'] = 0
        save_db(user_db)

        rules_text = (
            "💎 VIP AKTİVASİYA PROSEDURU\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "⚡️ Maksimum performans üçün aşağıdakı addımları tamamlayın:\n\n"
            f"1️⃣ Rəsmi YouTube Kanalı\n"
            f" Link: {YOUTUBE_URL}\n"
            f" Abunəlik və bildirişlər aktiv edilməlidir\n"
            f" Təsdiq üçün screenshot göndərin 📸\n\n"
            f"2️⃣ Tərəfdaş 1WIN Hesabı\n"
            f" Link: {REGISTER_URL}\n"
            f" Promo kod: yatirimsahesi\n"
            f" Qeydiyyat tamamlandıqdan sonra screenshot göndərin 📸\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "✅ Hər iki mərhələ təsdiqləndikdən sonra VIP giriş avtomatik aktivləşdiriləcək.\n"
            "📌 Qeyd: Şəkillər aydın və tam ölçüdə olmalıdır."
        )
        bot.send_message(uid, rules_text, disable_web_page_preview=True)

    elif call.data.startswith("approve_"):
        target_id = call.data.split("_")[1]
        if target_id in user_db:
            user_db[target_id]['status'] = 'vip'
            user_db[target_id]['proofs'] = 0
            save_db(user_db)
            bot.send_message(target_id,
                "🎉 VIP STATUS AKTİVLƏŞDİRİLDİ\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "✅ Təbriklər. Siz premium istifadəçi statusu əldə etdiniz.\n\n"
                "📊 İmtiyazlarınız:\n"
                "• 95% dəqiqlik dərəcəsi\n"
                "• 0.1 saniyə gecikmə\n"
                "• Prioritet siqnal çatdırılması\n\n"
                "🔥 Növbəti siqnal üçün bildiriş gözləyin."
            )
            bot.answer_callback_query(call.id, "İstifadəçi VIP edildi!")
            bot.edit_message_text(f"✅ TƏSDİQLƏNDİ\nİstifadəçi: {target_id}", ADMIN_ID, call.message.message_id)

    elif call.data.startswith("reject_"):
        target_id = call.data.split("_")[1]
        user_db[target_id]['status'] = 'test_sent' # Test etmiş sayılır, amma VIP deyil
        user_db[target_id]['proofs'] = 0
        save_db(user_db)
        bot.send_message(target_id,
            "❌ SORĞU RƏDD EDİLDİ\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "Təqdim edilən məlumatlar yoxlamadan keçmədi.\n\n"
            "Mümkün səbəblər:\n"
            "• Şəkil keyfiyyəti qeyri-kafidir\n"
            "• Abunəlik təsdiqlənmədi\n"
            "• Qeydiyyat tərəfdaş linkindən aparılmayıb\n\n"
            "🔄 Yenidən cəhd etmək üçün /start əmrindən istifadə edin."
        )
        bot.answer_callback_query(call.id, "İstifadəçi rədd edildi!")
        bot.edit_message_text(f"❌ RƏDD EDİLDİ\nİstifadəçi: {target_id}", ADMIN_ID, call.message.message_id)

@bot.message_handler(commands=['test'])
def admin_test(message):
    if message.from_user.id!= ADMIN_ID: return
    try:
        args = message.text.split(maxsplit=2)
        target_id, vaxt = args[1], args[2]

        # ADMİN ÖZÜNƏ TEST EDƏNDƏ LİMİT YOXDU
        if int(target_id)!= ADMIN_ID:
            user_db[target_id]['status'] = 'test_sent'
            user_db[target_id]['test_used'] = True
            save_db(user_db)

        bot.send_message(target_id,
            "📡 SİQNAL HAZIRLIQ MƏRHƏLƏSİ\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "⏳ Test siqnalı 10-15 saniyə ərzində təqdim ediləcək.\n\n"
            "📲 Xahiş: Cihazı nəzarətdə saxlayın.\n"
            "⚠️ Qeyd: Bu siqnal nümunəvi gecikmə ilə göndərilir."
        )

        bot.send_message(ADMIN_ID, f"✅ Hazırlıq bildirişi göndərildi. 10 saniyə sonra siqnal çatdırılacaq.\nİstifadəçi: {target_id}")
        time.sleep(10)

        msg = (
            "🧪 TEST SİQNALI\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"⏰ Vaxt Aralığı: {vaxt}\n"
            f"🎮 Oyun: Aviator\n"
            f"🎰 Platforma: 1WIN\n"
            f"🔗 Oyun Mühitinə Keçid: {AVIATOR_URL}\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "🐌 Qeyd: Bu siqnalda ~10 saniyə gecikmə müşahidə edildi.\n"
            "💎 VIP sistemdə gecikmə cəmi 0.1 saniyə təşkil edir.\n\n"
            "👇 Daimi və dəqiq siqnallar üçün:"
        )
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("💎 VIP Aktivasiya", callback_data="show_rules"))
        bot.send_message(target_id, msg, reply_markup=markup, disable_web_page_preview=True)
        bot.reply_to(message, "✅ Test prosesi tamamlandı")
    except Exception as e:
        bot.reply_to(message, f"❌ Xəta: {e}\nFormat: /test ID VAXT")

@bot.message_handler(content_types=['photo'])
def handle_proofs(message):
    uid = str(message.chat.id)
    if is_banned(uid): return
    if user_db.get(uid, {}).get('status') == 'awaiting_proof':
        user_db[uid]['proofs'] = user_db[uid].get('proofs', 0) + 1
        proof_count = user_db[uid]['proofs']
        save_db(user_db)

        if proof_count == 1:
            bot.send_message(uid,
                "📩 SƏNƏD 1/2 QƏBUL EDİLDİ ✅\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "İkinci təsdiq sənədini göndərin.\n"
                "⏳ Yoxlanış davam edir."
            )
            bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
            bot.send_message(ADMIN_ID, f"📸 SƏNƏD 1\n👤 İstifadəçi: @{message.from_user.username}\n🆔 ID: {uid}")

        elif proof_count >= 2:
            bot.send_message(uid,
                "📩 SƏNƏD 2/2 QƏBUL EDİLDİ ✅\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "Məlumatlar yoxlama mərkəzinə göndərildi.\n"
                "⏳ Təsdiq prosesi 1-2 dəqiqə ərzində tamamlanacaq.\n"
                "🔔 Nəticə barədə bildiriş alacaqsınız."
            )
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                telebot.types.InlineKeyboardButton("✅ Təsdiqlə", callback_data=f"approve_{uid}"),
                telebot.types.InlineKeyboardButton("❌ Rədd et", callback_data=f"reject_{uid}")
            )
            bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
            bot.send_message(ADMIN_ID,
                f"🔥 YOXLAMA ÜÇÜN HAZIR\n"
                f"━━━━━━━━━━━━\n"
                f"👤 İstifadəçi: @{message.from_user.username}\n"
                f"🆔 ID: {uid}\n"
                f"━━━━━━━━━━━━",
                reply_markup=markup
            )

@bot.message_handler(commands=['aviator'])
def broadcast_signal(message):
    if message.from_user.id!= ADMIN_ID: return
    try:
        vaxt = message.text.split(maxsplit=1)[1]
        vip_signal = (
            "🔥 VIP TƏCİLİ SİQNAL 🔥\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"✈️ Aviator Siqnalı\n\n"
            f"⏰ GİRİŞ VAXTI: {vaxt}\n"
            f"🎯 HƏDƏF ARALIĞI: 10x - 99x\n"
            f"📊 DƏQİQLİK: 95%\n"
            f"⚡️ GECİKMƏ: 0.1 san\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "💰 DƏRHAL GİRİŞ EDİN"
        )
        locked_signal = (
            "🔥 YENİ SİQNAL MÖVCUDDUR 🔥\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"✈️ Aviator Siqnalı\n\n"
            f"⏰ Giriş vaxtı: 🔒 KİLİDLİ\n"
            f"❗️Çəhrayı əmsala bu dəqiqə aralıqında qalxacaq. ⚠️\n"
            f"📊 Proqnoz faizi: 95%\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "🔓 Giriş vaxtını açmaq üçün:\n"
            f"1️⃣ Aşağıdakı linklə qeydiyyatdan keçərək mütləq yeni hesab aç. Əks halda gecikmə baş verəcək. {REGISTER_URL}\n"
            f"2️⃣ Təsdiq sənədi təqdim edin."
        )
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("💎 VIP Aktivasiya", callback_data="show_rules"))

        sent_vip, sent_locked = 0, 0
        for u_id, data in user_db.items():
            if data.get('status') == 'banned': continue
            try:
                if data.get('status') == 'vip':
                    bot.send_message(u_id, vip_signal)
                    sent_vip += 1
                else:
                    bot.send_message(u_id, locked_signal, reply_markup=markup, disable_web_page_preview=True)
                    sent_locked += 1
                time.sleep(0.05)
            except: pass
        bot.reply_to(message,
            f"📢 PAYLANIŞ TAMAMLANDI\n"
            f"━━━━━━━━━━━━\n"
            f"💎 VIP: {sent_vip}\n"
            f"🔒 Standart: {sent_locked}\n"
            f"━━━━━━━━━━━━"
        )
    except:
        bot.reply_to(message, "❌ Format: /aviator VAXT\nNümunə: /aviator 14:20-14:25")

@bot.message_handler(commands=['msg'])
def admin_message(message):
    if message.from_user.id!= ADMIN_ID: return
    try:
        args = message.text.split(maxsplit=2)
        target_id, text = args[1], args[2]
        bot.send_message(target_id, f"📩 ADMİNİSTRASİYA BİLDİRİŞİ\n━━━━━━━━━━━━\n{text}")
        bot.reply_to(message, f"✅ Mesaj {target_id} ID-li istifadəçiyə çatdırıldı")
    except:
        bot.reply_to(message, "❌ Format: /msg ID MƏTN")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.from_user.id!= ADMIN_ID: return
    try:
        target_id = message.text.split()[1]
        if target_id in user_db:
            user_db[target_id]['status'] = 'banned'
            save_db(user_db)
            bot.send_message(target_id, "⛔ GİRİŞ MƏHDUDLAŞDIRILDI\n\nHesabınız sistem tərəfindən bloklanıb.")
            bot.reply_to(message, f"✅ {target_id} bloklandı")
        else:
            bot.reply_to(message, "❌ İstifadəçi tapılmadı")
    except:
        bot.reply_to(message, "❌ Format: /ban ID")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if message.from_user.id!= ADMIN_ID: return
    try:
        target_id = message.text.split()[1]
        if target_id in user_db:
            user_db[target_id]['status'] = 'new'
            user_db[target_id]['test_used'] = False # Blokdan çıxanda test hüqu sıfırlanır
            save_db(user_db)
            bot.send_message(target_id, "✅ MƏHDUDİYYƏT LƏĞV EDİLDİ\n\nSistemə yenidən daxil olmaq üçün /start yazın.")
            bot.reply_to(message, f"✅ {target_id} blokdan çıxarıldı")
    except:
        bot.reply_to(message, "❌ Format: /unban ID")

@bot.message_handler(commands=['users'])
def list_users(message):
    if message.from_user.id!= ADMIN_ID: return
    text = "👥 İSTİFADƏÇİ SİYAHISI\n━━━━━━━━━━━━\n"
    for uid, data in user_db.items():
        status_emoji = {"vip":"💎", "banned":"⛔", "new":"🆕", "test_sent":"🧪", "awaiting_proof":"⏳"}.get(data.get('status'), "❓")
        name = data.get('name', 'Adsız').replace('_', ' ').replace('*', ' ')
        test_icon = "✓" if data.get('test_used') else "✗"
        text += f"{status_emoji} {uid} | {name} | {data.get('status')} | Test:{test_icon}\n"
    if len(text) > 4000: text = text[:4000] + "\n..."
    bot.reply_to(message, text)

@bot.message_handler(commands=['stat'])
def stats(message):
    if message.from_user.id!= ADMIN_ID: return
    total = len(user_db)
    vip = len([u for u in user_db.values() if u.get('status') == 'vip'])
    test = len([u for u in user_db.values() if u.get('test_used') == True])
    new = len([u for u in user_db.values() if u.get('status') == 'new'])
    banned = len([u for u in user_db.values() if u.get('status') == 'banned'])
    bot.reply_to(message,
        f"📊 SİSTEM STATİSTİKASI\n"
        f"━━━━━━━━━━━━\n"
        f"👥 Ümumi istifadəçi: {total}\n"
        f"💎 VIP: {vip}\n"
        f"🧪 Test etmiş: {test}\n"
        f"🆕 Yeni: {new}\n"
        f"⛔ Bloklanmış: {banned}\n"
        f"━━━━━━━━━━━━"
    )

if __name__ == '__main__':
    keep_alive()
    print("⚡ Bot PRO - Admin Limitsiz Versiya işə salındı...")
    bot.infinity_polling(skip_pending=True)
