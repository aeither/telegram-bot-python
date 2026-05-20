import os
import json
import asyncio
from flask import Flask, request, jsonify
from telegram import Bot
from telegram.constants import ParseMode
from datetime import datetime

app = Flask(__name__)

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "VOTRE_TOKEN_ICI")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "VOTRE_CHAT_ID_ICI")
WEBHOOK_SECRET   = os.environ.get("WEBHOOK_SECRET", "eurusd_secret_2024")

bot = Bot(token=TELEGRAM_TOKEN)

def format_buy_message(price, timeframe, atr):
    return f"""
SIGNAL ACHAT EUR/USD
Prix entree : {price}
Timeframe : {timeframe}
Stop Loss : {float(price) - float(atr) * 1.2:.5f}
Take Profit : {float(price) + float(atr) * 2.0:.5f}
Attendez la cloture de la bougie !
"""

def format_sell_message(price, timeframe, atr):
    return f"""
SIGNAL VENTE EUR/USD
Prix entree : {price}
Timeframe : {timeframe}
Stop Loss : {float(price) + float(atr) * 1.2:.5f}
Take Profit : {float(price) - float(atr) * 2.0:.5f}
Attendez la cloture de la bougie !
"""

@app.route("/webhook", methods=["POST"])
def webhook():
    secret = request.args.get("secret", "")
    if secret != WEBHOOK_SECRET:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        data      = request.get_json(force=True)
        signal    = data.get("signal", "").upper()
        price     = data.get("price", "0")
        timeframe = data.get("timeframe", "H4")
        atr       = data.get("atr", "0.00100")
        if signal == "BUY":
            message = format_buy_message(price, timeframe, atr)
        elif signal == "SELL":
            message = format_sell_message(price, timeframe, atr)
        else:
            message = "Pas de signal clair pour le moment"
        asyncio.run(bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message))
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/test", methods=["GET"])
def test():
    secret = request.args.get("secret", "")
    if secret != WEBHOOK_SECRET:
        return jsonify({"error": "Unauthorized"}), 401
    asyncio.run(bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Bot EUR/USD connecte ! Vous recevrez les signaux BUY/SELL ici."))
    return jsonify({"status": "test ok"}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
