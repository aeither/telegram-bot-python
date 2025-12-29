import os, json, uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)
from config import TOKEN, OWNER_ID, FORCE_CHANNEL

# ---------- PATHS ----------
FILES_DB = "data/files.json"
ADMINS_DB = "data/admins.json"
USERS_DB = "data/users.json"
MESSAGES_DB = "data/messages.json"
CLOSED_CHATS_DB = "data/closed_chats.json"

os.makedirs("files/free", exist_ok=True)
os.makedirs("files/paid", exist_ok=True)
os.makedirs("data", exist_ok=True)

for db in [FILES_DB, ADMINS_DB, USERS_DB, MESSAGES_DB, CLOSED_CHATS_DB]:
    if not os.path.exists(db):
        if db == ADMINS_DB:
            json.dump([OWNER_ID], open(db, "w", encoding="utf-8"))
        elif db == CLOSED_CHATS_DB:
            json.dump([], open(db, "w", encoding="utf-8"))
        else:
            json.dump([], open(db, "w", encoding="utf-8"))

# ---------- UTILS ----------
def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def is_admin(uid):
    return uid in load(ADMINS_DB)

async def is_member(bot, uid):
    try:
        m = await bot.get_chat_member(FORCE_CHANNEL, uid)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False

def load_users():
    data = load(USERS_DB)
    return data if isinstance(data, list) else []

def add_user(uid):
    users = load_users()
    if uid not in users:
        users.append(uid)
        save(USERS_DB, users)

def load_files():
    data = load(FILES_DB)
    return data if isinstance(data, list) else []

# ---------- KEYBOARDS ----------
def main_reply_keyboard():
    # منوی ثابت کنار دکمه سنجاق
    return ReplyKeyboardMarkup(
        [["🔙 Back to Main Menu"]], 
        resize_keyboard=True
    )

def join_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/Hq_Cracker")],
        [InlineKeyboardButton("✅ Verify Membership", callback_data="check_join")]
    ])

def user_menu(is_admin_user=False):
    kb = [
        [InlineKeyboardButton("📂 Free Files", callback_data="free_list")],
        [InlineKeyboardButton("💰 Paid Files", callback_data="paid_list")],
        [InlineKeyboardButton("📞 Contact Admin", callback_data="contact")],
        [InlineKeyboardButton("📩 Message Admin", callback_data="message_admin")]
    ]
    if is_admin_user:
        kb.append([InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(kb)

def admin_panel():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 Upload Free File", callback_data="upload_free")],
        [InlineKeyboardButton("💰 Upload Paid File", callback_data="upload_paid")],
        [InlineKeyboardButton("📊 File Stats", callback_data="stats")],
        [InlineKeyboardButton("📣 Broadcast Message", callback_data="admin_broadcast")],
        [InlineKeyboardButton("👥 Manage Admins", callback_data="manage_admins")],
        [InlineKeyboardButton("👁 User Stats", callback_data="user_stats")]
    ])

def back_button(is_admin_user=False):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_main")]])

def close_chat_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔒 Close Chat", callback_data="close_this_chat")]])

# ---------- FUNCTIONS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not await is_member(context.bot, uid):
        await update.message.reply_text("❌ You must join the channel first:", reply_markup=join_keyboard())
        return
    add_user(uid)
    welcome_text = "🚀 Welcome to Hq_Cracker!\n\nPremium cracked accounts & high-quality combo lists."
    # ارسال منوی شیشه‌ای + فعال کردن منوی کنار سنجاق
    await update.message.reply_text(
        welcome_text, 
        reply_markup=user_menu(is_admin(uid))
    )
    await update.message.reply_text("⚡ Quick Navigation Enabled:", reply_markup=main_reply_keyboard())

async def unblock_user(update, context):
    if update.effective_user.id != OWNER_ID: return
    try:
        target_uid = int(context.args[0])
        closed = load(CLOSED_CHATS_DB)
        if target_uid in closed:
            closed.remove(target_uid); save(CLOSED_CHATS_DB, closed)
            await update.message.reply_text(f"✅ User {target_uid} unblocked.")
        else: await update.message.reply_text("❌ Not blocked.")
    except: await update.message.reply_text("❌ Usage: /unblock USER_ID")

async def broadcast_new_file(context, file_name, file_type, description=None, price=None, fid=None):
    users = load_users()
    text = f"📢 New {file_type} file: {file_name}"
    for uid in users:
        try: await context.bot.send_message(uid, text)
        except: continue

# ---------- BUTTONS ----------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    try: await q.answer()
    except: pass
    uid = q.from_user.id
    data = load_files()

    if q.data == "check_join":
        if await is_member(context.bot, uid):
            await q.message.edit_text("✅ Verified.", reply_markup=user_menu(is_admin(uid)))
        else: await q.answer("❌ Join first!", show_alert=True)

    elif q.data == "back_main":
        context.user_data.clear()
        await q.message.edit_text("🔹 Main Menu", reply_markup=user_menu(is_admin(uid)))

    elif q.data == "free_list":
        kb = [[InlineKeyboardButton(f"📄 {f['name']} ({f['downloads']})", callback_data=f"get_{f['id']}")] for f in data if f["type"] == "free"]
        await q.message.reply_text("📂 Free Files:", reply_markup=InlineKeyboardMarkup(kb) if kb else back_button(is_admin(uid)))

    elif q.data.startswith("get_"):
        fid = q.data.replace("get_", "")
        for f in data:
            if f["id"] == fid:
                path = f"files/free/{f['name']}"
                f["downloads"] += 1; save(FILES_DB, data)
                await q.message.reply_document(open(path, "rb"))
                return

    elif q.data == "paid_list":
        kb = [[InlineKeyboardButton(f"📄 {f['name']} - ${f['price']}", callback_data=f"buy_{f['id']}")] for f in data if f["type"] == "paid"]
        await q.message.reply_text("💰 Paid Files:", reply_markup=InlineKeyboardMarkup(kb) if kb else back_button(is_admin(uid)))

    elif q.data.startswith("buy_"):
        fid = q.data.replace("buy_", "")
        for f in data:
            if f["id"] == fid:
                await context.bot.send_message(OWNER_ID, f"📥 Paid file request from user {uid}:\nFile: {f['name']}\nPrice: ${f['price']}")
                await q.message.reply_text(f"✅ Purchase request sent to admin.")

    elif q.data == "contact":
        await q.message.reply_text("📞 Contact: @Cracker_Proo / @Ali_storr", reply_markup=back_button(is_admin(uid)))

    elif q.data == "message_admin":
        context.user_data["msg_to_admin"] = True
        await q.message.reply_text("✏️ Send your message to admin:", reply_markup=back_button(is_admin(uid)))

    elif q.data == "admin_panel" and is_admin(uid):
        await q.message.reply_text("👑 Admin Panel", reply_markup=admin_panel())

    elif q.data == "upload_free" and is_admin(uid):
        context.user_data["upload"] = "free"
        await q.message.reply_text("📤 Send free file")

    elif q.data == "upload_paid" and is_admin(uid):
        context.user_data["upload"] = "paid"
        await q.message.reply_text("💰 Send paid file")

    elif q.data == "admin_broadcast" and is_admin(uid):
        context.user_data["broadcasting"] = True
        await q.message.reply_text("📣 Send message/photo to broadcast:")

    elif q.data == "stats" and is_admin(uid):
        text = "📊 File Stats:\n\n" + "\n".join([f"📄 {f['name']} -> {f['downloads']}" for f in data])
        await q.message.reply_text(text, reply_markup=back_button(True))

    elif q.data == "user_stats" and is_admin(uid):
        users = load_users()
        await q.message.reply_text(f"👥 Total Users: {len(users)}", reply_markup=back_button(True))

    elif q.data == "close_this_chat" and uid == OWNER_ID:
        try:
            target_uid = int(q.message.text.split("user ")[1].split(":")[0].strip())
            closed = load(CLOSED_CHATS_DB)
            if target_uid not in closed:
                closed.append(target_uid); save(CLOSED_CHATS_DB, closed)
            await q.message.edit_text(q.message.text + "\n\n🔒 (CHAT CLOSED)")
            await context.bot.send_message(target_uid, "🚫 Admin closed this chat.")
        except: await q.answer("Error")

# ---------- HANDLERS ----------
async def add_admin(update, context):
    if update.effective_user.id != OWNER_ID: return
    try:
        uid = int(context.args[0])
        admins = load(ADMINS_DB)
        if uid not in admins: admins.append(uid); save(ADMINS_DB, admins)
        await update.message.reply_text("✅ Admin added")
    except: pass

async def del_admin(update, context):
    if update.effective_user.id != OWNER_ID: return
    try:
        uid = int(context.args[0])
        admins = load(ADMINS_DB)
        if uid in admins and uid != OWNER_ID: admins.remove(uid); save(ADMINS_DB, admins)
        await update.message.reply_text("✅ Admin removed")
    except: pass

async def handle_upload(update, context):
    if not is_admin(update.effective_user.id): return
    upload_type = context.user_data.get("upload")
    if not upload_type or not update.message.document: return
    doc = update.message.document
    fid = uuid.uuid4().hex[:6]
    path = f"files/{upload_type}/{doc.file_name}"
    await (await doc.get_file()).download_to_drive(path)
    if upload_type == "free":
        data = load_files(); data.append({"id":fid,"name":doc.file_name,"type":"free","downloads":0}); save(FILES_DB, data)
        await update.message.reply_text("✅ Uploaded"); await broadcast_new_file(context, doc.file_name, "free")
        context.user_data.clear()
    else:
        context.user_data["paid_file"] = {"id":fid,"file_path":path,"type":"paid"}
        await update.message.reply_text("💰 Name | Description | Price")

async def handle_paid_details(update, context):
    try:
        name, desc, price = [x.strip() for x in update.message.text.split("|")]
        finfo = context.user_data["paid_file"]
        finfo.update({"name":name,"description":desc,"price":price,"downloads":0})
        data = load_files(); data.append(finfo); save(FILES_DB, data)
        await update.message.reply_text("✅ Paid File Saved"); await broadcast_new_file(context, name, "paid", desc, price, finfo["id"])
        context.user_data.clear()
    except: await update.message.reply_text("❌ Format: Name | Description | Price")

async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text or ""

    # واکنش به دکمه بازگشت کنار سنجاق
    if text == "🔙 Back to Main Menu":
        context.user_data.clear()
        await update.message.reply_text("🔹 Main Menu", reply_markup=user_menu(is_admin(uid)))
        return

    if context.user_data.get("broadcasting") and is_admin(uid):
        users = load_users()
        count = 0
        for user_id in users:
            try: await update.message.copy(chat_id=user_id); count += 1
            except: continue
        context.user_data.pop("broadcasting")
        await update.message.reply_text(f"✅ Sent to {count} users.")
        return

    if uid == OWNER_ID and update.message.reply_to_message:
        msg_text = update.message.reply_to_message.text
        if "Message from user" in msg_text:
            try:
                target_uid = int(msg_text.split("user ")[1].split(":")[0].strip())
                await context.bot.send_message(target_uid, f"💬 Admin Reply:\n{update.message.text}")
                await update.message.reply_text("✅ Sent.")
                return
            except: pass

    if context.user_data.get("msg_to_admin"):
        if uid in load(CLOSED_CHATS_DB):
            await update.message.reply_text("❌ Chat is closed.")
            return
        await context.bot.send_message(OWNER_ID, f"📩 Message from user {uid}:\n{text}", reply_markup=close_chat_kb())
        await update.message.reply_text("✅ Sent to admin.")

# ---------- RUN ----------
app = ApplicationBuilder().token(TOKEN).connect_timeout(30).read_timeout(30).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addadmin", add_admin))
app.add_handler(CommandHandler("deladmin", del_admin))
app.add_handler(CommandHandler("unblock", unblock_user))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.Document.ALL, handle_upload))
app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_router))
print("Bot is running...")
app.run_polling()
