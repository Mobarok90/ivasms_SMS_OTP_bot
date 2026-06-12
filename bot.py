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
# ⚙️ CONFIGURATION
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
EMAIL    = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

GROUP_ID         = "-1003871481057"
USER_BOT_USERNAME = "YourOTPBot"

# ==========================================
# 🎯 SERVICE FILTERS & LOGOS
# ==========================================
SERVICE_LOGOS = {
    "WHATSAPP":  "🟢 WhatsApp",
    "FACEBOOK":  "📘 Facebook",
    "TELEGRAM":  "✈️ Telegram",
    "TIKTOK":    "🎵 TikTok",
    "GOOGLE":    "🔴 Google",
    "VIBER":     "🟪 Viber",
    "MICROSOFT": "🪟 Microsoft",
    "SHEIN":     "👗 SHEIN",
    "HUAWEI":    "🟥 Huawei",
}
ALLOWED_SERVICES = list(SERVICE_LOGOS.keys())
BLOCKED_SERVICES = ["TIKTOKADS"]

# ==========================================
# 🌍 COUNTRY DICTIONARY (270+ Codes)
# ==========================================
COUNTRY_DICT = {
    "1": ("USA/Canada", "🇺🇸/🇨🇦"), "7": ("Russia/KZ", "🇷🇺/🇰🇿"), "20": ("Egypt", "🇪🇬"),
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
    "246": ("Diego Garcia", "🇮🇴"), "248": ("Seychelles", "🇸🇨"), "249": ("Sudan", "🇸🇩"),
    "250": ("Rwanda", "🇷🇼"), "251": ("Ethiopia", "🇪🇹"), "252": ("Somalia", "🇸🇴"),
    "253": ("Djibouti", "🇩🇯"), "254": ("Kenya", "🇰🇪"), "255": ("Tanzania", "🇹🇿"),
    "256": ("Uganda", "🇺🇬"), "257": ("Burundi", "🇧🇮"), "258": ("Mozambique", "🇲🇿"),
    "260": ("Zambia", "🇿🇲"), "261": ("Madagascar", "🇲🇬"), "262": ("Reunion", "🇷🇪"),
    "263": ("Zimbabwe", "🇿🇼"), "264": ("Namibia", "🇳🇦"), "265": ("Malawi", "🇲🇼"),
    "266": ("Lesotho", "🇱🇸"), "267": ("Botswana", "🇧🇼"), "268": ("Eswatini", "🇸🇿"),
    "269": ("Comoros", "🇰🇲"), "290": ("St Helena", "🇸🇭"), "291": ("Eritrea", "🇪🇷"),
    "297": ("Aruba", "🇦🇼"), "298": ("Faroe Islands", "🇫🇴"), "299": ("Greenland", "🇬🇱"),
    "350": ("Gibraltar", "🇬🇮"), "351": ("Portugal", "🇵🇹"), "352": ("Luxembourg", "🇱🇺"),
    "353": ("Ireland", "🇮🇪"), "354": ("Iceland", "🇮🇸"), "355": ("Albania", "🇦🇱"),
    "356": ("Malta", "🇲🇹"), "357": ("Cyprus", "🇨🇾"), "358": ("Finland", "🇫🇮"),
    "359": ("Bulgaria", "🇧🇬"), "370": ("Lithuania", "🇱🇹"), "371": ("Latvia", "🇱🇻"),
    "372": ("Estonia", "🇪🇪"), "373": ("Moldova", "🇲🇩"), "374": ("Armenia", "🇦🇲"),
    "375": ("Belarus", "🇧🇾"), "376": ("Andorra", "🇦🇩"), "377": ("Monaco", "🇲🇨"),
    "378": ("San Marino", "🇸🇲"), "379": ("Vatican City", "🇻🇦"), "380": ("Ukraine", "🇺🇦"),
    "381": ("Serbia", "🇷🇸"), "382": ("Montenegro", "🇲🇪"), "383": ("Kosovo", "🇽🇰"),
    "385": ("Croatia", "🇭🇷"), "386": ("Slovenia", "🇸🇮"), "387": ("Bosnia", "🇧🇦"),
    "389": ("North Macedonia", "🇲🇰"), "420": ("Czechia", "🇨🇿"), "421": ("Slovakia", "🇸🇰"),
    "423": ("Liechtenstein", "🇱🇮"), "500": ("Falkland", "🇫🇰"), "501": ("Belize", "🇧🇿"),
    "502": ("Guatemala", "🇬🇹"), "503": ("El Salvador", "🇸🇻"), "504": ("Honduras", "🇭🇳"),
    "505": ("Nicaragua", "🇳🇮"), "506": ("Costa Rica", "🇨🇷"), "507": ("Panama", "🇵🇦"),
    "508": ("St Pierre", "🇵🇲"), "509": ("Haiti", "🇭🇹"), "590": ("Guadeloupe", "🇬🇵"),
    "591": ("Bolivia", "🇧🇴"), "592": ("Guyana", "🇬🇾"), "593": ("Ecuador", "🇪🇨"),
    "594": ("French Guiana", "🇬🇫"), "595": ("Paraguay", "🇵🇾"), "596": ("Martinique", "🇲🇶"),
    "597": ("Suriname", "🇸🇷"), "598": ("Uruguay", "🇺🇾"), "599": ("Curacao", "🇨🇼"),
    "850": ("North Korea", "🇰🇵"), "852": ("Hong Kong", "🇭🇰"), "853": ("Macau", "🇲🇴"),
    "855": ("Cambodia", "🇰🇭"), "856": ("Laos", "🇱🇦"), "880": ("Bangladesh", "🇧🇩"),
    "886": ("Taiwan", "🇹🇼"), "960": ("Maldives", "🇲🇻"), "961": ("Lebanon", "🇱🇧"),
    "962": ("Jordan", "🇯🇴"), "963": ("Syria", "🇸🇾"), "964": ("Iraq", "🇮🇶"),
    "965": ("Kuwait", "🇰🇼"), "966": ("Saudi Arabia", "🇸🇦"), "967": ("Yemen", "🇾🇪"),
    "968": ("Oman", "🇴🇲"), "970": ("Palestine", "🇵🇸"), "971": ("UAE", "🇦🇪"),
    "972": ("Israel", "🇮🇱"), "973": ("Bahrain", "🇧🇭"), "974": ("Qatar", "🇶🇦"),
    "975": ("Bhutan", "🇧🇹"), "976": ("Mongolia", "🇲🇳"), "977": ("Nepal", "🇳🇵"),
    "992": ("Tajikistan", "🇹🇯"), "993": ("Turkmenistan", "🇹🇲"), "994": ("Azerbaijan", "🇦🇿"),
    "995": ("Georgia", "🇬🇪"), "996": ("Kyrgyzstan", "🇰🇬"), "998": ("Uzbekistan", "🇺🇿"),
}

# ==========================================
# 🕐 BANGLADESH TIMEZONE HELPER
# ==========================================
BD_TZ = timezone(timedelta(hours=6))

def bd_now():
    """সবসময় বাংলাদেশ সময় (UTC+6) দেবে — GitHub Actions যে সময়ে চলুক না কেন।"""
    return datetime.now(BD_TZ)

# ==========================================
# 🤖 TELEGRAM BOT SETUP
# ==========================================
bot = telebot.TeleBot(BOT_TOKEN)
try:
    bot.remove_webhook()
except Exception:
    pass

# ==========================================
# 📦 SEEN SIGNATURES (Thread-Safe)
# ==========================================
seen_lock       = threading.Lock()
seen_signatures = set()

def is_seen(sig: str) -> bool:
    with seen_lock:
        if sig in seen_signatures:
            return True
        if len(seen_signatures) > 2000:
            # পুরনো অর্ধেক সরিয়ে দাও — সম্পূর্ণ মুছলে duplicate হয়
            oldest = list(seen_signatures)[: len(seen_signatures) // 2]
            for s in oldest:
                seen_signatures.discard(s)
        seen_signatures.add(sig)
        return False

# ==========================================
# 🌍 COUNTRY DETECTOR
# ==========================================
def get_country_info(number, fallback_range=""):
    num_str = re.sub(r'\D', '', str(number))
    while num_str.startswith('0'):
        num_str = num_str[1:]

    for length in [4, 3, 2, 1]:
        prefix = num_str[:length]
        if prefix in COUNTRY_DICT:
            name, flag = COUNTRY_DICT[prefix]
            return f"{name} {flag}", num_str

    # fallback: range text থেকে দেশের নাম চেষ্টা করো
    letters = re.findall(r'[A-Za-z]+', str(fallback_range))
    if letters:
        country_name = ' '.join(letters).title()
        if country_name.lower() != "active":
            return f"{country_name} 🏳️", num_str

    return "Unknown 🌐", num_str

# ==========================================
# 🧹 TEXT CLEANERS
# ==========================================
def safe_text(text):
    if not text:
        return "Unknown"
    text = str(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = text.replace('<', ' ').replace('>', ' ').replace('&', 'and')
    return re.sub(r'\s+', ' ', text).strip()

def extract_otp(full_text):
    """
    OTP বের করার চেষ্টা করে — একাধিক ফরম্যাট সাপোর্ট করে।
    যেমন: 123456 | 12 3456 | 123-456 | G-123456
    """
    # G-XXXXXX ফরম্যাট (Google)
    m = re.search(r'\bG[-–]\s*(\d{6})\b', full_text)
    if m:
        return m.group(1)

    # XXX-XXX ফরম্যাট
    m = re.search(r'\b(\d{3}[-\s]\d{3})\b', full_text)
    if m:
        return m.group(1).replace(' ', '-')

    # 4–8 ডিজিটের কোড
    m = re.search(r'(?<!\d)(\d{4,8})(?!\d)', full_text)
    if m:
        return m.group(1)

    return "N/A"

# ==========================================
# 📨 TELEGRAM MESSAGE SENDER
# ==========================================
def send_otp_to_telegram(num, service_raw, full_text, range_text):
    country_info, exact_range = get_country_info(num, range_text)
    otp_code    = extract_otp(full_text)
    service_key = service_raw.upper()

    # 🚫 Blocked service হলে skip
    if service_key in BLOCKED_SERVICES:
        print(f"⛔ Blocked service skipped: {service_key}")
        return

    # ✅ Allowed service filter (SERVICE_LOGOS-এ থাকলে logo ব্যবহার করো)
    service_title = SERVICE_LOGOS.get(service_key, f"📱 {service_raw.title()}")

    country_parts = country_info.split(' ')
    country_name  = country_parts[0]
    flag          = country_parts[-1] if len(country_parts) > 1 else "🌐"

    bd_time_str = bd_now().strftime("%d-%b-%Y %I:%M %p")  # যেমন: 12-Jun-2026 11:30 PM

    msg_body = (
        f"{flag} <b>{country_name} | {service_title}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔐 <b>OTP Code:</b> <code>{otp_code}</code>\n\n"
        f"☎️ <b>Number:</b> <code>{exact_range}</code>\n"
        f"⚙️ <b>Service:</b> {service_title}\n"
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
            bot.send_message(
                GROUP_ID, msg_body,
                parse_mode="HTML",
                reply_markup=markup,
                disable_notification=True
            )
            print(f"✅ OTP Sent → {service_title} | Number: {exact_range} | OTP: {otp_code}")
            return
        except Exception as e:
            print(f"⚠️ Telegram retry {attempt + 1}/3: {e}")
            time.sleep(2)

    print(f"❌ Failed to send OTP after 3 attempts: {exact_range}")

# ==========================================
# 🔐 STEP 1: AUTO-LOGIN (SeleniumBase UC Mode)
# ==========================================
def get_fresh_cookies_and_tokens():
    print("🚀 Browser চালু হচ্ছে — ivasms.com লগইন করা হচ্ছে...")
    driver = None
    try:
        driver = Driver(uc=True, headless=True)  # GitHub Actions এ headless=True দরকার
        driver.set_page_load_timeout(60)

        print("🔐 Login page লোড করা হচ্ছে...")
        try:
            driver.get("https://www.ivasms.com/login")
        except Exception:
            pass

        time.sleep(3)

        try:
            driver.uc_gui_click_captcha()
            time.sleep(2)
        except Exception:
            pass

        driver.wait_for_element('input[name="email"]', timeout=40)
        print("✅ Cloudflare পার! Credentials দেওয়া হচ্ছে...")

        driver.type('input[name="email"]', EMAIL)
        time.sleep(0.5)
        driver.type('input[name="password"]', PASSWORD)
        time.sleep(1)

        try:
            driver.uc_gui_click_captcha()
            time.sleep(3)
        except Exception:
            pass

        print("🖱️ Login বাটন ক্লিক করা হচ্ছে...")
        try:
            driver.uc_click('button[type="submit"]')
        except Exception:
            driver.click('button[type="submit"]')

        # লগইন সম্পন্ন হওয়ার জন্য অপেক্ষা
        for _ in range(40):
            time.sleep(1)
            if "login" not in driver.current_url:
                break
        else:
            print("❌ Login ব্যর্থ হয়েছে!")
            driver.quit()
            return None, None, None

        print("✅ Dashboard পৌঁছেছি! SMS page এ যাচ্ছি...")
        driver.get("https://www.ivasms.com/portal/sms/received")
        time.sleep(6)

        cookies    = driver.get_cookies()
        user_agent = driver.execute_script("return navigator.userAgent;")

        page_token = ""
        try:
            page_token = driver.execute_script(
                'return document.querySelector("meta[name=\'csrf-token\']").getAttribute("content");'
            )
        except Exception:
            pass

        cookie_dict = {}
        for c in cookies:
            cookie_dict[c['name']] = c['value']
            if c['name'] == 'XSRF-TOKEN' and not page_token:
                page_token = urllib.parse.unquote(c['value'])

        print(f"🍪 Cookies ও Token সফলভাবে নেওয়া হয়েছে! (CSRF: {page_token[:20] if page_token else 'N/A'}...)")
        driver.quit()
        return cookie_dict, user_agent, page_token

    except Exception as e:
        print(f"❌ Cookie নেওয়া ব্যর্থ: {e}")
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        return None, None, None

# ==========================================
# 🧠 SMS HTML PARSER — সব ধরনের HTML পার্স করে
# ==========================================
def parse_sms_html(html_response: str):
    """
    ivasms SMS HTML response থেকে (sender, message) tuple list বের করে।
    একাধিক HTML structure সাপোর্ট করে।
    """
    soup = BeautifulSoup(html_response, 'html.parser')
    results = []

    # ✅ Method 1: <tr> row-based table parse
    rows = soup.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 2:
            continue

        # প্রথম কলাম = Sender
        sender_raw = safe_text(cols[0].get_text(strip=True)).upper()
        if not sender_raw or sender_raw in ("SENDER", "SERVICE", "#", "NO."):
            continue

        # দ্বিতীয় কলাম = Message
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

    # ✅ Method 2: যদি table না পাওয়া যায়, সরাসরি text থেকে OTP বের করো
    if not results:
        raw_text = soup.get_text(separator="\n")
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
        for i, line in enumerate(lines):
            if re.search(r'\d{4,8}', line):
                sender = lines[i - 1].upper() if i > 0 else "UNKNOWN"
                results.append((sender, line))

    return results

# ==========================================
# 📡 STEP 2: MAIN SCANNER (3-Step BD Timezone)
# ==========================================
def monitor_ranges():
    while True:
        cookie_dict, user_agent, page_token = get_fresh_cookies_and_tokens()

        if not cookie_dict:
            print("🔄 Login ব্যর্থ। ৩০ সেকেন্ড পর আবার চেষ্টা করা হবে...")
            time.sleep(30)
            continue

        print("⚡ Smart Scanner চালু (বাংলাদেশ সময় অনুযায়ী আজ + গতকাল স্ক্যান করবে)...")

        scraper = cloudscraper.create_scraper()
        scraper.cookies.update(cookie_dict)

        headers = {
            "User-Agent":      user_agent,
            "Accept":          "text/html, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRF-TOKEN":    page_token,
            "Content-Type":    "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin":          "https://www.ivasms.com",
            "Referer":         "https://www.ivasms.com/portal/sms/received",
        }

        error_count = 0

        while error_count < 5:
            try:
                # ✅ বাংলাদেশ সময়ে আজ ও গতকাল
                today_bd     = bd_now().strftime("%Y-%m-%d")
                yesterday_bd = (bd_now() - timedelta(days=1)).strftime("%Y-%m-%d")
                date_list    = [today_bd, yesterday_bd]

                print(f"📅 Scanning dates (BD): {date_list}")
                total_sent = 0

                for target_date in date_list:
                    base_payload = {
                        "_token": page_token,
                        "start":  target_date,
                        "end":    target_date,
                    }

                    # ─── STEP 1: Range list আনো ───
                    try:
                        res_ranges = scraper.post(
                            "https://www.ivasms.com/portal/sms/received/getsms",
                            headers=headers, data=base_payload, timeout=25
                        )
                    except Exception as e:
                        print(f"⚠️ Range fetch error [{target_date}]: {e}")
                        continue

                    if res_ranges.status_code != 200:
                        print(f"⚠️ Range response code: {res_ranges.status_code} [{target_date}]")
                        error_count += 1
                        break

                    soup_ranges = BeautifulSoup(res_ranges.text, 'html.parser')
                    raw_text    = soup_ranges.get_text(separator=" ")

                    # Range pattern: "COUNTRY_NAME 12345" বা শুধু number range
                    ranges_from_text = re.findall(r'\b[A-Z]{2,}(?:\s+[A-Z]+)*\s+\d{1,8}\b', raw_text)
                    ranges_from_html = re.findall(r"['\"]([A-Z]{2,}(?:\s+[A-Z]+)*\s+\d{1,8})['\"]", res_ranges.text)
                    # Pure numeric range (যদি country name না থাকে)
                    numeric_ranges   = re.findall(r"value=['\"](\d{1,8})['\"]", res_ranges.text)

                    valid_ranges = list(set(ranges_from_text + ranges_from_html))
                    valid_ranges = [r.strip() for r in valid_ranges if len(r) > 3 and any(c.isdigit() for c in r)]

                    # Numeric ranges fallback
                    if not valid_ranges and numeric_ranges:
                        valid_ranges = numeric_ranges

                    if not valid_ranges:
                        print(f"📭 [{target_date}] কোনো Range পাওয়া যায়নি।")
                        continue

                    print(f"✅ [{target_date}] {len(valid_ranges)} টি Range পাওয়া গেছে।")

                    # ─── STEP 2: প্রতিটি Range এর Number আনো ───
                    for r in valid_ranges:
                        payload_num        = base_payload.copy()
                        payload_num["Range"] = r

                        try:
                            res_num = scraper.post(
                                "https://www.ivasms.com/portal/sms/received/getsms/number",
                                headers=headers, data=payload_num, timeout=20
                            )
                        except Exception as e:
                            print(f"⚠️ Number fetch error [{r}]: {e}")
                            continue

                        if res_num.status_code != 200:
                            continue

                        soup_num  = BeautifulSoup(res_num.text, 'html.parser')
                        num_text  = soup_num.get_text(separator=" ")

                        nums_from_text = re.findall(r'(?<!\d)\d{8,15}(?!\d)', num_text)
                        nums_from_html = re.findall(r"['\"](\d{8,15})['\"]", res_num.text)
                        numbers        = list(set(nums_from_text + nums_from_html))

                        if not numbers:
                            continue

                        print(f"🔍 Range [{target_date}] {r} → {len(numbers)} টি নাম্বার পাওয়া গেছে")

                        # ─── STEP 3: প্রতিটি Number এর SMS আনো ───
                        for num in numbers:
                            payload_sms        = payload_num.copy()
                            payload_sms["Number"] = num

                            try:
                                res_sms = scraper.post(
                                    "https://www.ivasms.com/portal/sms/received/getsms/number/sms",
                                    headers=headers, data=payload_sms, timeout=20
                                )
                            except Exception as e:
                                print(f"⚠️ SMS fetch error [{num}]: {e}")
                                continue

                            if res_sms.status_code != 200:
                                continue

                            # HTML পার্স করে SMS বের করো
                            sms_list = parse_sms_html(res_sms.text)

                            for service_raw, full_text in sms_list:
                                if not full_text or len(full_text) < 5:
                                    continue

                                # Signature দিয়ে duplicate check
                                sig = f"{num}|{service_raw}|{full_text[:100]}"
                                if is_seen(sig):
                                    continue  # আগে পাঠানো হয়েছে

                                # 🚀 Telegram এ পাঠাও
                                send_otp_to_telegram(num, service_raw, full_text, r)
                                total_sent += 1
                                time.sleep(0.3)

                        time.sleep(0.8)

                if total_sent == 0:
                    print(f"📭 [{today_bd}] নতুন কোনো OTP পাওয়া যায়নি। পরের scan এ দেখা হবে...")

                error_count = 0

            except Exception as e:
                print(f"⚠️ Scan Error: {e}")
                error_count += 1

            # ✅ প্রতি ৮ সেকেন্ডে নতুন OTP চেক করবে
            time.sleep(8)

        print("🔄 Session শেষ! Browser দিয়ে নতুন Cookies নেওয়া হচ্ছে...")

# ==========================================
# ⌨️ TELEGRAM COMMANDS
# ==========================================
@bot.message_handler(commands=['setbot'])
def set_bot_username(message):
    global USER_BOT_USERNAME
    try:
        if str(message.chat.id) == GROUP_ID:
            parts = message.text.split()
            if len(parts) > 1:
                USER_BOT_USERNAME = parts[1].replace('https://t.me/', '').replace('@', '')
                bot.reply_to(message, f"✅ <b>Bot Link আপডেট:</b> @{USER_BOT_USERNAME}", parse_mode="HTML")
    except Exception:
        pass

@bot.message_handler(commands=['status'])
def status_cmd(message):
    bd_time_str = bd_now().strftime("%d-%b-%Y %I:%M:%S %p BST")
    bot.reply_to(
        message,
        f"✅ <b>Bot চলছে</b>\n"
        f"🕐 <b>BD সময়:</b> {bd_time_str}\n"
        f"📦 <b>Seen Signatures:</b> {len(seen_signatures)}",
        parse_mode="HTML"
    )

# ==========================================
# 🚀 MAIN ENTRY POINT
# ==========================================
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 iVASMS OTP Bot চালু হচ্ছে...")
    print(f"🕐 বাংলাদেশ সময়: {bd_now().strftime('%d-%b-%Y %I:%M %p BST')}")
    print("📌 গতকাল ও আজকের সমস্ত OTP পাঠানো হবে")
    print("=" * 60)

    # Background scanner thread
    scanner_thread = threading.Thread(target=monitor_ranges, daemon=True, name="OTP-Scanner")
    scanner_thread.start()

    # Telegram bot polling (main thread)
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
        except Exception as e:
            print(f"⚠️ Telegram Polling Error: {e}. ৫ সেকেন্ড পর আবার চেষ্টা...")
            time.sleep(5)
