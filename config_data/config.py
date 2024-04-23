import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_TOKEN = os.getenv("WEATHER_TOKEN")
EXCHANGE_TOKEN = os.getenv("EXCHANGE_TOKEN")
IP_TOKEN = os.getenv("IP_TOKEN")
DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    # ("weather", "Узнать погоду"),
    # ("hotels_list", "Узнать погоду"),
    # ("cost", "Узнать стоимость жизни в городе")
)
