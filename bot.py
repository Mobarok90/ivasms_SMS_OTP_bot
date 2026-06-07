import os
import time
import json
import re
import threading
import sqlite3
import html
from datetime import datetime, timedelta
import telebot
from telebot import types
import logging
from bs4 import BeautifulSoup
from seleniumbase import Driver

telebot.logger.setLevel(logging.ERROR)

# ==========================================
# ⚙️ ADVANCED CONFIGURATION
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

COUNTRY_CODES = {
    "1": ("USA/Canada", "🇺🇸"), "7": ("Russia", "🇷🇺"), "20": ("Egypt", "🇪🇬"), 
    "27": ("South Africa", "🇿🇦"), "31": ("Netherlands", "🇳🇱"), "33": ("France", "🇫🇷"), 
    "34": ("Spain", "🇪🇸"), "39": ("Italy", "🇮🇹"), "44": ("UK", "🇬🇧"), 
    "49": ("Germany", "🇩🇪"), "55": ("Brazil", "🇧🇷"), "60": ("Malaysia", "🇲🇾"), 
    "62": ("Indonesia", "🇮🇩"), "63": ("Philippines", "🇵🇭"), "66": ("Thailand", "🇹🇭"), 
    "84": ("Vietnam", "🇻🇳"), "86": ("China", "🇨🇳"), "91": ("India", "🇮🇳"), 
    "92": ("Pakistan", "🇵🇰"), "212": ("Morocco", "🇲🇦"), "234": ("Nigeria", "🇳🇬"), 
    "880": ("Bangladesh", "🇧🇩"), "966": ("Saudi Arabia", "🇸🇦"), "971": ("UAE", "🇦🇪")
    # আরও দেশ চাইলে এখানে অ্যাড করতে পারবেন
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
    # Format: /add WHATSAPP BANGLADESH 88017... 88018...
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
    # Demo static buttons, you can make dynamic from DB
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
        msg = f"<b>{service} Fresh Number Assigned</b>\n\nNumber: <code>+{number}</code>\n\n⏳ <i>বটের ভিতর অপেক্ষা করুন...</i>"
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "❌ No numbers available in stock!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "view_otp")
def view_otp_cmd(call):
    user_data = get_user_data(call.from_user.id)
    if user_data and user_data[2]: # If OTP exists
        bot.answer_callback_query(call.id, f"✅ Your OTP: {user_data[2]}", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "⏳ OTP not received yet. Please wait...", show_alert=False)

# ==========================================
# 🧠 SMART AI EXTRACTORS (No HTML Class needed!)
# ==========================================
def extract_otp(full_text):
    match = re.search(r'(?<!\d)(\d{4,8})(?!\d)', full_text)
    if match: return match.group(1)
    match_dash = re.search(r'\b(\d{3}[-\s]\d{3})\b', full_text)
    if match_dash: return match_dash.group(1)
    return "N/A"

def extract_phone_number(text):
    match = re.search(r'\b\d{8,15}\b', text)
    return match.group(0) if match else "Unknown"

# ==========================================
# 🌐 FULL BROWSER AUTOMATION (API BYPASS)
# ==========================================
seen_messages = set()

def start_browser_automation():
    global seen_messages
    
    while True:
        driver = None
        try:
            print("🚀 Booting up AI Browser (Headless Mode)...")
            # GitHub Server এ চলার জন্য Headless True রাখতে হয়, নাহলে ক্র্যাশ করে
            driver = Driver(uc=True, headless=True)
            driver.set_page_load_timeout(60)
            
            print("🔐 Navigating to iVASMS login...")
            driver.get("https://www.ivasms.com/login")
            
            print("⏳ Waiting for Email Field...")
            driver.wait_for_element('input[name="email"]', timeout=30)
            
            print("✅ Entering credentials...")
            driver.type('input[name="email"]', EMAIL)
            driver.type('input[name="password"]', PASSWORD)
            
            time.sleep(5)
            try: driver.uc_gui_click_captcha(); time.sleep(3)
            except: pass
            
            print("🖱️ Clicking Login...")
            try: driver.js_click('button[type="submit"]')
            except: driver.click('button[type="submit"]')
                
            time.sleep(10)
            if "login" in driver.current_url:
                print("❌ Login Failed! Cloudflare blocked. Retrying...")
                driver.quit()
                time.sleep(20)
                continue
                
            print("✅ Login Success! Moving to Dashboard...")
            
            # 🔄 24/7 Monitoring Loop inside the Browser
            error_count = 0
            while error_count < 5:
                try:
                    driver.get("https://www.ivasms.com/portal/sms/received")
                    time.sleep(5)
                    
                    # ⚠️ BD Timezone Fix (UTC+6)
                    bd_time = datetime.utcnow() + timedelta(hours=6)
                    today_str = bd_time.strftime("%Y-%m-%d")
                    yesterday_str = (bd_time - timedelta(days=1)).strftime("%Y-%m-%d")
                    
                    print(f"📅 Setting Dates (BD Time): {yesterday_str} to {today_str}")
                    
                    # Inject JavaScript to set dates and click "Get SMS"
                    js_script = f"""
                    document.getElementById('start_date').value = '{yesterday_str}';
                    document.getElementById('end_date').value = '{today_str}';
                    var btns = document.getElementsByTagName('button');
                    for(var i=0; i<btns.length; i++) {{
                        if(btns[i].innerText.includes('Get SMS')) {{ btns[i].click(); }}
                    }}
                    """
                    driver.execute_script(js_script)
                    
                    print("⏳ Waiting for table to load...")
                    time.sleep(10) # টেবিল লোড হওয়ার জন্য অপেক্ষা
                    
                    # 🧠 AI VISUAL TEXT READER: No HTML Class needed!
                    page_html = driver.get_page_source()
                    soup = BeautifulSoup(page_html, 'html.parser')
                    
                    # টেবিলের শাড়িগুলো (Rows) খুঁজবে
                    rows = soup.find_all('tr')
                    
                    for row in reversed(rows):
                        row_text = row.get_text(separator=" | ", strip=True)
                        
                        # যদি শাড়িতে কোনো নাম্বার থাকে (৮-১৫ ডিজিট), তারমানে এটা ওটিপির লাইন!
                        if re.search(r'\d{8,15}', row_text):
                            raw_num = extract_phone_number(row_text)
                            service = "UNKNOWN"
                            for s in SERVICE_LOGOS.keys():
                                if s.lower() in row_text.lower():
                                    service = s
                                    break
                            
                            otp_code = extract_otp(row_text)
                            
                            msg_hash = f"{raw_num}_{service}_{otp_code}"
                            if msg_hash not in seen_messages:
                                seen_messages.add(msg_hash)
                                
                                # 🗄️ Database Update & Notification
                                user_id = update_user_otp(raw_num, otp_code)
                                
                                if user_id: # যদি নাম্বারটি কোনো ইউজারের কেনা হয়ে থাকে
                                    try:
                                        bot.send_message(user_id, f"✅ <b>OTP Received!</b>\nCode: <code>{otp_code}</code>", parse_mode="HTML")
                                    except: pass
                                
                                # 🌟 GROUP MESSAGE (PAID OTP STYLE)
                                flag = SERVICE_LOGOS.get(service, "🌐")
                                msg_body = (
                                    f"🌍 {service.title()} Otp Code Received Successfully 🎉\n\n"
                                    f"🔐 <b>Your OTP:</b> <code>{otp_code}</code>\n\n"
                                    f"☎️ <b>Number:</b> <code>{raw_number}</code>\n"
                                    f"⚙️ <b>Service:</b> {service.title()}\n\n"
                                    f"📩 <b>Raw Text:</b>\n"
                                    f"<code>{row_text}</code>"
                                )
                                markup = types.InlineKeyboardMarkup()
                                markup.add(types.InlineKeyboardButton("🚀 Panel", url="https://t.me/"))
                                
                                try:
                                    bot.send_message(GROUP_ID, msg_body, parse_mode="HTML", reply_markup=markup, disable_notification=True)
                                    print(f"✅ PAID OTP Sent >> {service} | {raw_num}")
                                except Exception as e:
                                    print(f"❌ Telegram Error: {e}")
                                    
                    error_count = 0
                    time.sleep(15) # প্রতি ১৫ সেকেন্ড পর পর আবার Get SMS এ ক্লিক করবে
                    
                except Exception as e:
                    print(f"⚠️ Table parsing error: {e}")
                    error_count += 1
                    time.sleep(5)
            
            print("🔄 Browser session error limit reached. Restarting Browser...")
            driver.quit()
            
        except Exception as e:
            print(f"🔥 Critical Error! Recovering... Details: {e}")
            if driver:
                try: driver.quit()
                except: pass
            time.sleep(15)

if __name__ == "__main__":
    print("🤖 Paid SMS Panel & Scanner is turning on...")
    threading.Thread(target=start_browser_automation, daemon=True).start()
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
        except Exception:
            time.sleep(3)
