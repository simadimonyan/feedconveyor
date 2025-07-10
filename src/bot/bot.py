import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# handlers
from src.bot.features.post.callbacks.agent import router as agent_router
from src.bot.features.post.callbacks.approve import router as approve_router
from src.bot.features.post.callbacks.habr_news import router as habr_router

# commands
from src.bot.features.post.commands.generation import router as generation_router

load_dotenv(".env")
channel_id = os.getenv("CHANNEL_ID")
username = os.getenv("CHANNEL_USERNAME")

dp = Dispatcher()
bot = Bot(token=os.getenv("API_TOKEN"), default=DefaultBotProperties())

def register_handlers():
    dp.include_router(agent_router)
    dp.include_router(approve_router)
    dp.include_router(habr_router)

def register_commands():
    dp.include_router(generation_router)

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    register_commands()
    register_handlers()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())