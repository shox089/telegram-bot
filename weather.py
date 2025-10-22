import requests
from config import WEATHER_API_KEY

def get_weather(region_name):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={region_name},UZ&appid={WEATHER_API_KEY}&units=metric&lang=uz"
    response = requests.get(url).json()

    if response.get("cod") != 200:
        return "❌ Ob-havo ma'lumotini olishda xatolik!"

    weather = response["weather"][0]["description"].capitalize()
    temp = response["main"]["temp"]
    humidity = response["main"]["humidity"]
    pressure = response["main"]["pressure"]

    return f"🌤 {region_name} ob-havosi:\n\n🌡 Harorat: {temp}°C\n💧 Namlik: {humidity}%\n📊 Bosim: {pressure} hPa\n☁️ Holat: {weather}"
