import os
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port)
    
# ================================================================
#  main.py — Asosiy fayl
#  Render.com da ishga tushiriladi.
#
#  Tarkibi:
#    1. Flask web-server  — Render "Health Check" uchun (port 8080)
#    2. Monitoring tsikli — OLX-ni kuzatib, Telegram'ga xabar yuboradi
#    3. aiogram Bot       — /start va /status komandalari
# ================================================================

import asyncio
import logging
import random
import threading
import time
from datetime import datetime

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

import config
from database import cleanup_old_ads, init_db, is_new_ad, save_ad
from parser import fetch_ads

# ---------------------------------------------------------------
# LOGGING SOZLAMASI
# ---------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("olx_bot")

# ---------------------------------------------------------------
# GLOBAL HOLATLAR (monitoring statistikasi uchun)
# ---------------------------------------------------------------
stats = {
    "start_time":    datetime.now(),
    "checks_done":   0,
    "new_ads_found": 0,
    "last_check":    None,
    "last_error":    None,
}

# ---------------------------------------------------------------
# 1. FLASK — HEALTH CHECK SERVER
# ---------------------------------------------------------------
flask_app = Flask(__name__)


@flask_app.route("/")
def health_check():
    """
    Render.com ushbu endpoint'ni ping qilib botning tirik ekanini tekshiradi.
    Agar bu javob qaytarmasa, Render serverni qayta ishga tushiradi.
    """
    uptime_seconds = (datetime.now() - stats["start_time"]).total_seconds()
    uptime_str = f"{int(uptime_seconds // 3600)}s {int((uptime_seconds % 3600) // 60)}d"
    return {
        "status":        "ok",
        "uptime":        uptime_str,
        "checks_done":   stats["checks_done"],
        "new_ads_found": stats["new_ads_found"],
        "last_check":    str(stats["last_check"]),
    }, 200


@flask_app.route("/ping")
def ping():
    return "pong", 200


def run_flask():
    """Flask-ni alohida threadda ishga tushiradi."""
    flask_app.run(host="0.0.0.0", port=config.PORT, debug=False, use_reloader=False)


# ---------------------------------------------------------------
# 2. TELEGRAM BOT — KOMANDALAR
# ---------------------------------------------------------------
bot = Bot(token=config.BOT_TOKEN)
dp  = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 *OLX Monitoring Bot ishga tayyor!*\n\n"
        f"🔍 Kuzatilayotgan URL:\n`{config.OLX_URL[:80]}...`\n\n"
        f"⏱ Tekshirish oralig'i: {config.CHECK_INTERVAL_MIN // 60}–"
        f"{config.CHECK_INTERVAL_MAX // 60} daqiqa\n\n"
        "Yangi e'lon chiqsa, avtomatik xabar keladi.\n"
        "/status — joriy holat",
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    uptime = datetime.now() - stats["start_time"]
    hours, rem = divmod(int(uptime.total_seconds()), 3600)
    minutes = rem // 60

    last_chk = (
        stats["last_check"].strftime("%H:%M:%S")
        if stats["last_check"] else "hali tekshirilmagan"
    )
    last_err = stats["last_error"] or "xato yo'q ✅"

    await message.answer(
        f"📊 *Bot holati*\n\n"
        f"⏰ Ishlash vaqti: {hours}s {minutes}d\n"
        f"🔄 Tekshirishlar soni: {stats['checks_done']}\n"
        f"🆕 Topilgan yangi e'lonlar: {stats['new_ads_found']}\n"
        f"🕐 Oxirgi tekshiruv: {last_chk}\n"
        f"⚠️ Oxirgi xato: {last_err}",
        parse_mode=ParseMode.MARKDOWN,
    )


# ---------------------------------------------------------------
# 3. XABAR YUBORISH FUNKSIYALARI
# ---------------------------------------------------------------
async def send_ad_notification(ad) -> None:
    """
    Yangi e'lon haqida Telegram'ga xabar yuboradi.
    Rasm bo'lsa — foto bilan, bo'lmasa — matn xabar sifatida.
    Har doim xabar ostida "E'lonni ochish" inline tugmasi bo'ladi.
    """
    text = config.MESSAGE_TEMPLATE.format(
        title    = ad.title,
        price    = ad.price,
        location = ad.location,
        link     = ad.link,
    )

    # --- Inline Keyboard tugmasi ---
    # url= parametri Telegram da tashqi havolani to'g'ridan ochadi
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 E'lonni ochish", url=ad.link)]
    ])

    try:
        if ad.image and ad.image.startswith("http"):
            # Rasm + matn + tugma
            await bot.send_photo(
                chat_id      = config.CHAT_ID,
                photo        = ad.image,
                caption      = text,
                parse_mode   = ParseMode.MARKDOWN,
                reply_markup = keyboard,          # ← tugma shu yerda
            )
        else:
            # Faqat matn + tugma
            await bot.send_message(
                chat_id                  = config.CHAT_ID,
                text                     = text,
                parse_mode               = ParseMode.MARKDOWN,
                reply_markup             = keyboard,   # ← tugma shu yerda
                disable_web_page_preview = True,       # URL preview o'chirildi (tugma bor)
            )

        logger.info("📨 Xabar yuborildi: %s | %s", ad.id, ad.title[:40])

    except Exception as e:
        logger.error("❌ Xabar yuborishda xato (%s): %s", ad.id, e)
        # Rasm yuborishda xato bo'lsa, rasmsiz yuborishga urinib ko'r
        if ad.image:
            try:
                await bot.send_message(
                    chat_id      = config.CHAT_ID,
                    text         = text,
                    parse_mode   = ParseMode.MARKDOWN,
                    reply_markup = keyboard,
                    disable_web_page_preview = True,
                )
            except Exception as e2:
                logger.error("❌ Matnli xabar ham yuborilmadi: %s", e2)


# ---------------------------------------------------------------
# 4. ASOSIY MONITORING TSIKLI
# ---------------------------------------------------------------
async def monitoring_loop() -> None:
    """
    Cheksiz tsikl:
      1. OLX sahifasini yuklab oladi
      2. Har bir e'lonni tekshiradi (bazada yo'qmi?)
      3. Yangi e'lon bo'lsa Telegram'ga yuboradi
      4. Random interval kutadi (anti-bot)
    """
    logger.info("🚀 Monitoring tsikli ishga tushdi")
    logger.info("🔍 URL: %s", config.OLX_URL)

    # Birinchi ishga tushishda bazani to'ldirish (spam oldini olish)
    first_run = True

    while True:
        try:
            stats["checks_done"] += 1
            stats["last_check"]   = datetime.now()

            logger.info("🔄 Tekshiruv #%d boshlandi...", stats["checks_done"])

            ads = fetch_ads(config.OLX_URL)

            if not ads:
                logger.warning("⚠️ E'lonlar olinmadi, keyingi tekshiruvda uriniladi")
                stats["last_error"] = f"E'lon olinmadi ({datetime.now().strftime('%H:%M')})"
            else:
                stats["last_error"] = None

                if first_run:
                    # Birinchi ishga tushishda barcha e'lonlarni "ko'rilgan" deb belgilash
                    # (Restart bo'lganda eski e'lonlar yana yuborilmasligi uchun)
                    new_count = 0
                    for ad in ads:
                        if is_new_ad(ad.id):
                            save_ad(ad.id)
                            new_count += 1
                    logger.info(
                        "🏁 Birinchi ishga tushish: %d e'lon bazaga yozildi "
                        "(xabar yuborilmadi)", new_count
                    )
                    first_run = False

                else:
                    # Oddiy tekshiruv: yangilarini topib yuborish
                    new_found = 0
                    for ad in ads:
                        if is_new_ad(ad.id):
                            save_ad(ad.id)
                            await send_ad_notification(ad)
                            stats["new_ads_found"] += 1
                            new_found += 1
                            # Ketma-ket xabarlar orasida 1-2 sek kechikish
                            await asyncio.sleep(random.uniform(1, 2))

                    if new_found:
                        logger.info("✅ %d ta yangi e'lon topildi va yuborildi", new_found)
                    else:
                        logger.info("😴 Yangi e'lon yo'q")

            # Har 24 soatda bir baza tozalash (taxminan)
            if stats["checks_done"] % 500 == 0:
                cleanup_old_ads(days=30)

        except Exception as e:
            logger.error("💥 Monitoring tsikli xatosi: %s", e)
            stats["last_error"] = str(e)[:80]

        # Random kechikish: 2-5 daqiqa (OLX anti-bot choralari uchun)
        delay = random.randint(config.CHECK_INTERVAL_MIN, config.CHECK_INTERVAL_MAX)
        logger.info("⏳ Keyingi tekshiruv %d sekunddan keyin...", delay)
        await asyncio.sleep(delay)


# ---------------------------------------------------------------
# 5. DASTURNI ISHGA TUSHIRISH
# ---------------------------------------------------------------
async def main() -> None:
    """
    Barcha komponentlarni parallel ishga tushiradi:
      - Flask web-server (thread)
      - Monitoring tsikli (asyncio task)
      - aiogram polling (asosiy loop)
    """
    # Bazani tayyorlash
    init_db()

    # Flask'ni alohida daemon threadda ishga tushirish
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("🌐 Flask health-check server ishga tushdi (port %d)", config.PORT)

    # Monitoring tsiklini asyncio task sifatida boshlash
    asyncio.create_task(monitoring_loop())

    # aiogram polling — bot komandalari uchun
    logger.info("🤖 Telegram bot polling boshlandi...")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
