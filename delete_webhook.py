import asyncio
from aiogram import Bot

TOKEN = "7576064824:AAHxwXgr49ZG4uTMtIHZJyRW8jn5fOYO2c8"

async def main():
    bot = Bot(token=TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook حذف شد")

if __name__ == "__main__":
    asyncio.run(main())
