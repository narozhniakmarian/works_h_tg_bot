import logging
import os
import asyncio
from datetime import datetime, timedelta
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from gs_client import GoogleSheetsClient
from utils import calculate_hours, is_work_day

load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
JSON_KEY = "tgbotworkhours-f15c0ec0bb4d.json"
SHEET_NAME = "tg_bot_work_hour"
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "localhost")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
PORT = int(os.getenv("PORT", 8080))

# Initialize
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
gs = GoogleSheetsClient(JSON_KEY, SHEET_NAME)

# Handlers
@dp.message(F.text.in_({"1", "2", "3"}))
async def handle_shift_selection(message: types.Message):
    shift_val = int(message.text)
    next_monday = (datetime.now() + timedelta(days=(7 - datetime.now().weekday()))).strftime("%d.%m.%Y")
    gs.set_shift_for_week(next_monday, shift_val)
    await message.answer(f"✅ Зміну {shift_val} записано на наступний тиждень.", reply_markup=types.ReplyKeyboardRemove())

@dp.message()
async def handle_daily_hours(message: types.Message):
    text = message.text.lower().strip()
    current_shift = gs.get_current_shift()
    h, n, label, mult = calculate_hours(text, current_shift)
    
    date_str = datetime.now().strftime("%d.%m.%Y")
    is_weekend = not is_work_day(datetime.now())
    comment = label
    if is_weekend:
        comment += " (Вихідний/Святковий)"
        
    gs.add_record([date_str, current_shift, h, n, 0, comment])
    
    month_data = gs.get_monthly_data(datetime.now().month, datetime.now().year)
    
    # Stats for the response
    total_m = 0
    night_m = 0
    weekend_m = 0
    sick_m = 0
    vacation_m = 0
    
    for r in month_data:
        try:
            h_val = float(r.get('Години', 0))
            n_val = float(r.get('Нічні', 0))
            total_m += h_val
            night_m += n_val
            
            comment_low = str(r.get('Коментар', '')).lower()
            if "вихідний" in comment_low or "святковий" in comment_low:
                weekend_m += h_val
            if "sick" in comment_low:
                sick_m += h_val
            if "vacation" in comment_low and "unpaid" not in comment_low:
                vacation_m += h_val
        except:
            pass
    
    response = (
        f"✅ Записано на {date_str}: {h} год. ({label})\n\n"
        f"📊 На сьогодні відпрацьовано:\n"
        f"— Усього: {total_m} год.\n"
        f"— Нічні: {night_m} год.\n"
        f"— Вихідні/Святкові: {weekend_m} год.\n"
        f"— Лікарняні: {sick_m} год.\n"
        f"— Відпустки: {vacation_m} год.\n"
    )
    if total_m > 200:
        response += "\n⚠️ УВАГА: Перевищено ліміт 200 годин!"
    await message.answer(response)

# Shared task logic
async def ask_shift():
    await bot.send_message(
        CHAT_ID,
        "Яка зміна наступного тижня?\n1️⃣ 06:00–14:00\n2️⃣ 14:00–22:00\n3️⃣ 22:00–06:00",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="1"), types.KeyboardButton(text="2"), types.KeyboardButton(text="3")]],
            resize_keyboard=True
        )
    )

async def ask_hours():
    await bot.send_message(CHAT_ID, "Скільки годин ти сьогодні працював?\n(1-16, u, l4, up)")

async def send_monthly_report():
    now = datetime.now()
    data = gs.get_monthly_data(now.month, now.year)
    total_hours = sum([float(row.get('Години', 0)) for row in data])
    night_hours = sum([float(row.get('Нічні', 0)) for row in data])
    report = (
        f"📊 Підсумок за {now.strftime('%B %Y')}:\n"
        f"Загальна кількість годин: {total_hours}\n"
        f"Нічні години: {night_hours}\n"
    )
    await bot.send_message(CHAT_ID, report)

# HTTP Handlers for Cloud Scheduler
async def ask_shift_handler(request):
    await ask_shift()
    return web.Response(text="OK")

async def ask_hours_handler(request):
    await ask_hours()
    return web.Response(text="OK")

async def monthly_report_handler(request):
    await send_monthly_report()
    return web.Response(text="OK")

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

def main():
    app = web.Application()
    
    # Webhook endpoint
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    # Cloud Scheduler endpoints
    app.router.add_get('/tasks/ask-shift', ask_shift_handler)
    app.router.add_get('/tasks/ask-hours', ask_hours_handler)
    app.router.add_get('/tasks/report', monthly_report_handler)
    
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    web.run_app(app, host='0.0.0.0', port=PORT)

if __name__ == "__main__":
    main()
