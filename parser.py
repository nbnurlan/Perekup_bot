# ================================================================
#  parser.py — OLX sahifasini parse qilish
#  requests + BeautifulSoup4 ishlatadi
# ================================================================

import random
import logging
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional
from config import USER_AGENTS, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)


@dataclass
class Ad:
    """Bitta e'lon ma'lumotlari."""
    id:       str
    title:    str
    price:    str
    location: str
    link:     str
    image:    Optional[str]  # rasm URL (bo'lmasligi ham mumkin)


def _build_headers() -> dict:
    """
    Har safar yangi random User-Agent va real browser headerlarini qaytaradi.
    OLX'ning bot-filtriga tushmaslikning asosiy usuli.
    """
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language":  "ru-RU,ru;q=0.9,kk-KZ;q=0.8,en-US;q=0.7,en;q=0.6",
        "Accept-Encoding":  "gzip, deflate, br",
        "Connection":       "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest":   "document",
        "Sec-Fetch-Mode":   "navigate",
        "Sec-Fetch-Site":   "none",
        "Sec-Fetch-User":   "?1",
        "Cache-Control":    "max-age=0",
        "DNT":              "1",
    }


def _extract_ad_id(url: str) -> str:
    """
    E'lon havolasidan unikal ID-ni ajratib oladi.
    Masalan: https://www.olx.kz/d/obyavlenie/...ID123.html → 'ID123'
    """
    # OLX URL oxirida IDxxx.html formatida bo'ladi
    try:
        slug = url.rstrip("/").split("/")[-1]          # 'title-IDxxxxx.html'
        ad_id = slug.split("-")[-1].replace(".html", "") # 'IDxxxxx'
        return ad_id if ad_id else slug
    except Exception:
        return url   # oxirgi chora: URL-ning o'zini ID sifatida ishlatamiz


def fetch_ads(url: str) -> list[Ad]:
    """
    OLX sahifasidan e'lonlar ro'yxatini yuklab, parse qilib qaytaradi.
    Muammo bo'lsa bo'sh ro'yxat qaytaradi (dastur to'xtab qolmaydi).
    """
    try:
        response = requests.get(
            url,
            headers=_build_headers(),
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True
        )
    except requests.exceptions.Timeout:
        logger.warning("⏱️ So'rov vaqti tugadi (timeout): %s", url)
        return []
    except requests.exceptions.ConnectionError:
        logger.warning("🌐 Internet ulanish xatosi")
        return []
    except requests.exceptions.RequestException as e:
        logger.error("❌ So'rov xatosi: %s", e)
        return []

    # HTTP xatoliklarni tekshirish
    if response.status_code == 403:
        logger.warning("🚫 OLX 403 Forbidden qaytardi — bot filtriga tushildi")
        return []
    if response.status_code != 200:
        logger.warning("⚠️ HTTP %d: %s", response.status_code, url)
        return []

    return _parse_html(response.text)


def _parse_html(html: str) -> list[Ad]:
    """
    HTML matndan e'lonlarni ajratib oladi.
    OLX kodni yangilasa, shu yerda selector'larni yangilash kerak.
    """
    soup = BeautifulSoup(html, "html.parser")
    ads  = []

    # OLX.kz e'lon kartalari uchun asosiy selector
    # 2024-yil OLX tuzilishi asosida
    cards = soup.select("div[data-cy='l-card']")

    if not cards:
        # Zaxira selector (agar OLX interfeysi o'zgarsa)
        cards = soup.select("li.css-1sw3lx0") or soup.select("article")

    if not cards:
        logger.warning(
            "⚠️ Sahifadan e'lon topilmadi. "
            "OLX HTML tuzilishi o'zgangan bo'lishi mumkin."
        )
        return []

    for card in cards:
        try:
            ad = _parse_card(card)
            if ad:
                ads.append(ad)
        except Exception as e:
            logger.debug("Card parse xatosi (o'tkazib yuborildi): %s", e)
            continue

    logger.info("📋 Sahifadan %d ta e'lon olindi", len(ads))
    return ads


def _parse_card(card) -> Optional[Ad]:
    """Bitta e'lon kartasidan ma'lumot oladi."""

    # --- Havola va ID ---
    link_tag = card.select_one("a[href]")
    if not link_tag:
        return None

    raw_link = link_tag.get("href", "")
    # Ba'zan relative URL keladi
    if raw_link.startswith("/"):
        raw_link = "https://www.olx.kz" + raw_link
    if not raw_link.startswith("http"):
        return None

    ad_id = _extract_ad_id(raw_link)

    # --- Sarlavha ---
    title_tag = (
        card.select_one("h6")
        or card.select_one("[data-testid='ad-title']")
        or card.select_one("h4")
    )
    title = title_tag.get_text(strip=True) if title_tag else "Sarlavha yo'q"

    # --- Narx ---
    price_tag = (
        card.select_one("[data-testid='ad-price']")
        or card.select_one("p.css-10b0gli")
        or card.select_one("strong")
    )
    price = price_tag.get_text(strip=True) if price_tag else "Narx ko'rsatilmagan"

    # --- Joylashuv ---
    location_tag = (
        card.select_one("[data-testid='location-date']")
        or card.select_one("p.css-1a4brun")
    )
    location_text = location_tag.get_text(strip=True) if location_tag else ""
    # "Almaty, bugun 12:30" formatidan faqat shaharni olish
    location = location_text.split(",")[0].strip() if location_text else "Noma'lum"

    # --- Rasm ---
    img_tag = card.select_one("img")
    image = None
    if img_tag:
        # OLX ba'zan lazy-load ishlatadi: src yoki data-src
        image = (
            img_tag.get("src")
            or img_tag.get("data-src")
            or img_tag.get("data-lazy")
        )
        # Kichik placeholder rasmlarni o'tkazib yuborish
        if image and ("placeholder" in image or "data:image" in image):
            image = None

    return Ad(
        id=ad_id,
        title=title,
        price=price,
        location=location,
        link=raw_link,
        image=image
    )
