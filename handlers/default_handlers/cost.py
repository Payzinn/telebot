from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from loader import bot
from config_data.config import EXCHANGE_TOKEN
import re
import requests
import json
from translate import Translator

translator = Translator(from_lang='ru', to_lang='en')

def get_city(message: Message):
    city = bot.send_message(message.chat.id, 'Введите город')
    bot.register_next_step_handler(city, get_cost_of_life)

def get_cost_of_life(message: Message):
    city = message.text
    city_url = translator.translate(city.lower())
    print(city_url.lower())
    cost_of_life = requests.get(f'https://livingcost.org/cost/russia/{city_url.lower()}')
    content = cost_of_life.text
    if "404: page not found. Search for cities and countries below" in content:
        bot.send_message(message.chat.id, 'Ошибка')
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

        bot.send_message(message.chat.id, f"""
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

💳 Месячная зарплата после уплаты налогов: {prices_in_city[10]}₽""")
    