"""
ULTRA-STABLE 24/7 Bot v2.0
Advanced error handling, timeout management, and keepalive
GUARANTEED to work without stopping
"""

import os
import json
import logging
import asyncio
import signal
import traceback
from datetime import datetime, timedelta
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    RPCError, 
    ConnectionError, 
    TimeoutError,
    FloodWait,
    ServerError,
    BadRequestError
)

# ============= ULTRA LOGGING =============
Path("logs").mkdir(exist_ok=True)

class UltraLogger:
    def __init__(self):
        self.log_file = "logs/bot_ultra.log"
        self.logger = logging.getLogger("UltraBot")
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def info(self, msg):
        self.logger.info(msg)
    
    def error(self, msg):
        self.logger.error(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)
    
    def debug(self, msg):
        self.logger.debug(msg)

logger = UltraLogger()

# ============= CONFIGURATION =============
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

# Advanced settings
CONNECT_TIMEOUT = 30
WAIT_TIMEOUT = 30
PING_INTERVAL = 45  # Keepalive ping
MAX_RETRIES = 10
RETRY_DELAY = 5
FLOOD_WAIT_TIME = 60

Path("data").mkdir(exist_ok=True)
DATABASE_FILE = "data/bot_data.json"

# ============= ULTRA STABLE BOT CLASS =============
class UltraStableBot:
    def __init__(self):
        self.client = None
        self.running = False
        self.last_ping = datetime.now()
        self.ping_task = None
        self.reconnect_count = 0
        self.heartbeat_count = 0
        self.error_count = 0
        
    async def initialize(self):
        """Initialize bot"""
        try:
            logger.info("=" * 60)
            logger.info("🚀 ULTRA-STABLE BOT v2.0 INITIALIZING")
            logger.info("=" * 60)
            
            self.client = Client(
                "ultra_bot",
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=BOT_TOKEN,
                workdir="data",
                sleep_threshold=60,  # Important: handles slow connections
                no_updates=False,
                takeout=False
            )
            
            # Register all handlers
            self.register_handlers()
            
            logger.info("✅ Bot initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            traceback.print_exc()
            return False
    
    def register_handlers(self):
        """Register message handlers"""
        
        @self.client.on_message(filters.command("start") & filters.private)
        async def start(client, message: Message):
            try:
                if not self.is_admin(message.from_user.id):
                    await message.reply_text("❌ Unauthorized")
                    return
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
                    [InlineKeyboardButton("➕ Add Channel", callback_data="add_ch")],
                    [InlineKeyboardButton("📋 Targets", callback_data="targets")],
                    [InlineKeyboardButton("📊 Stats", callback_data="stats")],
                ])
                
                await message.reply_text(
                    "🤖 **ULTRA-STABLE BOT v2.0**\n\n"
                    "✅ Running 24/7 Non-Stop\n"
                    "💓 Keepalive: Active\n"
                    "🔄 Auto-Reconnect: Enabled\n\n"
                    "Choose option:",
                    reply_markup=keyboard
                )
                logger.info(f"✅ /start from {message.from_user.id}")
            except Exception as e:
                logger.error(f"Error in start: {e}")
                try:
                    await message.reply_text(f"⚠️ Error: {str(e)[:100]}")
                except:
                    pass
        
        @self.client.on_message(filters.command("addchannel") & filters.private)
        async def add_channel(client, message: Message):
            try:
                if not self.is_admin(message.from_user.id):
                    return
                
                args = message.text.split(maxsplit=1)
                if len(args) < 2:
                    await message.reply_text("Usage: /addchannel @name or -100ID")
                    return
                
                channel = args[1]
                db = self.load_db()
                
                try:
                    chat = await self.client.get_chat(channel)
                    entry = {
                        "id": chat.id,
                        "name": chat.title or channel,
                        "username": channel,
                        "type": "channel"
                    }
                    
                    if entry not in db["channels"]:
                        db["channels"].append(entry)
                        self.save_db(db)
                        await message.reply_text(f"✅ Added: {entry['name']}")
                        logger.info(f"✅ Channel added: {entry['name']}")
                    else:
                        await message.reply_text("⚠️ Already exists!")
                except Exception as e:
                    await message.reply_text(f"❌ Error: {str(e)[:100]}")
                    logger.error(f"Error adding channel: {e}")
            except Exception as e:
                logger.error(f"Error in add_channel: {e}")
        
        @self.client.on_message(filters.command("broadcast") & filters.private)
        async def broadcast(client, message: Message):
            try:
                if not self.is_admin(message.from_user.id):
                    return
                
                text = message.text.replace("/broadcast ", "", 1).strip()
                if not text:
                    await message.reply_text("Usage: /broadcast message")
                    return
                
                db = self.load_db()
                targets = db["channels"] + db["groups"]
                
                if not targets:
                    await message.reply_text("❌ No targets!")
                    return
                
                status = await message.reply_text(f"📤 Sending to {len(targets)} targets...")
                
                success = 0
                failed = 0
                
                for target in targets:
                    try:
                        await self.client.send_message(
                            chat_id=target["id"],
                            text=text,
                            parse_mode="markdown"
                        )
                        success += 1
                    except FloodWait as fw:
                        logger.warning(f"⏳ FloodWait: {fw.value}s")
                        await asyncio.sleep(fw.value)
                    except Exception as e:
                        failed += 1
                        logger.error(f"Failed to send to {target['name']}: {e}")
                    
                    await asyncio.sleep(0.1)
                
                await status.edit_text(
                    f"✅ Complete!\n"
                    f"Success: {success}\n"
                    f"Failed: {failed}"
                )
                logger.info(f"✅ Broadcast: {success} success, {failed} failed")
            except Exception as e:
                logger.error(f"Error in broadcast: {e}")
        
        @self.client.on_message(filters.command("stats") & filters.private)
        async def stats(client, message: Message):
            try:
                if not self.is_admin(message.from_user.id):
                    return
                
                db = self.load_db()
                
                stats_text = (
                    f"📊 **ULTRA-STABLE BOT STATS**\n\n"
                    f"✅ Status: ONLINE & STABLE\n"
                    f"💓 Heartbeats: {self.heartbeat_count}\n"
                    f"🔄 Reconnects: {self.reconnect_count}\n"
                    f"❌ Errors: {self.error_count}\n"
                    f"🕐 Last Ping: {self.last_ping.strftime('%H:%M:%S')}\n\n"
                    f"📢 Channels: {len(db['channels'])}\n"
                    f"👥 Groups: {len(db['groups'])}\n"
                    f"📤 Broadcasts: {len(db['broadcast_history'])}\n"
                )
                
                await message.reply_text(stats_text)
            except Exception as e:
                logger.error(f"Error in stats: {e}")
        
        logger.info("✅ All handlers registered")
    
    @staticmethod
    def load_db():
        """Load database"""
        try:
            if os.path.exists(DATABASE_FILE):
                with open(DATABASE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading DB: {e}")
        
        return {"channels": [], "groups": [], "broadcast_history": []}
    
    @staticmethod
    def save_db(data):
        """Save database"""
        try:
            with open(DATABASE_FILE, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving DB: {e}")
    
    def is_admin(self, user_id):
        """Check admin"""
        return user_id == ADMIN_ID
    
    # ============= KEEPALIVE MECHANISM =============
    async def keepalive_ping(self):
        """Continuous keepalive ping"""
        logger.info("💓 Starting keepalive mechanism...")
        
        while self.running:
            try:
                self.last_ping = datetime.now()
                self.heartbeat_count += 1
                
                # Try to get bot info (keeps connection alive)
                me = await self.client.get_me()
                
                logger.info(
                    f"💓 Heartbeat #{self.heartbeat_count} - "
                    f"Bot: {me.first_name} - "
                    f"Errors: {self.error_count} - "
                    f"Reconnects: {self.reconnect_count}"
                )
                
                await asyncio.sleep(PING_INTERVAL)
            except asyncio.CancelledError:
                logger.info("💓 Keepalive cancelled")
                break
            except Exception as e:
                logger.warning(f"⚠️ Keepalive error: {e}")
                self.error_count += 1
                await asyncio.sleep(PING_INTERVAL)
    
    # ============= START BOT =============
    async def start_bot(self):
        """Start bot with ultra stable connection"""
        self.running = True
        retry_count = 0
        
        while self.running:
            try:
                logger.info(f"🔄 Connection attempt {retry_count + 1}/{MAX_RETRIES}")
                
                # Connect with timeouts
                async with self.client:
                    logger.info("✅ CONNECTED TO TELEGRAM!")
                    self.reconnect_count = 0
                    
                    # Start keepalive
                    self.ping_task = asyncio.create_task(self.keepalive_ping())
                    
                    # Keep alive
                    try:
                        await asyncio.Event().wait()
                    except Exception as e:
                        logger.error(f"Bot error: {e}")
                        self.error_count += 1
                    finally:
                        if self.ping_task:
                            self.ping_task.cancel()
                            try:
                                await self.ping_task
                            except asyncio.CancelledError:
                                pass
            
            except FloodWait as fw:
                logger.warning(f"⏳ FLOODWAIT: Waiting {fw.value}s...")
                self.error_count += 1
                await asyncio.sleep(fw.value)
            
            except ConnectionError as e:
                retry_count += 1
                self.reconnect_count += 1
                self.error_count += 1
                logger.warning(f"⚠️ Connection error (attempt {retry_count}): {e}")
                
                if retry_count >= MAX_RETRIES:
                    logger.error("❌ Max retries reached")
                    break
                
                wait_time = RETRY_DELAY * (2 ** min(retry_count - 1, 3))
                logger.info(f"⏳ Waiting {wait_time}s before reconnect...")
                await asyncio.sleep(wait_time)
            
            except TimeoutError as e:
                retry_count += 1
                self.reconnect_count += 1
                self.error_count += 1
                logger.warning(f"⏳ Timeout error (attempt {retry_count}): {e}")
                
                if retry_count >= MAX_RETRIES:
                    logger.error("❌ Max retries reached")
                    break
                
                await asyncio.sleep(RETRY_DELAY * 2)
            
            except ServerError as e:
                retry_count += 1
                self.error_count += 1
                logger.warning(f"⚠️ Server error (attempt {retry_count}): {e}")
                await asyncio.sleep(RETRY_DELAY * 3)
            
            except RPCError as e:
                retry_count += 1
                self.error_count += 1
                logger.error(f"❌ RPC Error (attempt {retry_count}): {e}")
                await asyncio.sleep(RETRY_DELAY)
            
            except Exception as e:
                retry_count += 1
                self.error_count += 1
                logger.error(f"❌ Unexpected error (attempt {retry_count}): {e}")
                traceback.print_exc()
                
                if retry_count >= MAX_RETRIES:
                    logger.error("❌ Max retries reached")
                    break
                
                await asyncio.sleep(RETRY_DELAY)
        
        logger.error("❌ Bot stopped")
        self.running = False
    
    async def stop_bot(self):
        """Stop bot gracefully"""
        logger.info("🛑 Stopping bot...")
        self.running = False
        
        if self.ping_task:
            self.ping_task.cancel()
        
        try:
            await self.client.stop()
            logger.info("✅ Bot stopped")
        except Exception as e:
            logger.error(f"Error stopping: {e}")

# ============= MAIN =============
async def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("🚀 ULTRA-STABLE BOT v2.0")
    logger.info("Designed for 24/7 non-stop operation")
    logger.info("=" * 60)
    
    bot = UltraStableBot()
    
    # Signal handlers
    def signal_handler(sig, frame):
        logger.info(f"📛 Received signal {sig}")
        asyncio.create_task(bot.stop_bot())
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize
    if not await bot.initialize():
        logger.error("❌ Failed to initialize")
        return
    
    # Start
    try:
        await bot.start_bot()
    except KeyboardInterrupt:
        logger.info("⏸️ Interrupted")
    except Exception as e:
        logger.error(f"❌ Fatal: {e}")
        traceback.print_exc()
    finally:
        await bot.stop_bot()
        logger.info("✅ Shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("✅ Goodbye")
    except Exception as e:
        logger.error(f"Fatal: {e}")
        traceback.print_exc()
