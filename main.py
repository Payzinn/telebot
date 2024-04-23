from config_data.config import WEATHER_TOKEN
from loader import bot
from utils.set_bot_commands import set_default_commands
from handlers.default_handlers import start
# from handlers.default_handlers import weather
# from handlers.default_handlers import cost
# from handlers.default_handlers import hotels_list

if __name__ == "__main__":
    set_default_commands(bot)
    bot.infinity_polling()
