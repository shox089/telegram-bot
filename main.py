import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ✅ Token Environment Variables orqali olinadi
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 📲 Asosiy menyu
main_menu = ReplyKeyboardMarkup(
    [
        ["🎥 Video/MP3 yuklash"],
        ["🌦 Ob-havo", "🧮 Kalkulyator"],
        ["👤 Admin haqida"]
    ],
    resize_keyboard=True
)

# 🌦 Viloyatlar menyusi
regions_menu = ReplyKeyboardMarkup(
    [
        ["Toshkent", "Andijon"],
        ["Farg‘ona", "Namangan"],
        ["Buxoro", "Samarqand"],
        ["Orqaga qaytish 🔙"]
    ],
    resize_keyboard=True
)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom! Men ko‘p funksiyali botman.\nQuyidagi menyudan kerakli bo‘limni tanlang 👇",
        reply_markup=main_menu
    )

# Oddiy text handler
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🎥 Video/MP3 yuklash":
        await update.message.reply_text("📎 Menga YouTube yoki Instagram ssilka yuboring!")

    elif text == "🌦 Ob-havo":
        await update.message.reply_text("🇺🇿 Viloyatni tanlang 👇", reply_markup=regions_menu)

    elif text == "🧮 Kalkulyator":
        await update.message.reply_text("🧮 Kalkulyator funksiyasi yaqin orada qo‘shiladi!")

    elif text == "👤 Admin haqida":
        await update.message.reply_text("📊 Admin paneli: foydalanuvchi statistikasi, otzivlar va tahlillar.")

    elif text == "Orqaga qaytish 🔙":
        await update.message.reply_text("🏠 Asosiy menyuga qaytdingiz", reply_markup=main_menu)

    else:
        await update.message.reply_text("🚫 Men bu buyruqni hali tushunmayman.")

# Botni ishga tushirish
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
