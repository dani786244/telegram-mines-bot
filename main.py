import asyncio
import random
import time
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ========================================================
# 1. MINI WEB SERVER (For Render.com Health Checks)
# ========================================================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active 24/7!")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

# ========================================================
# 2. BOT & CHANNEL CONFIGURATION
# ========================================================
# REPLACE "YOUR_BOTFATHER_TOKEN_HERE" WITH YOUR ACTUAL BOT TOKEN FROM BOTFATHER
TOKEN = os.environ.get("BOT_TOKEN") 

CHANNEL_HANDLE = "@africa1winmines"

# REPLACE WITH YOUR ACTUAL REFERRAL / AFFILIATE LINK
AFFILIATE_LINK = "https://lkct.cc/b21fca"  

PROMO_CODE = "GOLD1010"
TUTORIAL_LINK = "https://t.me/africa1winmines/102"
STICKER_ID = "CAACAgIAAxkBAAERy5ZqkPwoJtly5slyLrQj3hpp-hvrvQACAwEAAladvQoC5dF4h-X6Tz0E"
MINES_PHOTO_URL = "https://i.ibb.co/cScKJ4ns/1787885990509.png"

# Loop Control & Timers
loop_running = False
last_tutorial_sent = 0  # Tracks 24-hour tutorial post

# ========================================================
# 3. HELPER FUNCTIONS & BOT LOGIC
# ========================================================
def generate_mines_grid(grid_size=5, num_stars=3):
    total_cells = grid_size * grid_size
    star_indices = set(random.sample(range(total_cells), num_stars))
    grid_str = ""
    for i in range(total_cells):
        grid_str += "⭐️" if i in star_indices else "🟦"
        if (i + 1) % grid_size == 0:
            grid_str += "\n"
    return grid_str

async def automated_signal_sequence(context: ContextTypes.DEFAULT_TYPE):
    global loop_running, last_tutorial_sent
    
    # Inline button attached to every signal
    tutorial_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Tutorial", url=TUTORIAL_LINK)]
    ])

    while loop_running:
        current_time = time.time()
        
        # --- 24-HOUR STANDALONE TUTORIAL POST ---
        if current_time - last_tutorial_sent >= 86400:
            try:
                await context.bot.send_message(
                    chat_id=CHANNEL_HANDLE,
                    text=(
                        "🎥 **HOW TO PLAY - TUTORIAL VIDEO**\n\n"
                        "Watch our step-by-step tutorial to learn how to follow the signals:\n"
                        f"👉 {TUTORIAL_LINK}"
                    ),
                    parse_mode="Markdown",
                    disable_web_page_preview=False
                )
                last_tutorial_sent = current_time
            except Exception as e:
                print(f"Error sending 24h tutorial post: {e}")

        # --- MINUTE 0: MAIN SIGNAL ---
        grid = generate_mines_grid(grid_size=5, num_stars=3)
        signal_text = (
            "New mines signal\n\n"
            "Bombs: 3💣\n"
            "Attempts: 3\n\n"
            f"👉 [Play here]({AFFILIATE_LINK})\n\n"
            f"{grid}"
        )
        
        signal_msg = await context.bot.send_message(
            chat_id=CHANNEL_HANDLE,
            text=signal_text,
            parse_mode="Markdown",
            reply_markup=tutorial_keyboard,
            disable_web_page_preview=True
        )

        # --- WAIT 2 MINUTES ---
        await asyncio.sleep(120)
        if not loop_running: break

        # --- MINUTE 2: GREEN RESULT & STICKER ---
        await context.bot.send_message(
            chat_id=CHANNEL_HANDLE,
            text="✅✅✅GREEEEEEEEENNNNNNN!!!✅✅✅",
            reply_to_message_id=signal_msg.message_id
        )
        
        try:
            await context.bot.send_sticker(chat_id=CHANNEL_HANDLE, sticker=STICKER_ID)
        except Exception as e:
            print(f"Sticker error: {e}")

        # --- WAIT 1 MINUTE ---
        await asyncio.sleep(60)
        if not loop_running: break

        # --- MINUTE 3: PROMO & PHOTO WITH CAPTION ---
        promo_text = (
            f"Register using the coupon **{PROMO_CODE}** and get a 500% bonus on your first deposit. 💎\n"
            "(Minimum $2 required to activate)"
        )
        await context.bot.send_message(chat_id=CHANNEL_HANDLE, text=promo_text, parse_mode="Markdown")

        photo_caption = (
            "To Get the Signals Enter the Official Site and Search for Mines and Make $20 - $50 Per Day.\n\n"
            f"➡️ [Click Here To Create Your Account]({AFFILIATE_LINK})👈\n\n"
            f"✅ [Tutorial]({TUTORIAL_LINK})👈"
        )
        
        try:
            await context.bot.send_photo(
                chat_id=CHANNEL_HANDLE,
                photo=MINES_PHOTO_URL,
                caption=photo_caption,
                parse_mode="Markdown",
                reply_markup=tutorial_keyboard
            )
        except Exception as e:
            print(f"Photo error: {e}")
            await context.bot.send_message(
                chat_id=CHANNEL_HANDLE,
                text=photo_caption,
                parse_mode="Markdown",
                reply_markup=tutorial_keyboard,
                disable_web_page_preview=True
            )

        # --- WAIT 1 MINUTE ---
        await asyncio.sleep(60)
        if not loop_running: break

        # --- MINUTE 4: COUNTDOWN ---
        await context.bot.send_message(
            chat_id=CHANNEL_HANDLE, 
            text="⏳ 1 minute left for the next signal..."
        )

        # --- WAIT 1 MINUTE (Completes 5-minute cycle) ---
        await asyncio.sleep(60)

async def start_loop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global loop_running
    if not loop_running:
        loop_running = True
        asyncio.create_task(automated_signal_sequence(context))
        await update.message.reply_text("▶️ **5-Minute Signal Loop Started!**", parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ Loop is already running.")

async def stop_loop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global loop_running
    loop_running = False
    await update.message.reply_text("⏹ **Automated Sequence Stopped.**", parse_mode="Markdown")

# ========================================================
# 4. MAIN ENTRY POINT (With Auto-Restart Loop)
# ========================================================
def main():
    # Start web server thread for Render.com health checks
    Thread(target=run_health_server, daemon=True).start()

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .build()
    )
    
    app.add_handler(CommandHandler("startloop", start_loop))
    app.add_handler(CommandHandler("stoploop", stop_loop))
    
    print("Bot is ready. Send /startloop in private chat to launch sequence.")
    app.run_polling()

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Bot error encountered: {e}. Retrying in 10s...")
            time.sleep(10)
