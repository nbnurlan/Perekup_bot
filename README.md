# 🤖 OLX.kz Monitoring Bot

OLX.kz saytini kuzatib, yangi e'lonlarni Telegram'ga yubboruvchi bot.

---

## 📁 Fayl tuzilishi

```
olx_bot/
├── main.py           # Asosiy fayl (bot + monitoring + Flask)
├── parser.py         # OLX parsing (BeautifulSoup4)
├── database.py       # SQLite bilan ishlash
├── config.py         # Barcha sozlamalar (env vars)
├── requirements.txt  # Python kutubxonalari
├── Procfile          # Render uchun ishga tushirish buyrug'i
└── README.md         # Shu fayl
```

---

## 🚀 Render.com ga Deploy qilish

### 1. Telegram bot yaratish
1. Telegram da `@BotFather` ga `/newbot` yuboring
2. Bot nomini va username'ini kiriting
3. **Token**ni saqlang (keyinroq kerak)
4. Botga `/start` yuboring va `@userinfobot` dan **CHAT_ID**ni bilib oling

### 2. GitHub ga yuklash
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/olx-bot.git
git push -u origin main
```

### 3. Render.com da sozlash
1. [render.com](https://render.com) ga kiring → **New** → **Web Service**
2. GitHub repo'ni ulang
3. Sozlamalar:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Instance Type**: `Free`

### 4. Environment Variables (muhim!)
Render dashboard → **Environment** bo'limiga qo'shing:

| Kalit          | Qiymat                          | Tavsif                    |
|----------------|---------------------------------|---------------------------|
| `BOT_TOKEN`    | `7123456789:AAF...`             | BotFather token           |
| `CHAT_ID`      | `-1001234567890` yoki `123456`  | Xabar yuboriladigan chat  |
| `OLX_URL`      | `https://www.olx.kz/...`        | Kuzatiladigan OLX havolasi|
| `CHECK_INTERVAL_MIN` | `120`                     | Min kechikish (sek)       |
| `CHECK_INTERVAL_MAX` | `300`                     | Max kechikish (sek)       |

### 5. Health Check sozlash
Render dashboard → **Settings** → **Health Check Path**: `/ping`

---

## ⚠️ Muhim eslatmalar

**Render Free tier cheklovi:**  
Render'ning bepul tarifi 15 daqiqa faollik bo'lmasa serverni "uxlatadi".
Bot o'zi Flask server orqali Render'ga javob beradi, shuning uchun bu muammo
avtomatik hal bo'ladi — lekin ishonchli ishlash uchun `UptimeRobot` yoki
`cron-job.org` orqali har 10 daqiqada `/ping` ga so'rov yuborishni sozlang.

**SQLite va Render:**  
Render'ning bepul tizimida disk o'zgaruvchilardan keyin saqlanishi **kafolatlanmaydi**.
Yani restart bo'lganda `olx_ads.db` o'chishi mumkin → bot restart'dan keyin eski
e'lonlarni qayta yuborishi mumkin (birinchi tekshiruvda emas, chunki `first_run`
logikasi bor). Bu muammo PostgreSQL bilan hal qilinadi, ammo oddiy foydalanish
uchun SQLite yetarli.

---

## 🛠️ Mahalliy sinovdan o'tkazish

```bash
# Kutubxonalarni o'rnatish
pip install -r requirements.txt

# .env fayl yaratish (yoki to'g'ridan config.py ga yozing)
export BOT_TOKEN="your_token"
export CHAT_ID="your_chat_id"
export OLX_URL="https://www.olx.kz/elektronika/..."

# Ishga tushirish
python main.py
```

---

## 📊 Bot komandalari

| Komanda   | Tavsif                                    |
|-----------|-------------------------------------------|
| `/start`  | Bot haqida ma'lumot va kuzatilayotgan URL |
| `/status` | Tekshirishlar soni, topilgan e'lonlar     |
