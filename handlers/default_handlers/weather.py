from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from loader import bot
from config_data.config import WEATHER_TOKEN
import requests
import json
from translate import Translator

translator = Translator(from_lang='en', to_lang='ru')

def city_input(message: Message):
    print('Вхождение в функцию city_input')

    city = bot.send_message(message.chat.id, 'Введите город')
    bot.register_next_step_handler(city, get_weather)

def get_weather(message: Message):
    print('Вхождение в функцию get_weather')

    city = message.text
    print(f"Received city: {city}")
    weather_request = "https://api.openweathermap.org/data/2.5/weather?q={},&appid={}&units=metric".format(city, WEATHER_TOKEN)
    url = requests.get(weather_request)
    data = json.loads(url.text)
    if data['cod'] != '400' and data['cod'] != '404':
        bot.send_message(message.chat.id, f'Температура в городе {city}\nТемпература: {int(data['main']['temp'])}°C\nОщущается как: {int(data['main']['feels_like'])}°C\nПогода: {translator.translate(data['weather'][0]['description'])}')
        print(f"Temperature for {city}: {int(data['main']['temp'])}°C")
    else:
        bot.send_message(message.chat.id, f'Город {city} не найден')
        city_input(message)
        print(f"Город {city} не найден")