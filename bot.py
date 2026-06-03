import os
import time
import json
import re
import threading
import html
import urllib.parse
from datetime import datetime
import telebot
import cloudscraper
import logging
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

# ⚠️ MASTER JSON API (সবচেয়ে ফাস্ট এবং নির্ভুল লিঙ্ক)
API_URL = "https://www.ivasms.com/portal/live/my_sms"

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

def get_country_and_exact_range(number):
    num_str = "".join(filter(str.isdigit, str(number)))
    while num_str.startswith('0'): num_str = num_str[1:]
    exact_range = num_str if num_str else str(number)
    country_info = "Unknown Country 🌐"
    
    for length in [4, 3, 2, 1]:  
        if len(exact_range) >= length:
            prefix = exact_range[:length]
            if prefix in COUNTRY_DICT:
                name, flag = COUNTRY_DICT[prefix]
                country_info = f"{name} {flag}"
                break
                
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
# 🌐 STEP 1: AUTO-LOGIN & SECURE TOKENS
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
        try: driver.js_click('button[type="submit"]')
        except: driver.click('button[type="submit"]')
            
        timeout_counter = 30
        while "login" in driver.current_url and timeout_counter > 0:
            time.sleep(1)
            timeout_counter -= 1
            
        if "login" in driver.current_url:
            print("❌ Login Failed! CF Blocked.")
            driver.quit()
            return None, None, None
            
        print("✅ Dashboard Reached! Letting cookies settle...")
        time.sleep(5)
        
        cookies = driver.get_cookies()
        user_agent = driver.execute_script("return navigator.userAgent;")
        
        cookie_dict = {}
        xsrf_token = ""
        for c in cookies:
            cookie_dict[c['name']] = c['value']
            if c['name'] == 'XSRF-TOKEN':
                xsrf_token = urllib.parse.unquote(c['value'])
        
        print("🍪 Fresh Cookies & Tokens Successfully Grabbed!")
        driver.quit() 
        return cookie_dict, user_agent, xsrf_token
        
    except Exception as e:
        print(f"❌ Failed to grab cookies: {e}")
        if driver:
            try: driver.quit()
            except: pass
        return None, None, None

# ==========================================
# 📡 STEP 2: ULTRA FAST JSON LIVE FEED SCANNER
# ==========================================
def monitor_ranges():
    global is_first_run, seen_signatures
    
    while True:
        try:
            cookie_dict, user_agent, xsrf_token = get_fresh_cookies_and_tokens()
            
            if not cookie_dict:
                print("🔄 Auto-Login failed. Retrying in 30 seconds...")
                time.sleep(30)
                continue
                
            print("⚡ Starting Ultra Fast JSON Scanner...")
            scraper = cloudscraper.create_scraper()
            scraper.cookies.update(cookie_dict)
            
            headers = {
                "User-Agent": user_agent,
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest", 
                "X-XSRF-TOKEN": xsrf_token,
                "Origin": "https://www.ivasms.com",
                "Referer": "https://www.ivasms.com/portal/sms/received"
            }
            
            error_count = 0
            
            while error_count < 5:
                try:
                    # ⚠️ ডাইরেক্ট JSON API লিঙ্ক ব্যবহার করা হলো
                    response = scraper.get(API_URL, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        try:
                            json_data = response.json()
                        except ValueError:
                            print("🚨 Server returned HTML instead of JSON. Retrying...")
                            error_count += 1
                            time.sleep(10)
                            continue
                            
                        sms_list = json_data.get('data', [])
                        
                        if not sms_list or len(sms_list) == 0:
                            if is_first_run:
                                print("📭 Inbox is currently empty. Waiting for OTPs...")
                                is_first_run = False
                            error_count = 0
                            time.sleep(8)
                            continue

                        if is_first_run:
                            print(f"📥 Found {len(sms_list)} OTPs in inbox. Forwarding ALL to the group...")
                            is_first_run = False

                        for sms in reversed(sms_list):
                            service_raw = safe_text(sms.get('originator', sms.get('sender', 'Unknown'))).upper()
                            
                            # TIKTOKADS ব্লক এবং ফিল্টার
                            if any(blocked in service_raw for blocked in BLOCKED_SERVICES): continue
                            if not any(allowed in service_raw for allowed in ALLOWED_SERVICES): continue 
                            
                            term_data = sms.get('termination', {})
                            raw_number = str(sms.get('number', sms.get('receiver', term_data.get('test_number', 'Unknown'))))
                            full_text = safe_text(sms.get('messagedata', sms.get('message', 'No Text')))
                            
                            # ⚠️ ডাবল মেসেজ ব্লক করার সিগনেচার
                            msg_signature = f"{raw_number}_{service_raw}_{full_text}"
                            
                            if msg_signature not in seen_signatures:
                                if len(seen_signatures) > 1000:
                                    seen_signatures.clear()
                                    
                                seen_signatures.add(msg_signature)
                                
                                country_info, exact_range = get_country_and_exact_range(raw_number)
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
                                    # ⚠️ সাইলেন্ট মেসেজ (MUTE)
                                    bot.send_message(GROUP_ID, msg_body, parse_mode="HTML", reply_markup=markup, disable_notification=True)
                                    print(f"✅ PAID OTP Sent >> {service_title} | Number: {exact_range}")
                                    time.sleep(2) 
                                except Exception as e:
                                    print(f"❌ Telegram Error: {e}")
                                    
                        error_count = 0 
                        
                    elif response.status_code in [401, 403, 419]:
                        print(f"🚨 Session Expired (Code {response.status_code}). Restarting login...")
                        break 
                    else:
                        error_count += 1
                        print(f"⚠️ API Error {response.status_code}. Retrying...")
                        
                except Exception as e:
                    print(f"⚠️ Fetch Error: {e}")
                    error_count += 1
                    
                time.sleep(8) 
                
            print("🔄 Browser Session lost. Restarting the whole process...")
            
        except Exception as e:
            print(f"🔥 Critical System Error! Self-healing in 10s... Details: {e}")
            time.sleep(10)

if __name__ == "__main__":
    print("🤖 Paid SMS Bot is turning on (JSON Feed + Full Countries + Mute!)...")
    threading.Thread(target=monitor_ranges, daemon=True).start()
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
        except Exception:
            time.sleep(3)
