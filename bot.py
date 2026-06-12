import os
import time
import json
import re
import threading
import html
import urllib.parse
from datetime import datetime, timedelta, timezone
import telebot
import cloudscraper
import logging
from bs4 import BeautifulSoup
from seleniumbase import Driver

telebot.logger.setLevel(logging.ERROR)

# ==========================================
# CONFIGURATION
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
EMAIL     = os.getenv("EMAIL")
PASSWORD  = os.getenv("PASSWORD")

GROUP_ID          = "-1003871481057"
USER_BOT_USERNAME = "YourOTPBot"

# ==========================================
# SERVICE FILTERS & LOGOS
# ==========================================
SERVICE_LOGOS = {
    "WHATSAPP":  "WhatsApp",
    "FACEBOOK":  "Facebook",
    "TELEGRAM":  "Telegram",
    "TIKTOK":    "TikTok",
    "GOOGLE":    "Google",
    "VIBER":     "Viber",
    "MICROSOFT": "Microsoft",
    "SHEIN":     "SHEIN",
    "HUAWEI":    "Huawei",
}
BLOCKED_SERVICES = ["TIKTOKADS"]

# ==========================================
# COUNTRY DICTIONARY (270+ Codes)
# ==========================================
COUNTRY_DICT = {
    "1": ("USA/Canada", "🇺🇸"), "7": ("Russia/KZ", "🇷🇺"), "20": ("Egypt", "🇪🇬"),
    "27": ("South Africa", "🇿🇦"), "30": ("Greece", "🇬🇷"), "31": ("Netherlands", "🇳🇱"),
    "32": ("Belgium", "🇧🇪"), "33": ("France", "🇫🇷"), "34": ("Spain", "🇪🇸"),
    "39": ("Italy", "🇮🇹"), "44": ("UK", "🇬🇧"), "49": ("Germany", "🇩🇪"),
    "51": ("Peru", "🇵🇪"), "52": ("Mexico", "🇲🇽"), "53": ("Cuba", "🇨🇺"),
    "54": ("Argentina", "🇦🇷"), "55": ("Brazil", "🇧🇷"), "56": ("Chile", "🇨🇱"),
    "57": ("Colombia", "🇨🇴"), "58": ("Venezuela", "🇻🇪"), "60": ("Malaysia", "🇲🇾"),
    "61": ("Australia", "🇦🇺"), "62": ("Indonesia", "🇮🇩"), "63": ("Philippines", "🇵🇭"),
    "64": ("New Zealand", "🇳🇿"), "65": ("Singapore", "🇸🇬"), "66": ("Thailand", "🇹🇭"),
    "81": ("Japan", "🇯🇵"), "82": ("South Korea", "🇰🇷"), "84": ("Vietnam", "🇻🇳"),
    "86": ("China", "🇨🇳"), "90": ("Turkey", "🇹🇷"), "91": ("India", "🇮🇳"),
    "92": ("Pakistan", "🇵🇰"), "93": ("Afghanistan", "🇦🇫"), "94": ("Sri Lanka", "🇱🇰"),
    "95": ("Myanmar", "🇲🇲"), "98": ("Iran", "🇮🇷"), "211": ("South Sudan", "🇸🇸"),
    "212": ("Morocco", "🇲🇦"), "213": ("Algeria", "🇩🇿"), "216": ("Tunisia", "🇹🇳"),
    "218": ("Libya", "🇱🇾"), "220": ("Gambia", "🇬🇲"), "221": ("Senegal", "🇸🇳"),
    "222": ("Mauritania", "🇲🇷"), "223": ("Mali", "🇲🇱"), "224": ("Guinea", "🇬🇳"),
    "225": ("Ivory Coast", "🇨🇮"), "226": ("Burkina Faso", "🇧🇫"), "227": ("Niger", "🇳🇪"),
    "228": ("Togo", "🇹🇬"), "229": ("Benin", "🇧🇯"), "230": ("Mauritius", "🇲🇺"),
    "231": ("Liberia", "🇱🇷"), "232": ("Sierra Leone", "🇸🇱"), "233": ("Ghana", "🇬🇭"),
    "234": ("Nigeria", "🇳🇬"), "235": ("Chad", "🇹🇩"), "236": ("CAR", "🇨🇫"),
    "237": ("Cameroon", "🇨🇲"), "238": ("Cape Verde", "🇨🇻"), "239": ("Sao Tome", "🇸🇹"),
    "240": ("Equatorial Guinea", "🇬🇶"), "241": ("Gabon", "🇬🇦"), "242": ("Congo", "🇨🇬"),
    "243": ("DR Congo", "🇨🇩"), "244": ("Angola", "🇦🇴"), "245": ("Guinea-Bissau", "🇬🇼"),
    "249": ("Sudan", "🇸🇩"), "250": ("Rwanda", "🇷🇼"), "251": ("Ethiopia", "🇪🇹"),
    "252": ("Somalia", "🇸🇴"), "253": ("Djibouti", "🇩🇯"), "254": ("Kenya", "🇰🇪"),
    "255": ("Tanzania", "🇹🇿"), "256": ("Uganda", "🇺🇬"), "257": ("Burundi", "🇧🇮"),
    "258": ("Mozambique", "🇲🇿"), "260": ("Zambia", "🇿🇲"), "261": ("Madagascar", "🇲🇬"),
    "263": ("Zimbabwe", "🇿🇼"), "264": ("Namibia", "🇳🇦"), "265": ("Malawi", "🇲🇼"),
    "266": ("Lesotho", "🇱🇸"), "267": ("Botswana", "🇧🇼"), "268": ("Eswatini", "🇸🇿"),
    "291": ("Eritrea", "🇪🇷"), "297": ("Aruba", "🇦🇼"), "298": ("Faroe Islands", "🇫🇴"),
    "299": ("Greenland", "🇬🇱"), "350": ("Gibraltar", "🇬🇮"), "351": ("Portugal", "🇵🇹"),
    "352": ("Luxembourg", "🇱🇺"), "353": ("Ireland", "🇮🇪"), "354": ("Iceland", "🇮🇸"),
    "355": ("Albania", "🇦🇱"), "356": ("Malta", "🇲🇹"), "357": ("Cyprus", "🇨🇾"),
    "358": ("Finland", "🇫🇮"), "359": ("Bulgaria", "🇧🇬"), "370": ("Lithuania", "🇱🇹"),
    "371": ("Latvia", "🇱🇻"), "372": ("Estonia", "🇪🇪"), "373": ("Moldova", "🇲🇩"),
    "374": ("Armenia", "🇦🇲"), "375": ("Belarus", "🇧🇾"), "376": ("Andorra", "🇦🇩"),
    "380": ("Ukraine", "🇺🇦"), "381": ("Serbia", "🇷🇸"), "382": ("Montenegro", "🇲🇪"),
    "383": ("Kosovo", "🇽🇰"), "385": ("Croatia", "🇭🇷"), "386": ("Slovenia", "🇸🇮"),
    "387": ("Bosnia", "🇧🇦"), "389": ("North Macedonia", "🇲🇰"), "420": ("Czechia", "🇨🇿"),
    "421": ("Slovakia", "🇸🇰"), "423": ("Liechtenstein", "🇱🇮"), "501": ("Belize", "🇧🇿"),
    "502": ("Guatemala", "🇬🇹"), "503": ("El Salvador", "🇸🇻"), "504": ("Honduras", "🇭🇳"),
    "505": ("Nicaragua", "🇳🇮"), "506": ("Costa Rica", "🇨🇷"), "507": ("Panama", "🇵🇦"),
    "509": ("Haiti", "🇭🇹"), "591": ("Bolivia", "🇧🇴"), "592": ("Guyana", "🇬🇾"),
    "593": ("Ecuador", "🇪🇨"), "595": ("Paraguay", "🇵🇾"), "597": ("Suriname", "🇸🇷"),
    "598": ("Uruguay", "🇺🇾"), "850": ("North Korea", "🇰🇵"), "852": ("Hong Kong", "🇭🇰"),
    "853": ("Macau", "🇲🇴"), "855": ("Cambodia", "🇰🇭"), "856": ("Laos", "🇱🇦"),
    "880": ("Bangladesh", "🇧🇩"), "886": ("Taiwan", "🇹🇼"), "960": ("Maldives", "🇲🇻"),
    "961": ("Lebanon", "🇱🇧"), "962": ("Jordan", "🇯🇴"), "963": ("Syria", "🇸🇾"),
    "964": ("Iraq", "🇮🇶"), "965": ("Kuwait", "🇰🇼"), "966": ("Saudi Arabia", "🇸🇦"),
    "967": ("Yemen", "🇾🇪"), "968": ("Oman", "🇴🇲"), "970": ("Palestine", "🇵🇸"),
    "971": ("UAE", "🇦🇪"), "972": ("Israel", "🇮🇱"), "973": ("Bahrain", "🇧🇭"),
    "974": ("Qatar", "🇶🇦"), "975": ("Bhutan", "🇧🇹"), "976": ("Mongolia", "🇲🇳"),
    "977": ("Nepal", "🇳🇵"), "992": ("Tajikistan", "🇹🇯"), "993": ("Turkmenistan", "🇹🇲"),
    "994": ("Azerbaijan", "🇦🇿"), "995": ("Georgia", "🇬🇪"), "996": ("Kyrgyzstan", "🇰🇬"),
    "998": ("Uzbekistan", "🇺🇿"),
}

# ==========================================
# BANGLADESH TIMEZONE (UTC+6) — Always fixed
# ==========================================
BD_TZ = timezone(timedelta(hours=6))

def bd_now() -> datetime:
    """Returns current time in Bangladesh timezone (UTC+6), regardless of server location."""
    return datetime.now(BD_TZ)

# ==========================================
# TELEGRAM BOT INIT
# ==========================================
bot = telebot.TeleBot(BOT_TOKEN)
try:
    bot.remove_webhook()
except Exception:
    pass

# ==========================================
# THREAD-SAFE SEEN SIGNATURES (Dedup)
# ==========================================
_seen_lock      = threading.Lock()
seen_signatures = set()

def is_seen(sig: str) -> bool:
    with _seen_lock:
        if sig in seen_signatures:
            return True
        # Prevent unlimited growth — drop oldest half when over 3000
        if len(seen_signatures) > 3000:
            to_remove = list(seen_signatures)[: len(seen_signatures) // 2]
            for s in to_remove:
                seen_signatures.discard(s)
        seen_signatures.add(sig)
        return False

# ==========================================
# HELPERS
# ==========================================
def get_country_info(number: str, fallback_range: str = ""):
    num_str = re.sub(r'\D', '', str(number))
    while num_str.startswith('0'):
        num_str = num_str[1:]
    for length in [4, 3, 2, 1]:
        prefix = num_str[:length]
        if prefix in COUNTRY_DICT:
            name, flag = COUNTRY_DICT[prefix]
            return f"{name} {flag}", num_str
    letters = re.findall(r'[A-Za-z]+', str(fallback_range))
    if letters:
        candidate = ' '.join(letters).title()
        if candidate.lower() != "active":
            return f"{candidate} 🏳️", num_str
    return "Unknown 🌐", num_str

def safe_text(text) -> str:
    if not text:
        return "Unknown"
    text = str(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = text.replace('<', ' ').replace('>', ' ').replace('&', 'and')
    return re.sub(r'\s+', ' ', text).strip()

def extract_otp(full_text: str) -> str:
    """Extracts OTP from message — supports G-XXXXXX, XXX-XXX, and plain XXXXXX formats."""
    m = re.search(r'\bG[-–]\s*(\d{4,8})\b', full_text)
    if m:
        return m.group(1)
    m = re.search(r'\b(\d{3}[-\s]\d{3})\b', full_text)
    if m:
        return m.group(1).replace(' ', '-')
    m = re.search(r'(?<!\d)(\d{4,8})(?!\d)', full_text)
    if m:
        return m.group(1)
    return "N/A"

def parse_sms_html(html_response: str):
    """
    Parses ivasms SMS HTML response and returns list of (sender, message) tuples.
    Supports multiple HTML structures.
    """
    soup    = BeautifulSoup(html_response, 'html.parser')
    results = []

    # Method 1: Standard <tr><td> table
    rows = soup.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 2:
            continue
        sender_raw = safe_text(cols[0].get_text(strip=True)).upper()
        if not sender_raw or sender_raw in ("SENDER", "SERVICE", "#", "NO.", "SL"):
            continue
        # Try multiple selectors for message cell
        msg_cell = (
            cols[1].find('div', class_='msg-text')
            or cols[1].find('div', class_='message')
            or cols[1].find('span', class_='msg-text')
            or cols[1].find('p')
            or cols[1]
        )
        full_text = safe_text(msg_cell.get_text(separator=" ", strip=True)) if msg_cell else ""
        if full_text and len(full_text) > 5:
            results.append((sender_raw, full_text))

    # Method 2: Fallback — scan raw text lines for OTP-like content
    if not results:
        raw_text = soup.get_text(separator="\n")
        lines    = [l.strip() for l in raw_text.splitlines() if l.strip()]
        for i, line in enumerate(lines):
            if re.search(r'\d{4,8}', line) and len(line) > 8:
                sender = lines[i - 1].upper() if i > 0 else "UNKNOWN"
                results.append((sender, line))

    return results

# ==========================================
# TELEGRAM OTP MESSAGE SENDER
# ==========================================
def send_otp_to_telegram(num: str, service_raw: str, full_text: str, range_text: str):
    service_key = service_raw.upper()

    if service_key in BLOCKED_SERVICES:
        print(f"[SKIP] Blocked service: {service_key}")
        return

    country_info, exact_range = get_country_info(num, range_text)
    otp_code      = extract_otp(full_text)
    service_label = SERVICE_LOGOS.get(service_key, service_raw.title())
    bd_time_str   = bd_now().strftime("%d-%b-%Y %I:%M %p BST")

    country_parts = country_info.split(' ')
    flag          = country_parts[-1] if len(country_parts) > 1 else "🌐"
    country_name  = ' '.join(country_parts[:-1]) if len(country_parts) > 1 else country_info

    msg_body = (
        f"{flag} <b>{country_name} | {service_label}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔐 <b>OTP Code:</b> <code>{otp_code}</code>\n\n"
        f"☎️ <b>Number:</b> <code>{exact_range}</code>\n"
        f"⚙️ <b>Service:</b> {service_label}\n"
        f"🌍 <b>Country:</b> {country_info}\n"
        f"🕐 <b>BD Time:</b> {bd_time_str}\n\n"
        f"📩 <b>Full Message:</b>\n"
        f"<code>{full_text[:400]}</code>"
    )

    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("🚀 Panel", url="https://t.me/"),
        telebot.types.InlineKeyboardButton("🛒 Buy IP", url="https://t.me/"),
    )

    for attempt in range(3):
        try:
            bot.send_message(GROUP_ID, msg_body, parse_mode="HTML",
                             reply_markup=markup, disable_notification=True)
            print(f"[SENT] {service_label} | {exact_range} | OTP: {otp_code}")
            return
        except Exception as e:
            print(f"[WARN] Telegram retry {attempt + 1}/3: {e}")
            time.sleep(2)

    print(f"[ERROR] Failed to send after 3 attempts: {exact_range}")

# ==========================================
# STEP 1: AUTO-LOGIN — Advanced Cloudflare Bypass
# KEY FIX: headless=False + xvfb virtual display (GitHub Actions uses xvfb-run)
# headless=True is easily detected by Cloudflare — always use headless=False with xvfb
# ==========================================
def get_fresh_cookies_and_tokens():
    print("[BROWSER] Launching Chrome with UC stealth mode (xvfb virtual display)...")
    driver = None

    for attempt in range(3):
        try:
            driver = Driver(
                uc=True,
                headless=False,   # IMPORTANT: False — Cloudflare detects headless=True
                                  # GitHub Actions provides virtual display via xvfb-run
            )
            driver.set_page_load_timeout(90)

            print(f"[LOGIN] Attempt {attempt + 1}/3 — Loading ivasms.com login page...")
            try:
                driver.uc_open_with_reconnect("https://www.ivasms.com/login", reconnect_time=6)
            except Exception:
                try:
                    driver.get("https://www.ivasms.com/login")
                except Exception:
                    pass

            # Wait for Cloudflare challenge to pass
            time.sleep(5)

            # Try clicking CAPTCHA if present
            for _ in range(3):
                try:
                    driver.uc_gui_click_captcha()
                    time.sleep(2)
                except Exception:
                    break

            # Check current URL — sometimes CF redirects
            current_url = driver.current_url
            print(f"[LOGIN] Current URL: {current_url}")

            # Wait for email field (up to 45 seconds)
            email_found = False
            for wait_sec in range(45):
                try:
                    driver.find_element("css selector", 'input[name="email"]')
                    email_found = True
                    print(f"[LOGIN] Email field found after {wait_sec}s!")
                    break
                except Exception:
                    time.sleep(1)
                    # Every 10 seconds, retry CAPTCHA click
                    if wait_sec % 10 == 9:
                        try:
                            driver.uc_gui_click_captcha()
                        except Exception:
                            pass

            if not email_found:
                page_src = driver.page_source[:500]
                print(f"[LOGIN] Email field NOT found. Page preview: {page_src}")
                if driver:
                    try:
                        driver.quit()
                    except Exception:
                        pass
                driver = None
                print(f"[LOGIN] Retrying in 15s (attempt {attempt + 1}/3)...")
                time.sleep(15)
                continue

            # Type credentials slowly (human-like)
            print("[LOGIN] Typing credentials...")
            driver.type('input[name="email"]', EMAIL)
            time.sleep(0.8)
            driver.type('input[name="password"]', PASSWORD)
            time.sleep(1.5)

            # One more CAPTCHA attempt before submit
            try:
                driver.uc_gui_click_captcha()
                time.sleep(3)
            except Exception:
                pass

            # Submit login form
            print("[LOGIN] Submitting login form...")
            try:
                driver.uc_click('button[type="submit"]')
            except Exception:
                try:
                    driver.click('button[type="submit"]')
                except Exception:
                    driver.execute_script(
                        'document.querySelector(\'button[type="submit"]\').click();'
                    )

            # Wait for redirect away from /login
            logged_in = False
            for _ in range(45):
                time.sleep(1)
                if "login" not in driver.current_url.lower():
                    logged_in = True
                    break

            if not logged_in:
                print(f"[LOGIN] Still on login page after submit. URL: {driver.current_url}")
                if driver:
                    try:
                        driver.quit()
                    except Exception:
                        pass
                driver = None
                time.sleep(15)
                continue

            print(f"[LOGIN] Success! Dashboard reached: {driver.current_url}")

            # Navigate to SMS received page
            driver.get("https://www.ivasms.com/portal/sms/received")
            time.sleep(6)

            # Extract cookies and tokens
            cookies    = driver.get_cookies()
            user_agent = driver.execute_script("return navigator.userAgent;")

            page_token = ""
            try:
                page_token = driver.execute_script(
                    "return document.querySelector(\"meta[name='csrf-token']\").getAttribute('content');"
                )
            except Exception:
                pass

            cookie_dict = {}
            for c in cookies:
                cookie_dict[c['name']] = c['value']
                if c['name'] == 'XSRF-TOKEN' and not page_token:
                    page_token = urllib.parse.unquote(c['value'])

            print(f"[LOGIN] Cookies captured! CSRF token: {'OK' if page_token else 'MISSING'}")
            driver.quit()
            return cookie_dict, user_agent, page_token

        except Exception as e:
            print(f"[ERROR] Browser exception (attempt {attempt + 1}/3): {e}")
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            driver = None
            time.sleep(15)

    print("[ERROR] All 3 login attempts failed.")
    return None, None, None

# ==========================================
# UNIVERSAL RESPONSE PARSER (JSON + HTML + plain-text)
# ==========================================
def extract_numbers_from_response(raw: str) -> list:
    """
    Extracts phone-number-like strings from ANY response format.
    Tries JSON first, then HTML option/select/data-attrs, then regex on plain text.
    """
    numbers = set()

    # --- Try JSON ---
    try:
        data = json.loads(raw)
        # Flatten all values from JSON and look for digit strings
        def walk(obj):
            if isinstance(obj, dict):
                for v in obj.values():
                    walk(v)
            elif isinstance(obj, list):
                for item in obj:
                    walk(item)
            elif isinstance(obj, (str, int)):
                s = str(obj).strip()
                if re.fullmatch(r'\d{6,15}', s):
                    numbers.add(s)
        walk(data)
        if numbers:
            print(f"[DEBUG] Numbers from JSON: {list(numbers)[:5]}")
            return list(numbers)
    except Exception:
        pass

    # --- Try HTML ---
    soup = BeautifulSoup(raw, 'html.parser')

    # <option value="NUMBER"> or <option>NUMBER</option>
    for opt in soup.find_all('option'):
        val = opt.get('value', '').strip()
        txt = opt.get_text(strip=True)
        for candidate in [val, txt]:
            if re.fullmatch(r'\d{6,15}', candidate):
                numbers.add(candidate)

    # data-number, data-value, data-id attributes
    for tag in soup.find_all(True):
        for attr in ['data-number', 'data-value', 'data-id', 'data-phone', 'value']:
            val = tag.get(attr, '').strip()
            if re.fullmatch(r'\d{6,15}', val):
                numbers.add(val)

    # <td> or <span> containing only digits
    for tag in soup.find_all(['td', 'span', 'div', 'p', 'li', 'a']):
        txt = tag.get_text(strip=True)
        if re.fullmatch(r'\d{6,15}', txt):
            numbers.add(txt)

    if numbers:
        print(f"[DEBUG] Numbers from HTML attrs/tags: {list(numbers)[:5]}")
        return list(numbers)

    # --- Regex fallback on raw text ---
    plain = soup.get_text(separator=" ")
    found = re.findall(r'(?<!\d)(\d{6,15})(?!\d)', plain)
    # Also check raw HTML for quoted digit strings
    found += re.findall(r'["\'](\d{6,15})["\']', raw)
    numbers.update(found)

    if numbers:
        print(f"[DEBUG] Numbers from regex fallback: {list(numbers)[:5]}")
    return list(numbers)


def extract_ranges_from_response(raw: str) -> list:
    """
    Extracts range identifiers from the getsms response.
    Handles JSON arrays, <option> tags, data-* attrs, and text patterns.
    """
    ranges = set()

    # --- Try JSON ---
    try:
        data = json.loads(raw)
        def walk(obj):
            if isinstance(obj, dict):
                for v in obj.values():
                    walk(v)
            elif isinstance(obj, list):
                for item in obj:
                    walk(item)
            elif isinstance(obj, str):
                s = obj.strip()
                if s and len(s) > 1:
                    ranges.add(s)
        walk(data)
        if ranges:
            print(f"[DEBUG] Ranges from JSON: {list(ranges)[:5]}")
            return [r for r in ranges if any(c.isdigit() for c in r) or len(r) > 2]
    except Exception:
        pass

    soup = BeautifulSoup(raw, 'html.parser')

    # <option value="RANGE">
    for opt in soup.find_all('option'):
        val = opt.get('value', '').strip()
        txt = opt.get_text(strip=True)
        for candidate in [val, txt]:
            if candidate and candidate.lower() not in ('', 'select', 'all', '--'):
                ranges.add(candidate)

    # data-range, data-value attributes
    for tag in soup.find_all(True):
        for attr in ['data-range', 'data-value', 'value']:
            val = tag.get(attr, '').strip()
            if val and len(val) > 1 and val.lower() not in ('', 'on', 'off', 'true', 'false'):
                ranges.add(val)

    if ranges:
        valid = [r for r in ranges if any(c.isdigit() for c in r)]
        if valid:
            print(f"[DEBUG] Ranges from HTML: {valid[:5]}")
            return valid

    # Text pattern fallback
    plain = soup.get_text(separator=" ")
    found_text = re.findall(r'\b[A-Z]{2,}(?:\s+[A-Z]+)*\s+\d{1,8}\b', plain)
    found_html = re.findall(r'["\']([A-Z]{2,}(?:\s+[A-Z]+)*\s+\d{1,8})["\']', raw)
    found_num  = re.findall(r'["\'](\d{1,8})["\']', raw)

    all_found = list(set(found_text + found_html + found_num))
    if all_found:
        print(f"[DEBUG] Ranges from regex: {all_found[:5]}")
    return all_found


# ==========================================
# STEP 2: MAIN OTP SCANNER (BD Timezone, 3-Step)
# ==========================================
def monitor_ranges():
    debug_logged = False  # Print raw response once per session for diagnosis

    while True:
        cookie_dict, user_agent, page_token = get_fresh_cookies_and_tokens()

        if not cookie_dict:
            print("[SCANNER] Login failed. Retrying in 60 seconds...")
            time.sleep(60)
            continue

        print("[SCANNER] Session established. Starting OTP scan (Bangladesh timezone)...")
        debug_logged = False

        scraper = cloudscraper.create_scraper()
        scraper.cookies.update(cookie_dict)

        headers = {
            "User-Agent":       user_agent,
            "Accept":           "text/html, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRF-TOKEN":     page_token,
            "Content-Type":     "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin":           "https://www.ivasms.com",
            "Referer":          "https://www.ivasms.com/portal/sms/received",
        }

        error_count = 0

        while error_count < 5:
            try:
                today_bd     = bd_now().strftime("%Y-%m-%d")
                yesterday_bd = (bd_now() - timedelta(days=1)).strftime("%Y-%m-%d")
                date_list    = [today_bd, yesterday_bd]

                print(f"[SCAN] Scanning BD dates: {date_list}")
                total_sent = 0

                for target_date in date_list:
                    base_payload = {
                        "_token": page_token,
                        "start":  target_date,
                        "end":    target_date,
                    }

                    # ── STEP 1: Fetch ranges ──────────────────────────────
                    try:
                        res_ranges = scraper.post(
                            "https://www.ivasms.com/portal/sms/received/getsms",
                            headers=headers, data=base_payload, timeout=25
                        )
                    except Exception as e:
                        print(f"[WARN] Range fetch failed [{target_date}]: {e}")
                        error_count += 1
                        break

                    if res_ranges.status_code in (401, 403):
                        print(f"[WARN] Session expired ({res_ranges.status_code}). Re-logging in...")
                        error_count = 999
                        break
                    if res_ranges.status_code != 200:
                        print(f"[WARN] Range response {res_ranges.status_code} [{target_date}]")
                        error_count += 1
                        break

                    # Debug: print raw response ONCE so we know the format
                    if not debug_logged:
                        preview = res_ranges.text[:600].replace('\n', ' ')
                        print(f"[DEBUG] Range raw response (first 600 chars): {preview}")

                    valid_ranges = extract_ranges_from_response(res_ranges.text)

                    if not valid_ranges:
                        print(f"[SCAN] No ranges found for {target_date}.")
                        continue

                    print(f"[SCAN] {len(valid_ranges)} range(s) found for {target_date}: {valid_ranges[:3]}")

                    # ── STEP 2: Fetch numbers per range ──────────────────
                    for r in valid_ranges:
                        payload_num = {**base_payload, "Range": r}

                        try:
                            res_num = scraper.post(
                                "https://www.ivasms.com/portal/sms/received/getsms/number",
                                headers=headers, data=payload_num, timeout=20
                            )
                        except Exception as e:
                            print(f"[WARN] Number fetch failed [{r}]: {e}")
                            continue

                        if res_num.status_code != 200:
                            print(f"[WARN] Number response {res_num.status_code} for range [{r}]")
                            continue

                        # Debug: print raw number response ONCE
                        if not debug_logged:
                            preview2 = res_num.text[:600].replace('\n', ' ')
                            print(f"[DEBUG] Number raw response (first 600 chars): {preview2}")
                            debug_logged = True

                        numbers = extract_numbers_from_response(res_num.text)

                        if not numbers:
                            print(f"[SCAN] Range [{r}] -> 0 numbers found. Raw snippet: {res_num.text[:200]}")
                            continue

                        print(f"[SCAN] Range [{r}] [{target_date}] -> {len(numbers)} number(s): {numbers[:3]}")

                        # ── STEP 3: Fetch SMS per number ─────────────────
                        for num in numbers:
                            payload_sms = {**payload_num, "Number": num}

                            try:
                                res_sms = scraper.post(
                                    "https://www.ivasms.com/portal/sms/received/getsms/number/sms",
                                    headers=headers, data=payload_sms, timeout=20
                                )
                            except Exception as e:
                                print(f"[WARN] SMS fetch failed [{num}]: {e}")
                                continue

                            if res_sms.status_code != 200:
                                continue

                            # Debug SMS raw response
                            sms_preview = res_sms.text[:400].replace('\n', ' ')
                            print(f"[DEBUG] SMS response for {num}: {sms_preview}")

                            sms_list = parse_sms_html(res_sms.text)

                            if not sms_list:
                                print(f"[WARN] No SMS parsed for number {num}. Raw: {res_sms.text[:200]}")

                            for service_raw, full_text in sms_list:
                                if not full_text or len(full_text) < 5:
                                    continue
                                sig = f"{num}|{service_raw}|{full_text[:120]}"
                                if is_seen(sig):
                                    continue
                                send_otp_to_telegram(num, service_raw, full_text, r)
                                total_sent += 1
                                time.sleep(0.3)

                        time.sleep(0.8)

                if total_sent == 0:
                    print(f"[SCAN] No new OTPs for {today_bd}. Next check in 8s...")
                else:
                    print(f"[SCAN] Cycle complete — sent {total_sent} OTP(s).")

                error_count = 0

            except Exception as e:
                print(f"[ERROR] Scan cycle error: {e}")
                error_count += 1

            time.sleep(8)

        print("[SCANNER] Session lost or too many errors. Re-logging in...")

# ==========================================
# TELEGRAM COMMANDS
# ==========================================
@bot.message_handler(commands=['setbot'])
def cmd_setbot(message):
    global USER_BOT_USERNAME
    try:
        if str(message.chat.id) == GROUP_ID:
            parts = message.text.split()
            if len(parts) > 1:
                USER_BOT_USERNAME = parts[1].replace('https://t.me/', '').replace('@', '')
                bot.reply_to(message, f"✅ <b>Bot link updated:</b> @{USER_BOT_USERNAME}", parse_mode="HTML")
    except Exception:
        pass

@bot.message_handler(commands=['status'])
def cmd_status(message):
    bd_str = bd_now().strftime("%d-%b-%Y %I:%M:%S %p BST")
    bot.reply_to(
        message,
        f"✅ <b>Bot is running</b>\n"
        f"🕐 <b>BD Time:</b> {bd_str}\n"
        f"📦 <b>Tracked Signatures:</b> {len(seen_signatures)}",
        parse_mode="HTML"
    )

# ==========================================
# ENTRY POINT
# ==========================================
if __name__ == "__main__":
    print("=" * 60)
    print("iVASMS OTP Bot starting...")
    print(f"BD Time: {bd_now().strftime('%d-%b-%Y %I:%M %p BST')}")
    print("Scanning: today + yesterday (Bangladesh dates)")
    print("=" * 60)

    if not BOT_TOKEN:
        print("[FATAL] BOT_TOKEN environment variable is not set!")
        exit(1)
    if not EMAIL or not PASSWORD:
        print("[FATAL] EMAIL or PASSWORD environment variable is not set!")
        exit(1)

    scanner_thread = threading.Thread(target=monitor_ranges, daemon=True, name="OTP-Scanner")
    scanner_thread.start()

    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
        except Exception as e:
            print(f"[WARN] Telegram polling error: {e}. Retrying in 5s...")
            time.sleep(5)
