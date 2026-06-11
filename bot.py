import os
import threading
from flask import Flask
from telegram.ext import Application

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Flask app for Render
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Telegram Bot is Running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# Telegram Bot
app = Application.builder().token(BOT_TOKEN).build()

def run_bot():
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    run_bot()
