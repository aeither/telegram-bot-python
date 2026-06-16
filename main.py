# -*- coding: utf-8 -*-
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

name_map = {
    "songbai": "94松白会所部长",
    "honghua": "94红花会所部长",
    "minsheng": "94民生会所部长",
    "huafa": "94华发会所部长",
    "tianyuan": "94田园会所部长",
    "tianliao": "94田寮会所部长",
    "jinyuwan": "94金御湾会所部长",
    "kangle": "95-96康乐会所部长",
    "gongming": "光明链接",
    "jinyu": "金鱼",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = context.args[0] if context.args else None
    user_id = update.effective_user.id

    if code and code in name_map:
        chinese = name_map[code]
        print(f"用户 {user_id} 通过 {code}（{chinese}）进入")
        await update.message.reply_text(f"兄弟 已经转接：{chinese}")
    elif code:
        print(f"用户 {user_id} 通过 {code} 进入")
        await update.message.reply_text(f"兄弟 已经转接：{code}")
    else:
        print(f"用户 {user_id} 直接开始")
        await update.message.reply_text("欢迎！")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("机器人已启动，按 Ctrl+C 停止")
    app.run_polling()

if __name__ == "__main__":
    main()
