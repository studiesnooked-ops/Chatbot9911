import os
from telegram import Update
from telegram.ext import ContextTypes
from database.mongo import users

OWNER_ID = int(os.getenv("OWNER_ID","0"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    await users.update_one({"user_id":u.id},{"$set":{"name":u.first_name,"banned":False}},upsert=True)
    await update.message.reply_text("Welcome to Support Bot")

async def support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        return
    await context.bot.forward_message(OWNER_ID, update.effective_chat.id, update.message.id)

async def reply_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if len(context.args) < 2:
        return await update.message.reply_text("/reply user_id message")
    uid = int(context.args[0])
    msg = " ".join(context.args[1:])
    await context.bot.send_message(uid, msg)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    total = await users.count_documents({})
    await update.message.reply_text(f"Users: {total}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    msg = " ".join(context.args)
    sent = 0
    async for user in users.find({}):
        try:
            await context.bot.send_message(user["user_id"], msg)
            sent += 1
        except:
            pass
    await update.message.reply_text(f"Broadcast sent to {sent} users")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await users.update_one({"user_id":int(context.args[0])},{"$set":{"banned":True}})
    await update.message.reply_text("Banned")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await users.update_one({"user_id":int(context.args[0])},{"$set":{"banned":False}})
    await update.message.reply_text("Unbanned")
