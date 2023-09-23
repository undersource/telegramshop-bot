from bot.main import TelegramBot
from bot.misc.settings import PRODUCT_IMAGES_DIR, VIRTUAL_PRODUCTS_DIR
from bot.misc.config import config
from os import makedirs

if __name__ == '__main__':
    makedirs(PRODUCT_IMAGES_DIR, exist_ok=True)
    makedirs(VIRTUAL_PRODUCTS_DIR, exist_ok=True)

    TOKEN = config["aiogram"]["TOKEN"]

    bot = TelegramBot(TOKEN)

    bot.run()
