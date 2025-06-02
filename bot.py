
import asyncio
import random
from datetime import datetime, timedelta
import os
import openai
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
openai.api_key = os.getenv("OPENAI_API_KEY")  # Должен быть добавлен отдельно

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

counter_file = "counter.txt"

def get_next_number():
    if not os.path.exists(counter_file):
        with open(counter_file, "w") as f:
            f.write("1")
            return 1
    with open(counter_file, "r+") as f:
        num = int(f.read().strip())
        f.seek(0)
        f.write(str(num + 1))
        return num

async def generate_reflection():
    number = get_next_number()
    prompt = (
        "Напиши философско-богословское размышление на одну-две абзаца. "
        "Оно должно быть глубоким, но понятным. Не используй современный сленг. "
        "Стиль — созерцательный, с элементами классической духовной традиции. "
        f"Внизу подпиши: *Размышление №{number}*."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )
    text = response.choices[0].message.content.strip()
    return text

async def post_to_channel():
    try:
        reflection = await generate_reflection()
        await bot.send_message(CHANNEL_ID, reflection, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        print("Ошибка при публикации:", e)

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply("Бот работает: публикует размышления 2 раза в день.")

async def on_startup(_):
    scheduler.add_job(post_to_channel, "cron", hour=9, minute=0)
    scheduler.add_job(post_to_channel, "cron", hour=21, minute=0)
    scheduler.start()

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
