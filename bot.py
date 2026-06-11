import os
import threading
from flask import Flask
from pymongo import MongoClient

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =====================
# CONFIG
# =====================

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
MONGO_URI = os.getenv("MONGO_URI")

# =====================
# DATABASE
# =====================

mongo = MongoClient(MONGO_URI)
db = mongo["supportbot"]
users_col = db["users"]

# =====================
# FLASK WEB SERVER
# =====================

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Support Bot Running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# =====================
# TELEGRAM BOT
# =====================

user_map = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    users_col.update_one(
        {"user_id": user.id},
        {
            "$set": {
                "name": user.first_name,
                "username": user.username
            }
        },
        upsert=True
    )

    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n"
        "Send me any message and it will reach the admin."
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    total = users_col.count_documents({})

    await update.message.reply_text(
        f"📊 Total Users: {total}"
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/broadcast message"
        )
        return

    msg = " ".join(context.args)

    users = users_col.find({})

    sent = 0

    for user in users:
        try:
            await context.bot.send_message(
                user["user_id"],
                f"📢 Broadcast\n\n{msg}"
            )
            sent += 1
        except:
            pass

    await update.message.reply_text(
        f"✅ Sent to {sent} users"
    )

async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    users_col.update_one(
        {"user_id": user.id},
        {
            "$set": {
                "name": user.first_name,
                "username": user.username
            }
        },
        upsert=True
    )

    text = update.message.text

    sent = await context.bot.send_message(
        OWNER_ID,
        (
            f"📩 New Message\n\n"
            f"👤 {user.first_name}\n"
            f"🆔 {user.id}\n\n"
            f"{text}"
        )
    )

    user_map[sent.message_id] = user.id

    await update.message.reply_text(
        "✅ Message delivered to admin."
    )

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    if not update.message.reply_to_message:
        return

    replied_msg_id = update.message.reply_to_message.message_id

    if replied_msg_id not in user_map:
        return

    user_id = user_map[replied_msg_id]

    try:
        await context.bot.send_message(
            user_id,
            f"📨 Admin Reply\n\n{update.message.text}"
        )

        await update.message.reply_text(
            "✅ Reply sent."
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ {e}"
        )

# =====================
# APP
# =====================

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("broadcast", broadcast))

app.add_handler(
    MessageHandler(
        filters.TEXT & filters.User(OWNER_ID) & filters.REPLY,
        admin_reply
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        user_message
    )
)

# =====================
# MAIN
# =====================

if __name__ == "__main__":

    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    app.run_polling(
        drop_pending_updates=True,
        close_loop=False
    )
