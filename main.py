import os, threading, requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
TOKEN = os.getenv("BOT_TOKEN")
NEMER_API_KEY = os.getenv("NEMER_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"
def run_flask():
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎮 ببجي 60 شدة", callback_data="buy_60")],[InlineKeyboardButton("🎮 ببجي 325 شدة", callback_data="buy_325")]]
    await update.message.reply_text("أهلا فيك بمتجر بارون 👑\nاختر شو بدك تشحن:", reply_markup=InlineKeyboardMarkup(keyboard))
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['product'] = query.data
    await query.message.reply_text("تمام ✅\nحول على شام كاش على هاد الرقم: [ 887b9099cd102f005bd724d7d58471eb]\nوبعدين ابعت صورة التحويل هون.")
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product = context.user_data.get('product', 'غير محدد')
    user = update.message.from_user
    caption = f"طلب جديد 📩\nمن: {user.first_name} (@{user.username})\nID: {user.id}\nالمنتج: {product}"
    keyboard = [[InlineKeyboardButton("✅ تأكيد وشحن", callback_data=f"confirm_{user.id}_{product}"), InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user.id}")]]
    await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard))
    await update.message.reply_text("وصلت الصورة ✅ عم نتحقق وبعدين منشحنلك.")
async def admin_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("confirm_"):
        await query.message.reply_text("تم التأكيد ✅ جاري الشحن عبر نمر كارد...")
    else:
        await query.message.reply_text("تم الرفض ❌")
def main():
    import asyncio
    asyncio.set_event_loop(asyncio.new_event_loop())
    threading.Thread(target=run_flask, daemon=True).start()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button, pattern="^buy_"))
    application.add_handler(CallbackQueryHandler(admin_button, pattern="^(confirm_|reject_)"))
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    application.run_polling()
if __name__ == "__main__":
    main()
