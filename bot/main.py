from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.executor import start_webhook, start_polling
from bot.handlers.client import register_handlers_client
from bot.handlers.admin import register_handlers_admin
from bot.keyboards.dialogs import *
from bot.misc.database import r
from bot.misc.config import config
from bot.misc.logger import logger


class TelegramBot:
    def __init__(self, TOKEN):
        self.WEBHOOK_HOST = config["aiogram"]["WEBHOOK_HOST"]
        self.WEBHOOK_PATH = config["aiogram"]["WEBHOOK_PATH"]
        self.WEBHOOK_URL = f"{self.WEBHOOK_HOST}{self.WEBHOOK_PATH}"
        self.WEBAPP_HOST = config["aiogram"]["WEBAPP_HOST"]
        self.WEBAPP_PORT = config["aiogram"]["WEBAPP_PORT"]

        storage = MemoryStorage()
        self.bot = Bot(TOKEN)
        self.dp = Dispatcher(self.bot, storage=storage)

        register_handlers_client(self.dp)
        register_handlers_admin(self.dp)

    async def on_startup(self, _):
        await self.bot.set_webhook(self.WEBHOOK_URL)

    async def on_shutdown(self, _):
        logger.warning('Shutting down..')

        await self.bot.delete_webhook()
        await self.dp.storage.close()
        await self.dp.storage.wait_closed()

        logger.warning('Bye!')

    def run(self):
        try:
            r.ping()
        except:
            print("For first run Redis!")
            exit(1)

        if config["aiogram"]["MODE"].lower() == "prod":
            start_webhook(
                dispatcher=self.dp,
                webhook_path=self.WEBHOOK_PATH,
                on_startup=self.on_startup,
                on_shutdown=self.on_shutdown,
                skip_updates=True,
                host=self.WEBAPP_HOST,
                port=self.WEBAPP_PORT,
            )
        else:
            start_polling(self.dp, skip_updates=True)
