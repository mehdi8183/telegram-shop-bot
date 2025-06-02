import asyncio
import requests
from requests.auth import HTTPBasicAuth

from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

# 🟡 اینها را با اطلاعات واقعی جایگزین کن
API_TOKEN = '7576064824:AAHxwXgr49ZG4uTMtIHZJyRW8jn5fOYO2c8'
WC_API_URL = "https://bwkatani.ir/wp-json/wc/v3/products"
WC_CONSUMER_KEY = "ck_80a0737b7b5223a3e839ac7383c6a1d71150669c"
WC_CONSUMER_SECRET = "cs_9a4fd8f87cb7a08066de02bf8d259aac467de578"

# راه‌اندازی بات و دیسپچر
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# حافظه سبد خرید کاربران
user_carts = {}

# دریافت لیست محصولات از سایت
def fetch_products():
    try:
        response = requests.get(
            WC_API_URL,
            auth=HTTPBasicAuth(WC_CONSUMER_KEY, WC_CONSUMER_SECRET),
            params={"per_page": 10}
        )
        response.raise_for_status()
        products_data = response.json()

        products = []
        for p in products_data:
            products.append({
                "id": str(p['id']),
                "name": p['name'],
                "price": int(float(p['price']) if p['price'] else 0)
            })
        return products
    except Exception as e:
        print("خطا در دریافت محصولات:", e)
        return []

# ساخت منو برای نمایش محصولات
def main_menu(products):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for product in products:
        name = product['name']
        price = product['price']
        keyboard.add(types.KeyboardButton(f"{name} - {price} تومان"))
    keyboard.add(types.KeyboardButton("🛒 مشاهده سبد خرید"))
    return keyboard

# ✅ هندلر شروع
async def cmd_start(message: types.Message):
    user_carts[message.from_user.id] = []
    products = await asyncio.to_thread(fetch_products)

    if not products:
        await message.answer("محصولی یافت نشد یا خطا در ارتباط با سایت.")
        return

    await message.answer(
        "سلام! به فروشگاه خوش آمدی. لطفا یک محصول انتخاب کن:",
        reply_markup=main_menu(products)
    )

# ✅ هندلر عمومی برای انتخاب محصول یا دیدن سبد خرید
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    products = await asyncio.to_thread(fetch_products)
    product_map = {f"{p['name']} - {p['price']} تومان": p['id'] for p in products}

    if text == "🛒 مشاهده سبد خرید":
        cart = user_carts.get(user_id, [])
        if not cart:
            await message.answer("سبد خرید شما خالی است.")
        else:
            msg = "🧺 سبد خرید شما:\n"
            total = 0
            for pid in cart:
                p = next((item for item in products if item['id'] == pid), None)
                if p:
                    msg += f"🔹 {p['name']} - {p['price']} تومان\n"
                    total += p['price']
            msg += f"\n💰 مجموع: {total} تومان"
            await message.answer(msg)
    elif text in product_map:
        user_carts.setdefault(user_id, []).append(product_map[text])
        await message.answer("✅ محصول به سبد خرید اضافه شد.")
    else:
        await message.answer("دستور یا محصول نامعتبر است. لطفاً از منو انتخاب کن.")

# ✅ راه‌اندازی هندلرها
dp.message.register(cmd_start, Command("start"))
dp.message.register(handle_message, F.text)

# ✅ تابع اصلی
async def main():
    print("🤖 ربات در حال اجراست...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
