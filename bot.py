import os
import time
import json
import re
import threading
import sqlite3
import html
import urllib.parse
from datetime import datetime, timedelta
import telebot
from telebot import types
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

# ⚠️ আপনার টেলিগ্রাম আইডি (অ্যাডমিন) এবং ওটিপি গ্রুপ
ADMIN_IDS = [123456789] # আপনার আসল টেলিগ্রাম আইডি দিন এখানে
GROUP_ID = "-1003871481057" # পেইড ওটিপি গ্রুপ

DB_PATH = "bot.db"

# ==========================================
# 🌍 SERVICE & COUNTRY SETTINGS
# ==========================================
SERVICE_LOGOS = {
    "WHATSAPP": "🟢", "FACEBOOK": "📘", "TELEGRAM": "✈️",
    "TIKTOK": "🎵", "GOOGLE": "🔴", "VIBER": "🟪", "MICROSOFT": "🪟",
    "SHEIN": "👗", "HUAWEI": "🟥"
}

COUNTRY_DICT = {
    "1": ("USA/Canada", "🇺🇸"), "7": ("Russia", "🇷🇺"), "20": ("Egypt", "🇪🇬"), 
    "27": ("South Africa", "🇿🇦"), "31": ("Netherlands", "🇳🇱"), "33": ("France", "🇫🇷"), 
    "34": ("Spain", "🇪🇸"), "39": ("Italy", "🇮🇹"), "44": ("UK", "🇬🇧"), 
    "49": ("Germany", "🇩🇪"), "55": ("Brazil", "🇧🇷"), "60": ("Malaysia", "🇲🇾"), 
    "62": ("Indonesia", "🇮🇩"), "63": ("Philippines", "🇵🇭"), "66": ("Thailand", "🇹🇭"), 
    "84": ("Vietnam", "🇻🇳"), "86": ("China", "🇨🇳"), "91": ("India", "🇮🇳"), 
    "92": ("Pakistan", "🇵🇰"), "212": ("Morocco", "🇲🇦"), "234": ("Nigeria", "🇳🇬"), 
    "880": ("Bangladesh", "🇧🇩"), "966": ("Saudi Arabia", "🇸🇦"), "971": ("UAE", "🇦🇪"),
    "998": ("Uzbekistan", "🇺🇿")
}

# ==========================================
# 🗄️ RAMOS DATABASE SYSTEM (SQLite)
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, assigned_number TEXT, service TEXT, otp TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, service TEXT, country TEXT, number TEXT, status TEXT DEFAULT 'available')''')
    conn.commit()
    conn.close()

init_db()

def add_numbers_to_db(service, country, numbers_list):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    count = 0
    for num in numbers_list:
        clean_num = re.sub(r'\D', '', str(num))
        if clean_num:
            c.execute("INSERT INTO inventory (service, country, number) VALUES (?, ?, ?)", (service.upper(), country.upper(), clean_num))
            count += 1
    conn.commit()
    conn.close()
    return count

def get_available_number(service, country):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, number FROM inventory WHERE service=? AND country=? AND status='available' LIMIT 1", (service.upper(), country.upper()))
    row = c.fetchone()
    if row:
        c.execute("UPDATE inventory SET status='assigned' WHERE id=?", (row[0],))
        conn.commit()
        conn.close()
        return row[1]
    conn.close()
    return None

def assign_user_number(user_id, number, service):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO users (user_id, assigned_number, service, otp) VALUES (?, ?, ?, NULL)", (user_id, number, service))
    conn.commit()
    conn.close()

def get_user_data(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT assigned_number, service, otp FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def update_user_otp(number, otp_code):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET otp=? WHERE assigned_number=?", (otp_code, number))
    c.execute("SELECT user_id FROM users WHERE assigned_number=?", (number,))
    user_row = c.fetchone()
    conn.commit()
    conn.close()
    return user_row[0] if user_row else None

# ==========================================
# 🤖 TELEGRAM BOT UI (RAMOS STYLE)
# ==========================================
bot = telebot.TeleBot(BOT_TOKEN)
try: bot.remove_webhook()
except: pass

@bot.message_handler(commands=['add'])
def add_nums_cmd(message):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        parts = message.text.split('\n')
        header = parts[0].split()
        service = header[1]
        country = header[2]
        nums = parts[1:]
        added = add_numbers_to_db(service, country, nums)
        bot.reply_to(message, f"✅ {added} numbers added for {service} {country}!")
    except:
        bot.reply_to(message, "❌ Format error. Use:\n/add SERVICE COUNTRY\nnumber1\nnumber2")

@bot.message_handler(commands=['start'])
def start_cmd(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📲 Get Number", callback_data="get_num"))
    bot.send_message(message.chat.id, "<b>❍ 𝐖𝐄𝐋𝐂𝐎𝐌 𝐓𝐎 𝐏𝐀𝐈𝐃 𝐒𝐌𝐒 𝐁𝐎𝐓 ❍</b>\n\nClick below to get a number:", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "get_num")
def get_num_menu(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🟢 WhatsApp", callback_data="buy_WHATSAPP_BANGLADESH"),
        types.InlineKeyboardButton("✈️ Telegram", callback_data="buy_TELEGRAM_RUSSIA")
    )
    bot.edit_message_text("Select Service:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def process_buy(call):
    parts = call.data.split('_')
    service = parts[1]
    country = parts[2]
    
    number = get_available_number(service, country)
    if number:
        assign_user_number(call.from_user.id, number, service)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("View OTP 📩", callback_data="view_otp"))
        msg = f"<b>{service} Fresh Number Assigned</b>\n\nNumber: <code>+{number}</code>\n\n⏳ <i>বটের ভিতর অপেক্ষা করুন ওটিপির জন্য...</i>"
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "❌ No numbers available in stock!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "view_otp")
def view_otp_cmd(call):
    user_data = get_user_data(call.from_user.id)
    if user_data and user_data[2]: 
        bot.answer_callback_query(call.id, f"✅ Your OTP: {user_data[2]}", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "⏳ OTP not received yet. Please wait...", show_alert=False)

# ==========================================
# 🧠 SMART AI EXTRACTORS
# ==========================================
def extract_otp(full_text):
    match = re.search(r'(?<!\d)(\d{4,8})(?!\d)', full_text)
    if match: return match.group(1)
    match_dash = re.search(r'\b(\d{3}[-\s]\d{3})\b', full_text)
    if match_dash: return match_dash.group(1)
    return "N/A"

def safe_text(text):
    if not text: return "Unknown"
    text = str(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    return re.sub(r'\s+', ' ', text).replace('<', '').replace('>', '').strip()

def get_country_info(number):
    num_str = "".join(filter(str.isdigit, str(number)))
    while num_str.startswith('0'): num_str = num_str[1:]
    exact_range = num_str if num_str else str(number)
    
    for length in [4, 3, 2, 1]:  
        if len(exact_range) >= length:
            prefix = exact_range[:length]
            if prefix in COUNTRY_DICT:
                name, flag = COUNTRY_DICT[prefix]
                return f"{name} {flag}", exact_range
    return "Unknown Country 🌐", exact_range

# ==========================================
# 🌐 STEP 1: AUTO-LOGIN & STEAL COOKIE
# ==========================================
def get_fresh_cookies_and_tokens():
    print("🚀 Launching AI Browser to login to Paid Account...")
    driver = None
    try:
        # ⚠️ CRITICAL FIX: headless=False is REQUIRED to bypass Cloudflare on GitHub Servers
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
# 📡 STEP 2: HYBRID 3-STEP SCANNER
# ==========================================
seen_signatures = set()
is_first_run = True

def monitor_ranges():
    global is_first_run, seen_signatures
    
    while True:
        try:
            cookie_dict, user_agent, page_token = get_fresh_cookies_and_tokens()
            
            if not cookie_dict:
                print("🔄 Auto-Login failed. Retrying in 30 seconds...")
                time.sleep(30)
                continue
                
            print("⚡ Starting Hybrid '3-Step' Scraper...")
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
                bd_time = datetime.utcnow() + timedelta(hours=6)
                date_list = [
                    bd_time.strftime("%Y-%m-%d"), 
                    (bd_time - timedelta(days=1)).strftime("%Y-%m-%d")
                ]
                
                try:
                    for target_date in date_list:
                        base_payload = {
                            "_token": page_token,
                            "from": target_date,
                            "to": target_date
                        }
                        
                        res_ranges = scraper.post("https://www.ivasms.com/portal/sms/received/getsms", headers=headers, data=base_payload, timeout=20)
                        
                        if res_ranges.status_code == 200:
                            ranges = re.findall(r"toggleRange\('([^']+)'", res_ranges.text)
                            if not ranges: continue 

                            for r in ranges:
                                payload_num = base_payload.copy()
                                payload_num["Range"] = r
                                res_num = scraper.post("https://www.ivasms.com/portal/sms/received/getsms/number", headers=headers, data=payload_num, timeout=15)
                                
                                if res_num.status_code == 200:
                                    raw_nums = re.findall(r"toggleSms\('([^']+)'", res_num.text)
                                    numbers = list(set([n for n in raw_nums if n.isdigit() and len(n) >= 8]))
                                    
                                    if not numbers: continue
                                    
                                    print(f"🔍 Checking Range [{target_date}]: {r} -> Found {len(numbers)} Active Numbers")
                                    
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
                                                    if msg_cell: full_text = safe_text(msg_cell.get_text(separator=" ", strip=True))
                                                    else: full_text = safe_text(cols[1].get_text(separator=" ", strip=True))
                                                    
                                                    msg_signature = f"{num}_{service_raw}_{full_text}"
                                                    
                                                    if msg_signature not in seen_signatures:
                                                        if len(seen_signatures) > 1000:
                                                            seen_signatures.clear()
                                                            
                                                        seen_signatures.add(msg_signature)
                                                        
                                                        if is_first_run: continue
                                                        
                                                        country_info, exact_range = get_country_and_exact_range(num, r)
                                                        otp_code = extract_otp(full_text)
                                                        service_title = service_raw.title()
                                                        
                                                        # 🗄️ Database Check & User Notify
                                                        buyer_id = update_user_otp(num, otp_code)
                                                        if buyer_id:
                                                            try: bot.send_message(buyer_id, f"✅ <b>OTP Received!</b>\nCode: <code>{otp_code}</code>", parse_mode="HTML")
                                                            except: pass

                                                        # 🌟 GROUP MESSAGE (PAID OTP STYLE)
                                                        flag = SERVICE_LOGOS.get(service_raw, "🌐")
                                                        msg_body = (
                                                            f"{flag} {country_info.split(' ')[0]} {service_title} Otp Code Received Successfully 🎉\n\n"
                                                            f"🔐 <b>Your OTP:</b> <code>{otp_code}</code>\n\n"
                                                            f"☎️ <b>Number:</b> <code>{exact_range}</code>\n"
                                                            f"⚙️ <b>Service:</b> {service_title}\n"
                                                            f"🌍 <b>Country:</b> {country_info}\n\n"
                                                            f"📩 <b>Full-Message:</b>\n"
                                                            f"<code>{full_text}</code>"
                                                        )
                                                        
                                                        markup = telebot.types.InlineKeyboardMarkup()
                                                        markup.add(telebot.types.InlineKeyboardButton("🚀 Panel", url="https://t.me/"))
                                                        
                                                        try:
                                                            bot.send_message(GROUP_ID, msg_body, parse_mode="HTML", reply_markup=markup, disable_notification=True)
                                                            print(f"✅ PAID OTP Sent >> {service_title} | Number: {exact_range}")
                                                        except Exception as e:
                                                            print(f"❌ Telegram Error: {e}")
                                                            
                                        time.sleep(0.5) 
                                        
                    if is_first_run:
                        print("✅ Pre-loaded old OTPs successfully! Now waiting for new ones...")
                        is_first_run = False
                        
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
    print("🤖 Paid SMS Bot & Panel is turning on (Hybrid Scanner!)...")
    threading.Thread(target=monitor_ranges, daemon=True).start()
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
        except Exception:
            time.sleep(3)
