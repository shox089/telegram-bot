import requests
from config import WEATHER_API_KEY

# Inglizcha holatlarni o'zbekchaga tarjima qilish lug'ati
WEATHER_TRANSLATE = {
    "clear sky": "Ochiq osmon",
    "few clouds": "Kam bulutli",
    "scattered clouds": "Tarqalgan bulutlar",
    "broken clouds": "Bulutli",
    "shower rain": "Yomg‘ir yog‘adi",
    "rain": "Yomg‘ir",
    "thunderstorm": "Momaqaldiroq",
    "snow": "Qor",
    "mist": "Tuman",
    "smoke": "Tutun",
    "haze": "Shamol/tuman aralash",
    # kerak bo‘lsa qo‘shimchalar qo‘shing
}

def get_weather(region_name):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={region_name},UZ&appid={WEATHER_API_KEY}&units=metric&lang=uz"
    response = requests.get(url).json()

    if response.get("cod") != 200:
        return "❌ Ob-havo ma'lumotini olishda xatolik!"

    weather_en = response["weather"][0]["description"].lower()
    weather_uz = WEATHER_TRANSLATE.get(weather_en, weather_en.capitalize())

    temp = response["main"]["temp"]
    humidity = response["main"]["humidity"]
    pressure = response["main"]["pressure"]

    return f"🌤 {region_name} ob-havosi:\n\n🌡 Harorat: {temp}°C\n💧 Namlik: {humidity}%\n📊 Bosim: {pressure} hPa\n☁️ Holat: {weather_uz}"
