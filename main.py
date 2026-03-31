import telebot
import os
import random
import time
import json
from telebot import types

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8742056784:AAHzOGPUiuhqyi7pIWrPSiBWwtF0LTgAd3M')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://check-eav9.onrender.com')
ADMIN_IDS = [5921095143]  # Add more admin IDs here

bot = telebot.TeleBot(BOT_TOKEN)

# In-memory storage (in production, use a database)
user_data = {}
otp_storage = {}
api_keys = {}

# Helper Functions
def is_admin(user_id):
    return user_id in ADMIN_IDS

def generate_otp():
    return str(random.randint(100000, 999999))

def generate_api_key():
    return f"hitchk_{random.randint(100000, 999999)}_{int(time.time())}"

def get_user_info(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            'plan': 'free',
            'referrals': 0,
            'referred_by': None,
            'api_key': None,
            'hits_today': 0,
            'plan_expiry': None
        }
    return user_data[user_id]

def save_user_data(user_id, data):
    user_data[user_id] = data

# Start Command
@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    first_name = message.from_user.first_name or "User"
    
    # Handle referral links
    if len(message.text.split()) > 1:
        param = message.text.split()[1]
        if param.startswith('ref_'):
            referrer_id = int(param[4:])
            handle_referral(user_id, referrer_id)
    
    # Create user record
    user_info = get_user_info(user_id)
    
    # Welcome message
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton("🚀 Open HIT PRO", url=WEBAPP_URL))
    keyboard.row(types.InlineKeyboardButton("📱 Get OTP", callback_data="get_otp"))
    
    if is_admin(user_id):
        keyboard.row(types.InlineKeyboardButton("🔐 Admin Panel", callback_data="admin_panel"))
    
    welcome_text = f"""
⚡ **Welcome to HIT PRO, {first_name}!**

🌟 **Professional Stripe Auto Hitter**
🔥 **Checkout • Invoice • Billing Gates**

📱 **Your Telegram ID:** `{user_id}`
🌐 **Web App:** [click here]({WEBAPP_URL})

**📊 Your Plan:** {user_info['plan'].upper()}
**🎁 Referrals:** {user_info['referrals']}

**🎯 Plans Available:**
⚡ **Free:** 3 hits/day
⭐ **Silver:** 10 hits/day ($5/week)  
👑 **Gold:** Unlimited ($7/week)

**🎁 Referral Rewards:**
• 4 referrals = 7 days Silver FREE
• 8 referrals = 7 days Gold FREE

**📋 Commands:**
/help - Show all commands
/profile - Your account info
/otp - Get login OTP
"""
    
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        parse_mode='Markdown',
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

# Handle Referrals
def handle_referral(user_id, referrer_id):
    if user_id == referrer_id:
        return  # Can't refer yourself
    
    user_info = get_user_info(user_id)
    if user_info['referred_by']:
        return  # Already referred
    
    # Mark user as referred
    user_info['referred_by'] = referrer_id
    save_user_data(user_id, user_info)
    
    # Update referrer
    referrer_info = get_user_info(referrer_id)
    referrer_info['referrals'] += 1
    
    # Check for automatic upgrades
    if referrer_info['referrals'] >= 8 and referrer_info['plan'] != 'gold':
        referrer_info['plan'] = 'gold'
        referrer_info['plan_expiry'] = int(time.time()) + (7 * 24 * 60 * 60)  # 7 days
        bot.send_message(referrer_id, "🎉 **GOLD UPGRADE!**\nYou got 8 referrals! Upgraded to GOLD for 7 days! 👑")
    elif referrer_info['referrals'] >= 4 and referrer_info['plan'] == 'free':
        referrer_info['plan'] = 'silver'
        referrer_info['plan_expiry'] = int(time.time()) + (7 * 24 * 60 * 60)  # 7 days
        bot.send_message(referrer_id, "🎉 **SILVER UPGRADE!**\nYou got 4 referrals! Upgraded to SILVER for 7 days! ⭐")
    
    save_user_data(referrer_id, referrer_info)
    
    # Notify both users
    bot.send_message(user_id, f"🎁 **Welcome!** You were referred by user #{referrer_id}")
    bot.send_message(referrer_id, f"🎁 **New Referral!** User #{user_id} joined using your link!")

# OTP Command
@bot.message_handler(commands=['otp'])
def send_otp_command(message):
    send_otp(message.chat.id)

def send_otp(chat_id):
    user_id = chat_id
    otp = generate_otp()
    otp_storage[user_id] = {
        'code': otp,
        'timestamp': time.time(),
        'expires': time.time() + 600  # 10 minutes
    }
    
    otp_text = f"""
🔐 **HIT PRO Verification Code**

Your OTP: `{otp}`

⏰ **Valid for 10 minutes**
🌐 **Enter on:** {WEBAPP_URL}

⚠️ **Don't share this code with anyone!**
"""
    
    bot.send_message(chat_id, otp_text, parse_mode='Markdown')

# Profile Command
@bot.message_handler(commands=['profile'])
def profile_command(message):
    user_id = message.from_user.id
    user_info = get_user_info(user_id)
    
    plan_emoji = {'free': '⚡', 'silver': '⭐', 'gold': '👑'}
    
    profile_text = f"""
👤 **Your HIT PRO Profile**

**📱 User ID:** `{user_id}`
**📊 Plan:** {plan_emoji.get(user_info['plan'], '⚡')} {user_info['plan'].upper()}
**🎁 Referrals:** {user_info['referrals']}
**🔥 Hits Today:** {user_info['hits_today']}
**🔑 API Key:** {user_info['api_key'][:12] + '...' if user_info['api_key'] else 'Not generated'}

**🔗 Your Referral Link:**
`https://t.me/HITPROOBOT?start=ref_{user_id}`

**💡 Share your link to earn rewards!**
"""
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton("🚀 Open Web App", url=WEBAPP_URL))
    keyboard.row(types.InlineKeyboardButton("📱 Get New OTP", callback_data="get_otp"))
    
    bot.send_message(message.chat.id, profile_text, parse_mode='Markdown', reply_markup=keyboard)

# Help Command
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = f"""
🆘 **HIT PRO Help & Commands**

**👥 User Commands:**
/start - Welcome & main menu
/profile - Your account information  
/otp - Get login verification code
/help - Show this help menu

**🌐 Web App:** {WEBAPP_URL}
**📞 Support:** Contact @username5921095143

**💰 Plans & Pricing:**
⚡ **Free:** 3 hits/day
⭐ **Silver:** 10 hits/day ($5/week)
👑 **Gold:** Unlimited hits ($7/week)

**🎁 Referral System:**
• Share your link: get rewards
• 4 referrals = Free Silver (7 days)
• 8 referrals = Free Gold (7 days)

**🔥 Features:**
• Stripe Checkout Testing
• Invoice Payment Testing  
• Billing Portal Testing
• Proxy Support (Premium)
• Real-time Results
"""
    
    if is_admin(message.from_user.id):
        help_text += """

**🔐 Admin Commands:**
/admin - Admin panel
/upgrade [user_id] [plan] - Upgrade user
/genkey - Generate API key
/broadcast [message] - Send to all users
/stats - Bot statistics
"""
    
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

# Admin Commands
@bot.message_handler(commands=['admin'])
def admin_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ **Access Denied!** Admin only command.")
        return
    
    stats_text = f"""
🔐 **HIT PRO Admin Panel**

**📊 Bot Statistics:**
👥 **Total Users:** {len(user_data)}
⚡ **Free Users:** {len([u for u in user_data.values() if u['plan'] == 'free'])}
⭐ **Silver Users:** {len([u for u in user_data.values() if u['plan'] == 'silver'])}
👑 **Gold Users:** {len([u for u in user_data.values() if u['plan'] == 'gold'])}
🔑 **API Keys:** {len(api_keys)}

**🎁 Total Referrals:** {sum(u['referrals'] for u in user_data.values())}

**⚡ Admin Commands:**
/upgrade [user_id] [plan] - Upgrade user
/genkey - Generate new API key  
/broadcast [message] - Broadcast message
/stats - Detailed statistics
"""
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton("📊 Full Stats", callback_data="admin_stats"))
    keyboard.row(types.InlineKeyboardButton("👥 User List", callback_data="admin_users"))
    
    bot.send_message(message.chat.id, stats_text, parse_mode='Markdown', reply_markup=keyboard)

@bot.message_handler(commands=['upgrade'])
def upgrade_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ **Access Denied!**")
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.send_message(message.chat.id, "Usage: `/upgrade [user_id] [free/silver/gold]`", parse_mode='Markdown')
            return
        
        target_user = int(parts[1])
        new_plan = parts[2].lower()
        
        if new_plan not in ['free', 'silver', 'gold']:
            bot.send_message(message.chat.id, "❌ Invalid plan! Use: free, silver, or gold")
            return
        
        user_info = get_user_info(target_user)
        old_plan = user_info['plan']
        user_info['plan'] = new_plan
        
        if new_plan != 'free':
            user_info['plan_expiry'] = int(time.time()) + (7 * 24 * 60 * 60)  # 7 days
        else:
            user_info['plan_expiry'] = None
        
        save_user_data(target_user, user_info)
        
        # Notify admin
        bot.send_message(message.chat.id, f"✅ **User #{target_user}** upgraded: {old_plan.upper()} → {new_plan.upper()}")
        
        # Notify user
        plan_emoji = {'free': '⚡', 'silver': '⭐', 'gold': '👑'}
        try:
            bot.send_message(target_user, f"🎉 **Plan Upgraded!**\n\nYour plan: {plan_emoji[new_plan]} **{new_plan.upper()}**\n\nEnjoy your new features!")
        except:
            pass  # User might have blocked the bot
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['genkey'])
def genkey_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ **Access Denied!**")
        return
    
    api_key = generate_api_key()
    api_keys[api_key] = {
        'created_by': message.from_user.id,
        'created_at': int(time.time()),
        'active': True
    }
    
    key_text = f"""
🔑 **New API Key Generated**

**Key:** `{api_key}`

⚠️ **Save this key securely!**
🔧 **Use in API requests**
"""
    
    bot.send_message(message.chat.id, key_text, parse_mode='Markdown')

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ **Access Denied!**")
        return
    
    try:
        broadcast_text = message.text[11:]  # Remove '/broadcast '
        if not broadcast_text:
            bot.send_message(message.chat.id, "Usage: `/broadcast [your message]`", parse_mode='Markdown')
            return
        
        sent = 0
        failed = 0
        
        for user_id in user_data.keys():
            try:
                bot.send_message(user_id, f"📢 **HIT PRO Announcement**\n\n{broadcast_text}", parse_mode='Markdown')
                sent += 1
            except:
                failed += 1
        
        bot.send_message(message.chat.id, f"📢 **Broadcast Complete!**\n✅ Sent: {sent}\n❌ Failed: {failed}")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

# Callback Handlers
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "get_otp":
        send_otp(call.message.chat.id)
        bot.answer_callback_query(call.id, "🔐 OTP sent!")
        
    elif call.data == "admin_panel":
        if is_admin(call.from_user.id):
            admin_command(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Access Denied!")
    
    elif call.data == "admin_stats":
        if is_admin(call.from_user.id):
            # Detailed stats
            stats = f"""
📊 **Detailed Statistics**

👥 **Users by Plan:**
⚡ Free: {len([u for u in user_data.values() if u['plan'] == 'free'])}
⭐ Silver: {len([u for u in user_data.values() if u['plan'] == 'silver'])}  
👑 Gold: {len([u for u in user_data.values() if u['plan'] == 'gold'])}

🎁 **Referral Stats:**
Total Referrals: {sum(u['referrals'] for u in user_data.values())}
Top Referrer: {max(user_data.keys(), key=lambda x: user_data[x]['referrals'], default='None')}

🔑 **API Keys:** {len(api_keys)} active
💾 **OTP Cache:** {len(otp_storage)} codes
"""
            bot.send_message(call.message.chat.id, stats, parse_mode='Markdown')
        bot.answer_callback_query(call.id)

# Error Handler
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text and not message.text.startswith('/'):
        help_text = "🤖 **Unknown command!**\n\nUse /help to see available commands.\n\n🚀 **Quick Access:** " + WEBAPP_URL
        bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

# Keep the bot running
if __name__ == "__main__":
    print("🤖 HIT PRO Bot started!")
    print(f"🌐 Web App: {WEBAPP_URL}")
    print(f"👑 Admins: {ADMIN_IDS}")
    bot.infinity_polling()
