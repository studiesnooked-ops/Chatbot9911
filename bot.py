import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

print("BOT_TOKEN =", "SET" if BOT_TOKEN else "MISSING")

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot Running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is working!")

def run_bot():
    print("Starting Telegram Bot...")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.run_polling(
        drop_pending_updates=True,
        close_loop=False
    )

if __name__ == "__main__":
    print("Starting Flask...")
    threading.Thread(target=run_web, daemon=True).start()

    print("Starting Polling...")
    run_bot()
