import os
import requests
from telebot import TeleBot, types

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = TeleBot(TOKEN)

DEX_URL = "https://api.dexscreener.com/latest/dex/pairs/solana"


def get_hot_pairs():
    try:
        response = requests.get(DEX_URL, timeout=20)
        response.raise_for_status()
        data = response.json()
        pairs = data.get("pairs", [])

        filtered = []

        for p in pairs:
            try:
                name = p["baseToken"]["name"]
                symbol = p["baseToken"]["symbol"]
                price = p.get("priceUsd", "N/A")
                liquidity = float(p.get("liquidity", {}).get("usd", 0))
                volume_5m = float(p.get("volume", {}).get("m5", 0))
                price_change_5m = float(p.get("priceChange", {}).get("m5", 0))
                pair_url = p.get("url", "")

                if liquidity > 50000 and volume_5m > 20000 and price_change_5m > 5:
                    score = volume_5m + (price_change_5m * 1000)
                    filtered.append({
                        "name": name,
                        "symbol": symbol,
                        "price": price,
                        "liquidity": liquidity,
                        "volume_5m": volume_5m,
                        "price_change_5m": price_change_5m,
                        "url": pair_url,
                        "score": score
                    })
            except Exception:
                continue

        filtered.sort(key=lambda x: x["score"], reverse=True)
        return filtered[:5]

    except Exception as e:
        return {"error": str(e)}


def build_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔥 Hot Solana Picks")
    markup.row("📈 Market Summary", "ℹ️ Help")
    return markup


@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        "Welcome to Hustlemilk 🚀\n\nChoose an option below:",
        reply_markup=build_main_menu()
    )


@bot.message_handler(func=lambda message: message.text == "🔥 Hot Solana Picks")
def hot_picks_handler(message):
    bot.send_message(message.chat.id, "Scanning Solana pairs...")

    results = get_hot_pairs()

    if isinstance(results, dict) and results.get("error"):
        bot.send_message(message.chat.id, f"Error fetching market data:\n{results['error']}")
        return

    if not results:
        bot.send_message(message.chat.id, "No strong momentum pairs found right now.")
        return

    for idx, token in enumerate(results, start=1):
        msg = (
            f"#{idx} {token['name']} ({token['symbol']})\n"
            f"Price: ${token['price']}\n"
            f"Liquidity: ${token['liquidity']:,.0f}\n"
            f"5m Volume: ${token['volume_5m']:,.0f}\n"
            f"5m Change: {token['price_change_5m']:.2f}%\n"
            f"Chart: {token['url']}"
        )
        bot.send_message(message.chat.id, msg)


@bot.message_handler(func=lambda message: message.text == "📈 Market Summary")
def market_summary_handler(message):
    bot.send_message(
        message.chat.id,
        "This scans Solana pairs using liquidity, 5m volume, and 5m price change."
    )


@bot.message_handler(func=lambda message: message.text == "ℹ️ Help")
def help_handler(message):
    bot.send_message(
        message.chat.id,
        "Tap Hot Solana Picks to get the top momentum pairs."
    )


@bot.message_handler(func=lambda message: True)
def fallback_handler(message):
    bot.send_message(
        message.chat.id,
        "Use the menu buttons below.",
        reply_markup=build_main_menu()
    )


bot.infinity_polling()
