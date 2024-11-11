from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Reemplaza este token por el tuyo
TOKEN = "8025298642:AAFBcj1aMXJI6Rw6lmgZ40tfX3lFx2g86bw"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 ¡Bienvenido a Psique Oculta!\n"
        "🎉 Estamos emocionados de que te unas a nuestra comunidad. Este es un espacio para explorar, compartir y aprender sobre los misterios de la mente, el subconsciente y todo lo relacionado con el mundo oculto. 🌙✨\n\n"
        "👁️‍🗨️ Como agradecimiento por unirte, te estamos regalando un e-book exclusivo completamente gratis. 🎁\n"
        "Haz clic en el enlace de abajo para descargar tu regalo y comenzar tu viaje hacia lo desconocido.\n\n"
        "🔮 ¡Que tu viaje sea enriquecedor y lleno de descubrimientos! Si tienes alguna pregunta o quieres compartir algo interesante, no dudes en interactuar. ¡Nos encantaría saber tu opinión! "
    )

def main():
    # Crea una aplicación y pasa el token
    application = Application.builder().token(TOKEN).build()

    # Añade el manejador para el comando /start
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    # Comienza a escuchar por mensajes
    application.run_polling()

if __name__ == "__main__":
    main()
