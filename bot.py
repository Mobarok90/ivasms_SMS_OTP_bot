import os
import time
import json
import re
import threading
import html
import urllib.parse
from datetime import datetime, timedelta
import telebot
import cloudscraper
import logging
from bs4 import BeautifulSoup
from seleniumbase import Driver

telebot.logger.setLevel(logging.ERROR)

# ==========================================
# ⚙️ ADVANCED CONFIGURATION (Paid SMS System)
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

GROUP_ID = "-1003871481057"
USER_BOT_USERNAME = "YourOTPBot"

# ==========================================
# 🎯 SERVICE FILTERS & LOGOS
# ==========================================
SERVICE_LOGOS = {
    "WHATSAPP": "🟢 WhatsApp", "FACEBOOK": "📘 Facebook", "TELEGRAM": "✈️ Telegram",
    "TIKTOK": "🎵 TikTok", "GOOGLE": "🔴 Google", "VIBER": "🟪 Viber", "MICROSOFT": "🪟 Microsoft",
    "SHEIN": "👗 SHEIN", "HUAWEI": "🟥 Huawei"
}
ALLOWED_SERVICES = list(SERVICE_LOGOS.keys())
BLOCKED_SERVICES = ["TIKTOKADS"] 

# ==========================================
# 🌍 SUPER MASSIVE COUNTRY DICTIONARY (270+ Codes)
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
    "995": ("Georgia", "🇬🇪"), "996": ("Kyrgyzstan", "🇰🇬"), "998": ("Uzbekistan", "🇺🇿")
}

bot = telebot.TeleBot(BOT_TOKEN)
try: bot.remove_webhook()
except: pass

seen_signatures = set() 
is_first_run = True

@bot.message_handler(commands=['setbot'])
def set_bot_username(message):
    global USER_BOT_USERNAME
    try:
        if str(message.chat.id) == GROUP_ID:
            text = message.text.split()
            if len(text) > 1:
                USER_BOT_USERNAME = text[1].replace('https://t.me/', '').replace('@', '')
                bot.reply_to(message, f"✅ <b>Bot Link Updated:</b> @{USER_BOT_USERNAME}", parse_mode="HTML")
    except: pass

def get_country_and_exact_range(number, range_text=""):
    num_str = "".join(filter(str.isdigit, str(number)))
    while num_str.startswith('0'): num_str = num_str[1:]
    exact_range = num_str if num_str else str(number)
    country_info = "Unknown Country 🌐"
    
    matched = False
    for length in [4, 3, 2, 1]:  
        if len(exact_range) >= length:
            prefix = exact_range[:length]
            if prefix in COUNTRY_DICT:
                name, flag = COUNTRY_DICT[prefix]
                country_info = f"{name} {flag}"
                matched = True
                break
                
    if not matched and range_text:
        letters_only = re.findall(r'[A-Za-z]+', str(range_text))
        if letters_only:
            country_name = ' '.join(letters_only).title()
            if country_name.lower() != "active": 
                country_info = f"{country_name} 🏳️"
    return country_info, exact_range

def safe_text(text):
    if not text: return "Unknown"
    text = str(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = text.replace('<', ' ').replace('>', ' ').replace('&', 'and')
    return re.sub(r'\s+', ' ', text).strip()

def extract_otp(full_text):
    match = re.search(r'(?<!\d)(\d{4,8})(?!\d)', full_text)
    if match: return match.group(1)
    match_dash = re.search(r'\b(\d{3}[-\s]\d{3})\b', full_text)
    if match_dash: return match_dash.group(1)
    return "N/A"

# ==========================================
# 🌐 STEP 1: AUTO-LOGIN & GET SECURE TOKENS
# ==========================================
def get_fresh_cookies_and_tokens():
    print("🚀 Launching invisible Browser to login to Paid Account...")
    driver = None
    try:
        driver = Driver(uc=True, headless=False)
        driver.set_page_load_timeout(45)
        
        print("🔐 Navigating to iVASMS login...")
        try: driver.get("https://www.ivasms.com/login")
        except: pass
        
        try: driver.uc_gui_click_captcha(); time.sleep(2)
        except: pass
        
        driver.wait_for_element('input[name="email"]', timeout=30)
        print("✅ CF bypassed! Entering credentials...")
        driver.type('input[name="email"]', EMAIL)
        driver.type('input[name="password"]', PASSWORD)
        
        time.sleep(7)
        try: driver.uc_gui_click_captcha(); time.sleep(3)
        except: pass
        
        print("🖱️ Clicking Login Submit Button...")
        try: driver.uc_click('button[type="submit"]')
        except: driver.click('button[type="submit"]')
            
        timeout_counter = 30
        while "login" in driver.current_url and timeout_counter > 0:
            time.sleep(1)
            timeout_counter -= 1
            
        if "login" in driver.current_url:
            print("❌ Login Failed! CF Blocked.")
            driver.quit()
            return None, None, None
            
        print("✅ Dashboard Reached! Moving to 'My SMS' page...")
        driver.get("https://www.ivasms.com/portal/sms/received")
        time.sleep(5)
        
        cookies = driver.get_cookies()
        user_agent = driver.execute_script("return navigator.userAgent;")
        
        try:
            page_token = driver.execute_script('return document.querySelector("meta[name=\'csrf-token\']").getAttribute("content");')
        except:
            page_token = ""
            
        cookie_dict = {}
        for c in cookies:
            cookie_dict[c['name']] = c['value']
            if c['name'] == 'XSRF-TOKEN' and not page_token:
                page_token = urllib.parse.unquote(c['value'])
        
        print("🍪 Fresh Cookies & Tokens Successfully Grabbed!")
        driver.quit() 
        return cookie_dict, user_agent, page_token
        
    except Exception as e:
        print(f"❌ Failed to grab cookies: {e}")
        if driver:
            try: driver.quit()
            except: pass
        return None, None, None

# ==========================================
# 📡 STEP 2: HUMAN-LIKE 3-STEP SCANNER (AI Powered)
# ==========================================
def monitor_ranges():
    global is_first_run, seen_signatures
    
    while True:
        try:
            cookie_dict, user_agent, page_token = get_fresh_cookies_and_tokens()
            
            if not cookie_dict:
                print("🔄 Auto-Login failed. Retrying in 30 seconds...")
                time.sleep(30)
                continue
                
            print("⚡ Starting Smart '3-Step' Scraper (Exact API Replication)...")
            scraper = cloudscraper.create_scraper()
            scraper.cookies.update(cookie_dict)
            
            headers = {
                "User-Agent": user_agent,
                "Accept": "text/html, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest", 
                "X-CSRF-TOKEN": page_token,
                "Origin": "https://www.ivasms.com",
                "Referer": "https://www.ivasms.com/portal/sms/received"
            }
            
            error_count = 0
            
            while error_count < 5:
                # ⚠️ Timezone Fix: স্ক্যানিং যাতে মিস না হয় তাই গতকাল এবং আজকের ডেট একসাথে চেক করবে
                date_list = [
                    time.strftime("%Y-%m-%d"), # Today
                    (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d") # Yesterday
                ]
                
                total_active_nums = 0
                
                try:
                    for target_date in date_list:
                        # ⚠️ API 1 Payload: আপনার স্ক্রিনশট অনুযায়ী 'from' এবং 'to' দেওয়া হলো
                        payload_ranges = {
                            "_token": page_token,
                            "from": target_date,
                            "to": target_date
                        }
                        
                        # ⚠️ ধাপ ১: Range আনবে
                        res_ranges = scraper.post("https://www.ivasms.com/portal/sms/received/getsms", headers=headers, data=payload_ranges, timeout=20)
                        
                        if res_ranges.status_code == 200:
                            ranges = re.findall(r"toggleRange\('([^']+)'", res_ranges.text)
                            
                            if not ranges:
                                continue # এই ডেটে না পেলে পরের ডেটে খুঁজবে

                            # ⚠️ ধাপ ২: Range থেকে Number আনবে (আপনার স্ক্রিনশট অনুযায়ী Payload)
                            for r in ranges:
                                payload_num = {
                                    "_token": page_token,
                                    "start": target_date,
                                    "end": target_date,
                                    "Range": r
                                }
                                res_num = scraper.post("https://www.ivasms.com/portal/sms/received/getsms/number", headers=headers, data=payload_num, timeout=15)
                                
                                if res_num.status_code == 200:
                                    raw_nums = re.findall(r"toggle[A-Za-z0-9_]*\(['\"]([^'\"]+)['\"]", res_num.text)
                                    numbers = list(set([n for n in raw_nums if n.isdigit() and len(n) >= 8]))
                                    
                                    total_active_nums += len(numbers)
                                    
                                    if not numbers:
                                        continue
                                    
                                    print(f"🔍 Checking Range [{target_date}]: {r} -> Found {len(numbers)} Active Numbers")
                                    
                                    # ⚠️ ধাপ ৩: Number থেকে SMS Table (HTML) আনবে (আপনার স্ক্রিনশট অনুযায়ী Payload)
                                    for num in numbers:
                                        payload_sms = payload_num.copy()
                                        payload_sms["Number"] = num
                                        res_sms = scraper.post("https://www.ivasms.com/portal/sms/received/getsms/number/sms", headers=headers, data=payload_sms, timeout=15)
                                        
                                        if res_sms.status_code == 200:
                                            soup = BeautifulSoup(res_sms.text, 'html.parser')
                                            rows = soup.find_all('tr')
                                            
                                            for row in reversed(rows):
                                                cols = row.find_all('td')
                                                if len(cols) >= 2:
                                                    service_raw = safe_text(cols[0].get_text(strip=True)).upper()
                                                    if service_raw == "SENDER" or not service_raw: continue
                                                    
                                                    msg_cell = cols[1].find('div', class_='msg-text')
                                                    if msg_cell:
                                                        full_text = safe_text(msg_cell.get_text(separator=" ", strip=True))
                                                    else:
                                                        full_text = safe_text(cols[1].get_text(separator=" ", strip=True))
                                                    
                                                    msg_signature = f"{num}_{service_raw}_{full_text}"
                                                    
                                                    if msg_signature not in seen_signatures:
                                                        if len(seen_signatures) > 1000:
                                                            seen_signatures.clear()
                                                            
                                                        seen_signatures.add(msg_signature)
                                                        
                                                        if is_first_run:
                                                            continue
                                                        
                                                        country_info, exact_range = get_country_and_exact_range(num, r)
                                                        otp_code = extract_otp(full_text)
                                                        service_title = service_raw.title()
                                                        
                                                        country_parts = country_info.split(' ')
                                                        country_name = country_parts[0]
                                                        flag = country_parts[1] if len(country_parts) > 1 else "🌐"

                                                        msg_body = (
                                                            f"{flag} {country_name} {service_title} Otp Code Received Successfully 🎉\n\n"
                                                            f"🔐 <b>Your OTP:</b> <code>{otp_code}</code>\n\n"
                                                            f"☎️ <b>Number:</b> <code>{exact_range}</code>\n"
                                                            f"⚙️ <b>Service:</b> {service_title}\n"
                                                            f"🌍 <b>Country:</b> {country_info}\n\n"
                                                            f"📩 <b>Full-Message:</b>\n"
                                                            f"<code>{full_text}</code>"
                                                        )
                                                        
                                                        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
                                                        markup.add(
                                                            telebot.types.InlineKeyboardButton("🚀 Panel", url="https://t.me/"),
                                                            telebot.types.InlineKeyboardButton("🛒 Buy IP", url="https://t.me/")
                                                        )
                                                        
                                                        try:
                                                            bot.send_message(GROUP_ID, msg_body, parse_mode="HTML", reply_markup=markup, disable_notification=True)
                                                            print(f"✅ PAID OTP Sent >> {service_title} | Number: {exact_range}")
                                                        except Exception as e:
                                                            print(f"❌ Telegram Error: {e}")
                                                            
                                        time.sleep(0.5) 
                                        
                    elif res_ranges.status_code in [401, 403, 419]:
                        print(f"🚨 Session Expired (Code {res_ranges.status_code}). Restarting login...")
                        error_count = 5 # Force break inner loop
                        break 
                    else:
                        error_count += 1
                        print(f"⚠️ API Error {res_ranges.status_code}. Retrying...")
                        
                if is_first_run:
                    print("✅ Pre-loaded old OTPs successfully! Now waiting for new ones...")
                    is_first_run = False
                    
                if total_active_nums == 0:
                    print("📭 Inbox is empty today. Waiting for OTPs...")
                    
                error_count = 0
                time.sleep(8) 
                
            print("🔄 Browser Session lost. Restarting the whole process...")
            
        except Exception as e:
            print(f"🔥 Critical System Error! Self-healing in 10s... Details: {e}")
            time.sleep(10)

if __name__ == "__main__":
    print("🤖 Paid SMS Bot is turning on (Ultimate 3-Step API Match!)...")
    threading.Thread(target=monitor_ranges, daemon=True).start()
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
        except Exception:
            time.sleep(3)
