import os
import zipfile

zip_path_new = '/mnt/data/auto_reflections_bot_new_token.zip'

os.makedirs('/mnt/data', exist_ok=True)  # Создаем папку, если её нет

project_files_new = {
    'bot.py': """
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import openai

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "7866232548:AAEPApwZlsj-OyqVOtAMtKkLJM5gbCp9BlQ"
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

openai.api_key = OPENAI_API_KEY
scheduler = AsyncIOScheduler()

async def generate_reflection():
    prompt = "Напиши философско-богословское размышление примерно на 150 слов."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=300,
        temperature=0.7,
    )
    text = response.choices[0].text.strip()
    return text

async def publish_reflection():
    text = await generate_reflection()
    await bot.send_message(CHANNEL_ID, text, parse_mode="Markdown")

@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer("Бот работает и будет публиковать размышления в канал дважды в день.", parse_mode="Markdown")

async def scheduler_start():
    scheduler.add_job(publish_reflection, 'cron', hour=9, minute=0)
    scheduler.add_job(publish_reflection, 'cron', hour=21, minute=0)
    scheduler.start()

async def main():
    await scheduler_start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
""",
    'requirements.txt': """
aiogram==3.20.0.post0
apscheduler==3.11.0
openai==1.83.0
python-dotenv==1.1.0
""".strip()
}

with zipfile.ZipFile(zip_path_new, 'w') as zf:
    for filename, content in project_files_new.items():
        zf.writestr(filename, content)

print(zip_path_new)
