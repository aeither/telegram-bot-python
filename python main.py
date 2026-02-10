from telegram.ext import Application, CommandHandler

async def start(update, context):
    await update.message.reply_text("Bot is working!")

app = Application.builder().token("YOUR_TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.run_polling()