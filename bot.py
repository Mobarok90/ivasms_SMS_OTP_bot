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
    "51": ("Peru", "🇵🇪"), "52": ("Mexico", "🇲🇽"), "54": ("Argentina", "🇦🇷"), 
    "55": ("Brazil", "🇧🇷"), "57": ("Colombia", "🇨🇴"), "60": ("Malaysia", "🇲🇾"), 
    "62": ("Indonesia", "🇮🇩"), "63": ("Philippines", "🇵🇭"), "66": ("Thailand", "🇹🇭"), 
    "81": ("Japan", "🇯🇵"), "82": ("South Korea", "🇰🇷"), "84": ("Vietnam", "🇻🇳"), 
    "86": ("China", "🇨🇳"), "90": ("Turkey", "🇹🇷"), "91": ("India", "🇮🇳"), 
    "92": ("Pakistan", "🇵🇰"), "93": ("Afghanistan", "🇦🇫"), "98": ("Iran", "🇮🇷"), 
    "212": ("Morocco", "🇲🇦"), "234": ("Nigeria", "🇳🇬"), "249": ("Sudan", "🇸🇩"), 
    "251": ("Ethiopia", "🇪🇹"), "254": ("Kenya", "🇰🇪"), "351": ("Portugal", "🇵🇹"), 
    "380": ("Ukraine", "🇺🇦"), "880": ("Bangladesh", "🇧🇩"), "966": ("Saudi Arabia", "🇸🇦"), 
    "971": ("UAE", "🇦🇪"), "998": ("Uzbekistan", "🇺🇿")
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
                
            print("⚡ Starting Smart '3-Step' Scraper (BD Timezone + X-Ray Extractor)...")
            scraper = cloudscraper.create_scraper()
            scraper.cookies.update(cookie_dict)
            
            headers = {
                "User-Agent": user_agent,
                "Accept": "text/html, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest", 
                "X-CSRF-TOKEN": page_token,
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "https://www.ivasms.com",
                "Referer": "https://www.ivasms.com/portal/sms/received"
            }
            
            error_count = 0
            
            while error_count < 5:
                # ⚠️ Timezone Fix: গিটহাবের UTC টাইমকে +6 ঘণ্টা যোগ করে "বাংলাদেশ টাইম" বানানো হলো!
                bd_time = datetime.utcnow() + timedelta(hours=6)
                date_list = [
                    bd_time.strftime("%Y-%m-%d"), # Today (BD Time)
                    (bd_time - timedelta(days=1)).strftime("%Y-%m-%d") # Yesterday (BD Time)
                ]
                
                total_active_nums = 0
                
                try:
                    for target_date in date_list:
                        base_payload = {
                            "_token": page_token,
                            "start": target_date,
                            "end": target_date
                        }
                        
                        # ⚠️ ধাপ ১: Range আনবে
                        res_ranges = scraper.post("https://www.ivasms.com/portal/sms/received/getsms", headers=headers, data=base_payload, timeout=20)
                        
                        if res_ranges.status_code == 200:
                            # 🧠 X-RAY RANGE EXTRACTOR: HTML থেকে যেকোনো "COUNTRY_NAME 1234" ফরম্যাটের লেখা টেনে আনবে!
                            soup_ranges = BeautifulSoup(res_ranges.text, 'html.parser')
                            raw_text = soup_ranges.get_text(separator=" ")
                            
                            ranges_from_text = re.findall(r'\b[A-Z]+(?:\s[A-Z]+)*\s\d{2,8}\b', raw_text)
                            ranges_from_html = re.findall(r"['\"]([A-Z\s]+\s\d{2,8})['\"]", res_ranges.text)
                            
                            ranges = list(set(ranges_from_text + ranges_from_html))
                            valid_ranges = [r.strip() for r in ranges if len(r) > 5]
                            
                            if not valid_ranges:
                                continue 

                            # ⚠️ ধাপ ২: Range থেকে Number আনবে
                            for r in valid_ranges:
                                payload_num = base_payload.copy()
                                payload_num["Range"] = r
                                res_num = scraper.post("https://www.ivasms.com/portal/sms/received/getsms/number", headers=headers, data=payload_num, timeout=15)
                                
                                if res_num.status_code == 200:
                                    # 🧠 X-RAY NUMBER EXTRACTOR: যেকোনো ৮ থেকে ১৫ ডিজিটের নাম্বার বের করবে!
                                    soup_num = BeautifulSoup(res_num.text, 'html.parser')
                                    num_text = soup_num.get_text(separator=" ")
                                    
                                    nums_from_text = re.findall(r'(?<!\d)\d{8,15}(?!\d)', num_text)
                                    nums_from_html = re.findall(r"['\"](\d{8,15})['\"]", res_num.text)
                                    
                                    numbers = list(set(nums_from_text + nums_from_html))
                                    total_active_nums += len(numbers)
                                    
                                    if not numbers:
                                        continue
                                    
                                    print(f"🔍 Checking Range [{target_date}]: {r} -> Found {len(numbers)} Active Numbers")
                                    
                                    # ⚠️ ধাপ ৩: Number থেকে SMS Table (HTML) আনবে
                                    for num in numbers:
                                        payload_sms = payload_num.copy()
                                        payload_sms["Number"] = num
                                        res_sms = scraper.post("https://www.ivasms.com/portal/sms/received/getsms/number/sms", headers=headers, data=payload_sms, timeout=15)
                                        
                                        if res_sms.status_code == 200:
                                            # HTML পার্স করে ওটিপি বের করা
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

                                                        # 🌟 RS OTP BOT STYLE DESIGN
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
                                                            # ⚠️ Mute Mode ON
                                                            bot.send_message(GROUP_ID, msg_body, parse_mode="HTML", reply_markup=markup, disable_notification=True)
                                                            print(f"✅ PAID OTP Sent >> {service_title} | Number: {exact_range}")
                                                        except Exception as e:
                                                            print(f"❌ Telegram Error: {e}")
                                                            
                                        time.sleep(0.5) 
                                        
                    if is_first_run:
                        print("✅ Pre-loaded old OTPs successfully! Now waiting for new ones...")
                        is_first_run = False
                        
                    if total_active_nums == 0:
                        print(f"📭 Inbox empty for {date_list[0]} & {date_list[1]}. Waiting for OTPs...")
                        
                    error_count = 0 
                    
                except Exception as e:
                    print(f"⚠️ Script Execution Error: {e}")
                    error_count += 1
                    
                time.sleep(8) 
                
            print("🔄 Browser Session lost. Restarting the whole process...")
            
        except Exception as e:
            print(f"🔥 Critical System Error! Self-healing in 10s... Details: {e}")
            time.sleep(10)

if __name__ == "__main__":
    print("🤖 Paid SMS Bot is turning on (Bangladesh Timezone & X-Ray AI Extractor)...")
    threading.Thread(target=monitor_ranges, daemon=True).start()
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
        except Exception:
            time.sleep(3)
