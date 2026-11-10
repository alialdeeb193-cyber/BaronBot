import os, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

def run_web():
    port = int(os.environ.get("PORT", 10000))
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is running")
        def log_message(self, *a):
            pass
    HTTPServer(("0.0.0.0", port), H).serve_forever()

threading.Thread(target=run_web, daemon=True).start()

import os, uuid, requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
NEMER_TOKEN = os.getenv("NEMER_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
BASE = "https://nemer-card.com/api"
HEADERS = {"api-token": NEMER_TOKEN, "Authorization": f"Bearer {NEMER_TOKEN}", "Content-Type": "application/json", "Accept": "application/json"}

def find_key(obj, keys):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in keys:
                return v
            r = find_key(v, keys)
            if r is not None:
                return r
    if isinstance(obj, list):
        for item in obj:
            r = find_key(item, keys)
            if r is not None:
                return r
    return None

def find_list(obj):
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        return obj
    if isinstance(obj, dict):
        for v in obj.values():
            r = find_list(v)
            if r:
                return r
    return []

def get_profile():
    try:
        r = requests.get(f"{BASE}/profile", headers=HEADERS, timeout=15)
        print("PROFILE:", r.status_code, r.text[:500])
        return r.json() if r.text else {}
    except Exception as e:
        print("PROFILE ERR:", e)
        return {}

def get_balance_text():
    data = get_profile()
    bal = find_key(data, ["balance", "credit", "wallet", "رصيد"])
    if bal is None:
        bal = 0
    return f"💰 رصيدك الحالي: {bal} $"

def get_products():
    try:
        r = requests.get(f"{BASE}/products", headers=HEADERS, timeout=15)
        print("PRODUCTS:", r.status_code, r.text[:500])
        data = r.json() if r.text else {}
        return find_list(data)
    except Exception as e:
        print("PRODUCTS ERR:", e)
        return []
        return f"Error: {e}"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("💰 رصيدي", callback_data="balance")],
          [InlineKeyboardButton("🎮 شحن ببجي", callback_data="shop")]]
    await update.message.reply_text("أهلا فيك بـ BaronBot 👑\nاختر:", reply_markup=InlineKeyboardMarkup(kb))

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "balance":
        await q.edit_message_text(get_balance_text())
    elif q.data == "shop":
        prods = get_products()
        if not prods:
            await q.edit_message_text("❌ ما في منتجات حالياً، جرب بعد شوي")
            return
        kb = []
        for p in prods[:20]:
            pid = p.get("id")
            name = p.get("name") or p.get("title") or str(pid)
            price = p.get("price") or p.get("cost") or ""
            kb.append([InlineKeyboardButton(f"{name} - {price}$", callback_data=f"buy_{pid}")])
        kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="back")])
        await q.edit_message_text("اختر المنتج:", reply_markup=InlineKeyboardMarkup(kb))
    elif q.data == "back":
        kb = [[InlineKeyboardButton("💰 رصيدي", callback_data="balance")],
              [InlineKeyboardButton("🎮 شحن ببجي", callback_data="shop")]]
        await q.edit_message_text("أهلا فيك بـ BaronBot 👑\nاختر:", reply_markup=InlineKeyboardMarkup(kb))
    elif q.data.startswith("buy_"):
        pid = q.data.replace("buy_", "")
        context.user_data["buy_pid"] = pid
        await q.edit_message_text("ابعت ID اللاعب (ببجي):")

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "buy_pid" not in context.user_data:
        return
    pid = context.user_data.pop("buy_pid")
    player = update.message.text.strip()
    order_uuid = str(uuid.uuid4())
    try:
        r = requests.get(f"{BASE}/client/api/newOrder/{pid}/params", params={"qty": 1, "playerId": player, "order_uuid": order_uuid}, headers=HEADERS, timeout=30)
        await update.message.reply_text(f"✅ تم إرسال الطلب!\nرقم الطلب: {order_uuid}\nالرد: {r.text[:500]}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    print("Bot started...")
    app.run_polling()
