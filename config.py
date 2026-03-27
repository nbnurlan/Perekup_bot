# ================================================================
#  config.py — Barcha sozlamalar
#  Render.com da Environment Variables orqali o'rnatiladi
# ================================================================

import os

# ---------------------------------------------------------------
# TELEGRAM
# ---------------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "")          # Render → Environment → BOT_TOKEN
CHAT_ID   = os.getenv("CHAT_ID", "")            # Render → Environment → CHAT_ID

# ---------------------------------------------------------------
# KUZATILADIGAN OLX URL
# ---------------------------------------------------------------
# Render → Environment → OLX_URL  (yoki quyida default)
OLX_URL = os.getenv(
    "OLX_URL",
    "https://www.olx.kz/elektronika/?search%5Border%5D=created_at%3Adesc"
)

# ---------------------------------------------------------------
# TEKSHIRISH ORALIG'I (sekundlarda)
# ---------------------------------------------------------------
CHECK_INTERVAL_MIN = int(os.getenv("CHECK_INTERVAL_MIN", "120"))  # 2 daqiqa
CHECK_INTERVAL_MAX = int(os.getenv("CHECK_INTERVAL_MAX", "300"))  # 5 daqiqa

# ---------------------------------------------------------------
# FLASK WEB-SERVER (Render Health Check uchun)
# ---------------------------------------------------------------
PORT = int(os.getenv("PORT", "8080"))

# ---------------------------------------------------------------
# MA'LUMOTLAR BAZASI
# ---------------------------------------------------------------
DB_PATH = os.getenv("DB_PATH", "olx_ads.db")

# ---------------------------------------------------------------
# HTTP SO'ROV SOZLAMALARI
# ---------------------------------------------------------------
REQUEST_TIMEOUT = 20   # sekund

# ---------------------------------------------------------------
# USER-AGENT ROTATSIYASI
# Real browserlar User-Agent'lari — OLX bot filtriga tushmaslik uchun
# ---------------------------------------------------------------
USER_AGENTS = [
    # Chrome Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",

    # Chrome macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",

    # Firefox Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) "
    "Gecko/20100101 Firefox/125.0",

    # Firefox Linux
    "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) "
    "Gecko/20100101 Firefox/124.0",

    # Edge Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",

    # Safari macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",

    # Chrome Android
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",

    # Samsung Browser
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 "
    "(KHTML, like Gecko) SamsungBrowser/24.0 Chrome/117.0.0.0 Mobile Safari/537.36",
]

# ---------------------------------------------------------------
# TELEGRAM XABAR SHABLONI
# ---------------------------------------------------------------
MESSAGE_TEMPLATE = (
    "🆕 *Yangi e'lon!*\n\n"
    "📌 *{title}*\n"
    "💰 {price}\n"
    "📍 {location}\n"
    "🔗 `{link}`"
)
