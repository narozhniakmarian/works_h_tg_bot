import asyncio
from bot import dp, bot, ask_shift, ask_hours, send_monthly_report
from aiogram import types

async def main():
    print("🚀 Запуск бота в режимі Polling для локального тестування...")
    
    # Видаляємо вебхук, якщо він був встановлений раніше
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Викликаємо тригери відразу для перевірки
    print("📨 Надсилання тестових запитань у Telegram...")
    await ask_shift()
    await ask_hours()
    
    print("✅ Бот активний. Чекаю на ваші відповіді у Telegram...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот зупинений.")
