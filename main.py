from flask import Flask
from threading import Thread
app_web = Flask(__name__)
@app_web.route('/')
def home(): return "Bot is alive"
Thread(target=lambda: app_web.run(host='0.0.0.0', port=10000), daemon=True).start()
import os, uuid, requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
NEMER_TOKEN = os.getenv("NEMER_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
BASE = "https://nemer-card.com"
HEADERS = {"api-token": NEMER_TOKEN}

def get_profile():
    r = requests.get(f"{BASE}/client/api/profile/", headers=HEADERS, timeout=20)
    print("PROFILE:", r.status_code, r.text[:500])
    return r.json() if r.status_code == 200 else {}

def get_products():
    r = requests.get(f"{BASE}/client/api/products/", headers=HEADERS, timeout=20)
    print("PRODUCTS:", r.status_code, r.text[:1000])
    data = r.json()
    if isinstance(data, dict):
        return data.get("products", []) or data.get("data", []) or []
    return data if isinstance(data, list) else []

def get_balance_text():
    try:
        d = get_profile()
        # جرب كل الاحتمالات للرصيد
        bal = d.get("balance") or d.get("Balance")
        if bal is None and "user" in d: bal = d["user"].get("balance")
        if bal is None and "profile" in d: bal = d["profile"].get("balance")
        if bal is None and "data" in d and isinstance(d["data"], dict): bal = d["data"].get("balance")
        if bal is None: return f"رصيدك: {d}"
        return f"💰 رصيدك: {bal} $"
    except Exception as e:
        return f"❌ خطأ بالرصيد: {e}"

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
