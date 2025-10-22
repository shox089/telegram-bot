import logging
import threading
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN, ADMIN_ID
from downloader import download_media
from weather import get_weather
from calculator import calculate
from database import add_or_update_user, get_user_count
from flask import Flask
import os

# 🔹 Telegram botni ishga tushirish
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# 📍 Asosiy menyu
main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.row("🎥 Video/MP3 yuklash")
main_menu.row("🌤 Ob-havo", "🧮 Kalkulyator")
main_menu.row("👤 Admin haqida")

# 🌍 Viloyatlar menyusi
regions = [
    "Toshkent", "Andijon", "Farg‘ona", "Namangan", "Samarqand", "Buxoro",
    "Xorazm", "Qashqadaryo", "Surxondaryo", "Jizzax", "Sirdaryo", "Navoiy"
]
regions_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
for i in range(0, len(regions), 2):
    regions_menu.row(*regions[i:i + 2])
regions_menu.row("🔙 Orqaga qaytish")

# 🧩 Start
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    add_or_update_user(message.from_user.id, message.from_user.username)
    await message.answer("👋 Salom! Men ko‘p funksiyali botman.\nQuyidagi menyudan tanlang 👇", reply_markup=main_menu)

# 🎥 Media yuklash
@dp.message_handler(lambda msg: msg.text == "🎥 Video/MP3 yuklash")
async def ask_link(message: types.Message):
    await message.answer("📎 YouTube yoki Instagram ssilka yuboring!")

# 🌤 Ob-havo
@dp.message_handler(lambda msg: msg.text == "🌤 Ob-havo")
async def weather_menu(message: types.Message):
    await message.answer("🇺🇿 Viloyatni tanlang 👇", reply_markup=regions_menu)

@dp.message_handler(lambda msg: msg.text in regions)
async def send_weather(message: types.Message):
    result = get_weather(message.text)
    await message.answer(result)

# 🧮 Kalkulyator
@dp.message_handler(lambda msg: msg.text == "🧮 Kalkulyator")
async def calc_mode(message: types.Message):
    await message.answer("✍️ Ifodani yuboring (masalan: 2+2 yoki (5*3)/2)")

# 👤 Admin haqida
@dp.message_handler(lambda msg: msg.text == "👤 Admin haqida")
async def admin_info(message: types.Message):
    count = get_user_count()
    await message.answer(f"👤 Admin: @{ADMIN_ID}\n👥 Foydalanuvchilar soni: {count}")

# 🔙 Orqaga
@dp.message_handler(lambda msg: msg.text == "🔙 Orqaga qaytish")
async def back_to_main(message: types.Message):
    await message.answer("🏠 Asosiy menyuga qaytdingiz", reply_markup=main_menu)

# 🔗 Media yuklash
@dp.message_handler(lambda msg: msg.text.startswith("http"))
async def handle_download(message: types.Message):
    file_path = download_media(message.text)
    if file_path:
        await message.answer_document(open(file_path, 'rb'))
    else:
        await message.answer("❌ Yuklashda xatolik yuz berdi.")

# 🔢 Kalkulyator ifodalari
@dp.message_handler()
async def calc_handler(message: types.Message):
    result = calculate(message.text)
    await message.answer(f"🧮 Natija: {result}")

# 🌐 Flask server Render uchun
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot ishlayapti (Render Flask server orqali).", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def run_bot():
    executor.start_polling(dp, skip_updates=True)

if __name__ == '__main__':
    threading.Thread(target=run_web).start()
    run_bot()
