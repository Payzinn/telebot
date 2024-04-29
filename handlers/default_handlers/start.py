from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from loader import bot
from telebot import types
from config_data.config import WEATHER_TOKEN
from config_data.config import EXCHANGE_TOKEN
from config_data.config import IP_TOKEN
import requests
import json
from translate import Translator
import re
from datetime import date
from datetime import timedelta


translator_en_to_ru = Translator(from_lang='en', to_lang='ru')
translator_ru_to_en = Translator(from_lang='ru', to_lang='en')

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
weather_item = types.KeyboardButton('🌤️ Узнать погоду')
cost_item = types.KeyboardButton('💵 Стоимость жизни в городе')
hotel_item = types.KeyboardButton('🏬 Отели')
markup.add(weather_item, cost_item, hotel_item)

today = date.today()
two_weeks = today + timedelta(weeks=1)

previous_city = ''

# from default_handlers.cost import get_city
# from default_handlers.weather import city_input

@bot.message_handler(commands=["start"])
def welcome(message: Message):
    print(f'{message.from_user.full_name} Вхождение в функцию welcome')
    commands = bot.send_message(message.chat.id, f'''Привет {message.from_user.username}, 
я бот который предоставит тебе инорфмацию о нужном городе. 
Воспользуйтесь моими возможностями ниже.''', reply_markup=markup)
    bot.register_next_step_handler(commands, get_command)

def get_command(message: Message):
    text = message.text

    if text == '🌤️ Узнать погоду':
        city_input(message)
    elif text == '💵 Стоимость жизни в городе':
        get_city(message)
    elif text == '🏬 Отели':
        get_city_hotel(message)
    elif text != '🏬 Отели' or text != '🌤️ Узнать погоду' or '💵 Стоимость жизни в городе':
        welcome(message)



#WEATHER
def city_input(message: Message):
    print(f'{message.from_user.full_name} Вхождение в функцию city_input, узнаёт погоду')

    city = bot.send_message(message.chat.id, 'Введите город, чтобы узнать погоду')
    bot.register_next_step_handler(city, get_weather)

def get_weather(message: Message):
    city = message.text
    if message.text == '🌤️ Узнать погоду' or message.text == '💵 Стоимость жизни в городе' or message.text == '🏬 Отели':
        get_command(message)
    else:
        print(f'{message.from_user.full_name} Вхождение в функцию get_weather')
        print(f"Введёный город: {city}")
        weather_request = "https://api.openweathermap.org/data/2.5/weather?q={},&appid={}&units=metric".format(city, WEATHER_TOKEN)
        url = requests.get(weather_request)
        data = json.loads(url.text)

        if data['cod'] != '400' and data['cod'] != '404':
            msg = bot.send_message(message.chat.id, f'Температура в городе {city}\nТемпература: {int(data['main']['temp'])}°C\nОщущается как: {int(data['main']['feels_like'])}°C\nПогода: {translator_en_to_ru.translate(data['weather'][0]['description'])}', reply_markup=markup)
            print(f"{message.from_user.full_name} Температура в {city}: {int(data['main']['temp'])}°C")
        else:
            bot.send_message(message.chat.id, f'Город {city} не найден')
            city_input(message)
            print(f"{message.from_user.full_name} Город {city} не найден")

        bot.register_next_step_handler(msg, get_command)


#COST
def get_city(message: Message):
    print(f'{message.from_user.full_name} Вхождение в функцию get_city, узнаёт стоимость жизни в городе')

    city = bot.send_message(message.chat.id, 'Введите город, чтобы узнать стоимость жизни')
    bot.register_next_step_handler(city, get_cost_of_life)

def get_cost_of_life(message: Message):
    city = message.text
    if message.text == '🌤️ Узнать погоду' or message.text == '💵 Стоимость жизни в городе' or message.text == '🏬 Отели':
        get_command(message)
    else:
        print(f'{message.from_user.full_name} Город: {city}')
        city_url = translator_ru_to_en.translate(city.lower())
        print(city_url.lower())
        cost_of_life = requests.get(f'https://livingcost.org/cost/russia/{city_url.lower()}')
        content = cost_of_life.text
        if "404: page not found. Search for cities and countries below" in content:
            bot.send_message(message.chat.id, f'Город {city} не найден')
            get_city(message)
            print(f"{message.from_user.full_name} Город {city} не найден")

        else:
            pattern = r'data-usd="\d{2,4}.\d{1,4}"'
            result = re.findall(pattern, content, re.MULTILINE)
            price_pattern = r'\d{2,4}.\d{1,4}'
            prices = [float(re.findall(price_pattern, i)[0]) for i in re.findall(pattern, content, re.MULTILINE)]
            rounded_prices = [int(price) for price in prices]

            currency_url = f'https://v6.exchangerate-api.com/v6/{EXCHANGE_TOKEN}/latest/USD'
            response_currency = requests.get(currency_url)
            data = json.loads(response_currency.text)
            ruble_to_dollar = int(data['conversion_rates']['RUB'])
            prices_in_rubles = [price * ruble_to_dollar for price in rounded_prices]
            prices_in_city = prices_in_rubles[:11]

            msg = bot.send_message(message.chat.id, f"""
        💰 Итого с арендной платой 
        Один человек: {prices_in_city[0]}₽ 
        Семья из 4 человек: {prices_in_city[1]}₽

        🛋️ Без арендной платы 
        Один человек: {prices_in_city[2]}₽ 
        Семья из 4 человек: {prices_in_city[3]}₽

        🏨 Аренда и коммунальные услуги 
        Один человек: {prices_in_city[4]}₽ 
        Семья из 4 человек: {prices_in_city[5]}₽

        🍽️ Еда 
        Один человек: {prices_in_city[6]}₽ 
        Семья из 4 человек: {prices_in_city[7]}₽

        🚐 Транспорт 
        Один человек: {prices_in_city[8]}₽ 
        Семья из 4 человек: {prices_in_city[9]}₽

        💳 Месячная зарплата после уплаты налогов: {prices_in_city[10]}₽""", reply_markup=markup)

            print(f"""{message.from_user.full_name} успешно получил ответ о стоимости жизни в городе {city}""")

        bot.register_next_step_handler(msg, get_command)


#HOTEL
def get_city_hotel(message: Message):
    print(message.from_user.full_name, "Вхождение в get_city_hotel")

    city = bot.send_message(message.chat.id, f"""Введите город: """, )
    bot.register_next_step_handler(city, get_hotel)


def get_hotel(message: Message):
    if message.text == '🌤️ Узнать погоду' or message.text == '💵 Стоимость жизни в городе' or message.text == '🏬 Отели':
        get_command(message)

    else:
        city = message.text
        hotel_url = f'https://engine.hotellook.com/api/v2/cache.json?location={translator_ru_to_en.translate(city).lower()}&currency=rub&checkIn={today}&checkOut={two_weeks}&limit=10'

        response = requests.get(hotel_url)
        if str(response) == '<Response [200]>':
            print(message.from_user.full_name, response)
            data = json.loads(response.text)
            content = data
            bot.send_message(message.chat.id,"Найденные отели по вашему запросу")
            for hotel in content:
                current_hotel = translator_en_to_ru.translate(hotel['hotelName'])
                hotel_without_space = current_hotel.replace(" ", "")
                link_on_hotel = f"https://yandex.ru/maps/?text={hotel_without_space}"
                msg = bot.send_message(message.chat.id, f"""

Название отеля: {translator_en_to_ru.translate(hotel['hotelName'])}
Звёзд: {hotel['stars']}
Цена от: {int(hotel['priceFrom'])} 
Цена за 1 день: {int(hotel['priceFrom'])//7} 
Средняя цена: {int(hotel['priceAvg'])} 
Ссылка на карту: {link_on_hotel}    
                    """)
            print(message.from_user.full_name, 'Успешно получил информацию об отелях')
        else:
            bot.send_message(message.chat.id,'Ошибка в получении запроса. Или вы не правильно ввели данные.')
            get_city_hotel(message)
            print(message.from_user.full_name, 'Ошибка в получении запроса')
    bot.register_next_step_handler(msg, get_command)
