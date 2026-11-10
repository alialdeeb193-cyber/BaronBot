import os
import threading
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
NEMER_TOKEN = os.getenv("NEMER_TOKEN")

# --- keep alive لـ Render ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")

def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

# --- نمر كارد ---
def get_balance():
    try:
        headers = {"Authorization": f"Bearer {NEMER_TOKEN}"}
        # إذا نمر كارد عندها رابط تاني، بنغيرو بعدين
        r = requests.get("https://api.nemercard.com/api/balance", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return str(data)
        return f"خطأ من نمر كارد: {r.status_code}"
    except Exception as e:
        return f"خطأ بالاتصال: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 رصيدي", callback_data="balance")],
        [InlineKeyboardButton("⚡ شحن", callback_data="charge")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "أهلا فيك ببارون بوت ❤️\nاختر من القائمة:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text in ["رصيد", "الرصيد", "/رصيد", "💰 رصيدي"]:
        if not NEMER_TOKEN:
            await update.message.reply_text("التوكن مو موجود بـ Render، تأكد من NEMER_TOKEN")
            return
        await update.message.reply_text("عم جيب رصيدك من نمر كارد... ⏳")
        bal = get_balance()
        await update.message.reply_text(f"رصيدك:\n{bal}")
    elif text in ["شحن", "⚡ شحن"]:
        await update.message.reply_text("ابعت المبلغ يلي بدك تشحنو، أو تواصل مع الإدارة.")
    else:
        await update.message.reply_text("ابعت /start للبداية، أو اكتب `رصيد` لتعرف رصيدك.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "balance":
        bal = get_balance()
        await query.message.reply_text(f"رصيدك:\n{bal}")
    elif query.data == "charge":
        await query.message.reply_text("ابعت المبلغ يلي بدك تشحنو.")

def main():
    threading.Thread(target=keep_alive, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
