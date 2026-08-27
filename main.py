import os
import sqlite3
import hashlib
from datetime import date

import telebot


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN تنظیم نشده است.")

bot = telebot.TeleBot(TOKEN)

DB_NAME = "edit_points.db"
DAILY_LIMIT = 3


# =========================
# DATABASE
# =========================

def db():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            points INTEGER DEFAULT 0,
            daily_count INTEGER DEFAULT 0,
            last_date TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS edits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            file_hash TEXT UNIQUE,
            score INTEGER,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# =========================
# LEVEL SYSTEM
# =========================

def get_level(points):
    levels = [
        (10000, 8, "💎👑"),
        (5000, 7, "👑"),
        (2000, 6, "🔥"),
        (1000, 5, "💎"),
        (500, 4, "🥇"),
        (250, 3, "🥈"),
        (100, 2, "🥉"),
        (0, 1, "🪵"),
    ]

    for required, level, icon in levels:
        if points >= required:
            return level, icon

    return 1, "🪵"


# =========================
# USER
# =========================

def register_user(user):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO users
        (user_id, username, first_name, points, daily_count, last_date)
        VALUES (?, ?, ?, 0, 0, ?)
    """, (
        user.id,
        user.username,
        user.first_name,
        str(date.today())
    ))

    cur.execute("""
        UPDATE users
        SET username = ?, first_name = ?
        WHERE user_id = ?
    """, (
        user.username,
        user.first_name,
        user.id
    ))

    conn.commit()
    conn.close()


def get_user(user_id):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT points, daily_count, last_date
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    result = cur.fetchone()
    conn.close()

    return result


def add_points(user_id, points):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET points = points + ?
        WHERE user_id = ?
    """, (points, user_id))

    conn.commit()
    conn.close()


def increase_daily_count(user_id):
    today = str(date.today())

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT last_date
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    result = cur.fetchone()

    if not result:
        conn.close()
        return

    last_date = result[0]

    if last_date != today:
        cur.execute("""
            UPDATE users
            SET daily_count = 1,
                last_date = ?
            WHERE user_id = ?
        """, (today, user_id))
    else:
        cur.execute("""
            UPDATE users
            SET daily_count = daily_count + 1
            WHERE user_id = ?
        """, (user_id,))

    conn.commit()
    conn.close()


# =========================
# RANK
# =========================

def get_rank(user_id):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE points > (
            SELECT points
            FROM users
            WHERE user_id = ?
        )
    """, (user_id,))

    result = cur.fetchone()
    conn.close()

    return (result[0] if result else 0) + 1


# =========================
# DUPLICATE CHECK
# =========================

def is_duplicate(file_hash):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM edits
        WHERE file_hash = ?
    """, (file_hash,))

    result = cur.fetchone()
    conn.close()

    return result is not None


def save_edit(user_id, file_hash, score):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO edits
        (user_id, file_hash, score, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        file_hash,
        score,
        str(date.today())
    ))

    conn.commit()
    conn.close()


# =========================
# SCORE
# =========================

def calculate_score(file_size, duration):
    """
    نسخه اولیه امتیازدهی.
    بعداً AI واقعی برای کیفیت ادیت، آهنگ،
    هماهنگی و خلاقیت اضافه می‌کنیم.
    """

    quality = 30
    audio = 20
    effects = 20
    sync = 20
    creativity = 10

    # کمی بررسی ساده فایل
    if file_size < 1_000_000:
        quality -= 5

    if duration and duration < 3:
        creativity -= 2

    score = quality + audio + effects + sync + creativity

    return max(0, min(score, 100))


def score_icon(score):
    if score >= 90:
        return "🟢"
    elif score >= 80:
        return "🔵"
    elif score >= 70:
        return "🟡"
    elif score >= 60:
        return "🟠"
    else:
        return "🔴"


# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):
    register_user(message.from_user)

    bot.reply_to(
        message,
        """
🎬 به «مهندس ادیت» خوش آمدی!

ادیتت رو بفرست تا بررسیش کنم.

⭐ نمره از 100
🏆 دریافت Points
📈 Level
🥇 Ranking

📌 روزانه حداکثر 3 ادیت می‌توانی ارسال کنی.

دستورات:
/points - مشاهده امتیاز
/rank - جدول برترین‌ها
"""
    )


# =========================
# POINTS
# =========================

@bot.message_handler(commands=["points"])
def points_command(message):
    register_user(message.from_user)

    user = get_user(message.from_user.id)

    points = user[0]
    level, icon = get_level(points)
    rank = get_rank(message.from_user.id)

    bot.reply_to(
        message,
        f"""
👤 {message.from_user.first_name}

🏆 Points: {points}
{icon} Level: {level}
🥇 Rank: #{rank}
"""
    )


# =========================
# RANKING
# =========================

@bot.message_handler(commands=["rank"])
def rank_command(message):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, username, first_name, points
        FROM users
        ORDER BY points DESC
        LIMIT 10
    """)

    users = cur.fetchall()
    conn.close()

    if not users:
        bot.reply_to(message, "هنوز کسی Point ندارد.")
        return

    text = "🏆 TOP 10 EDITORS\n\n"

    medals = ["🥇", "🥈", "🥉"]

    for i, user in enumerate(users, start=1):

        user_id, username, first_name, points = user

        name = first_name or username or str(user_id)

        level, icon = get_level(points)

        medal = medals[i - 1] if i <= 3 else f"{i}️⃣"

        text += (
            f"{medal} {name}\n"
            f"   {icon} Level {level} | "
            f"🏆 {points} Points\n\n"
        )

    bot.reply_to(message, text)


# =========================
# VIDEO
# =========================

@bot.message_handler(content_types=["video"])
def receive_video(message):

    register_user(message.from_user)

    user = get_user(message.from_user.id)

    points = user[0]
    daily_count = user[1]
    last_date = user[2]

    today = str(date.today())

    if last_date != today:
        daily_count = 0

    if daily_count >= DAILY_LIMIT:
        bot.reply_to(
            message,
            """
⛔ سهم امروزت تمام شده.

📅 حداکثر 3 ادیت در روز می‌توانی ارسال کنی.
فردا دوباره می‌توانی ادیت بفرستی. 🎬
"""
        )
        return

    wait = bot.reply_to(
        message,
        "⏳ ادیت دریافت شد...\nدر حال بررسی 🎬🎵"
    )

    try:
        file_info = bot.get_file(message.video.file_id)

        file_data = bot.download_file(file_info.file_path)

        file_hash = hashlib.sha256(file_data).hexdigest()

        if is_duplicate(file_hash):

            bot.edit_message_text(
                "❌ این ادیت قبلاً ثبت شده است.\n\n🏆 Point جدیدی دریافت نمی‌کنی.",
                message.chat.id,
                wait.message_id
            )

            return

        file_size = len(file_data)

        duration = message.video.duration or 0

        score = calculate_score(
            file_size,
            duration
        )

        add_points(
            message.from_user.id,
            score
        )

        increase_daily_count(
            message.from_user.id
        )

        save_edit(
            message.from_user.id,
            file_hash,
            score
        )

        new_points = get_user(
            message.from_user.id
        )[0]

        level, icon = get_level(new_points)

        rank = get_rank(
            message.from_user.id
        )

        color = score_icon(score)

        remaining = DAILY_LIMIT - (
            get_user(message.from_user.id)[1]
        )

        text = f"""
🎬 نتیجه بررسی ادیت

{color} نمره: {score}/100

📹 کیفیت: 30/30
🎵 آهنگ: 20/20
✨ افکت: 20/20
🎯 هماهنگی: 20/20
💡 خلاقیت: 10/10

━━━━━━━━━━━━

🏆 +{score} Points

💰 مجموع: {new_points} Points

{icon} Level: {level}

🥇 Rank: #{rank}

📅 ادیت باقی‌مانده امروز: {remaining}
"""

        bot.edit_message_text(
            text,
            message.chat.id,
            wait.message_id
        )

    except Exception as e:

        print("ERROR:", e)

        bot.edit_message_text(
            "❌ در بررسی ادیت مشکلی پیش آمد. دوباره امتحان کن.",
            message.chat.id,
            wait.message_id
        )


# =========================
# RUN
# =========================

print("🎬 Mohandes Edit Bot is running...")

bot.infinity_polling(
    skip_pending=True
)
