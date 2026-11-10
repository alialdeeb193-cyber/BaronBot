from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "9185507456:AAF0d0Dx5DBqy53-wFCxBkAkJpUVzm24TKc"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("متابعة", callback_data="continue")]]
    await update.message.reply_text("أهلا فيك ببارون بوت 👑\nكبس متابعة لتشوف شام", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "continue":
        await query.message.reply_photo(photo=open("sham.png", "rb"), caption="هي شام ❤️")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.run_polling()
