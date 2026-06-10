from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import *
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("reply", reply_cmd))
app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, support_message))

app.run_polling()
