import logging
import sqlite3
import openai
from aiogram import Bot, Dispatcher, types, Router
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.enums import ParseMode
from aiogram.fsm.state import State,StatesGroup
from aiogram.dispatcher.dispatcher import FSMContextMiddleware
from aiogram.filters.command import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = '7430397258:AAFZ6B8VStfnscDoeDsmP7R-b5C9n0kTXhs'
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher()



def web_builder():
    builder=InlineKeyboardBuilder
    builder.button(text="Let's go", web_app=WebAppInfo(
        url="..."
    ))
    return builder.as_markup()

router=Router()

@router.message_handler(Command("start"))
async def start(message:types.Message):
    await message.reply(
        'Click! Click! Click!', reply_markup=web_builder()
    )

async def main():
    # Использование polling для разработки
    dp=Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(True)
    await dp.start_polling(bot)