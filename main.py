import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import start, upload, settings, process, menu, history, cancel, view_map

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(upload.router)
    dp.include_router(settings.router)
    dp.include_router(process.router)
    dp.include_router(history.router)
    dp.include_router(cancel.router)
    dp.include_router(menu.router)
    dp.include_router(view_map.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
