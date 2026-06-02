import os
import time
import json
import re
import threading
import html
import urllib.parse
from datetime import datetime
import telebot
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

# ==========================================
# 🎯 SERVICE FILTERS & LOGOS
# ==========================================
SERVICE_LOGOS = {
    "WHATSAPP": "🟢 WhatsApp", "FACEBOOK": "📘 Facebook", "TELEGRAM": "✈️ Telegram",
    "TIKTOK": "🎵 TikTok", "GOOGLE": "🔴 Google", "VIBER": "🟪 Viber", "MICROSOFT": "🪟 Microsoft",
    "SHEIN": "👗 SHEIN", "HUAWEI": "🟥 Huawei"
}

# ==========================================
# 🌍 SUPER MASSIVE COUNTRY DICTIONARY (270+ Codes)
# ==========================================
COUNTRY_DICT = {
    "1": ("USA/Canada", "🇺🇸/🇨🇦"), "7": ("Russia/KZ", "🇷🇺/🇰🇿"), "20": ("Egypt", "🇪🇬"), 
    "27": ("South Africa", "🇿🇦"), "30": ("Greece", "🇬🇷"), "31": ("Netherlands", "🇳🇱"), 
    "32": ("Belgium", "🇧🇪"), "33": ("France", "🇫🇷"), "34": ("Spain", "🇪🇸"), 
    "36": ("Hungary", "🇭🇺"), "39": ("Italy", "🇮🇹"), "40": ("Romania", "🇷🇴"), 
    "41": ("Switzerland", "🇨🇭"), "42": ("Czech/Slovakia", "🇨🇿/🇸🇰"), "43": ("Austria", "🇦🇹"), 
    "44": ("UK", "🇬🇧"), "45": ("Denmark", "🇩🇰"), "46": ("Sweden", "🇸🇪"), 
    "47": ("Norway", "🇳🇴"), "48": ("Poland", "🇵🇱"), "49": ("Germany", "🇩🇪"), 
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

seen_messages = set()
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
    text = re.split(r'<script|function|\$\(', text, flags=re.IGNORECASE)[0]
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
# 🤖 AI CORE: 24/7 BROWSER AUTOMATION (VIDEO LOGIC)
# ==========================================
def run_smart_bot():
    global is_first_run, seen_messages, seen_signatures
    driver = None
    
    while True:
        try:
            print("🚀 Booting up invisible AI Browser...")
            driver = Driver(uc=True, headless=False) # Headless=False helps bypass CF
            driver.set_page_load_timeout(60)
            
            # 1. Login Process
            print("🔐 Navigating to iVASMS login...")
            try: driver.get("https://www.ivasms.com/login")
            except: pass
            
            print("⏳ Waiting for Email Field...")
            # Smart Wait: wait up to 40 seconds, but move instantly if found
            driver.wait_for_element('input[name="email"]', timeout=40)
            
            print("✅ CF bypassed! Entering credentials...")
            driver.type('input[name="email"]', EMAIL)
            driver.type('input[name="password"]', PASSWORD)
            
            print("⏳ Waiting 5 seconds for Turnstile to auto-resolve...")
            time.sleep(5)
            
            try: driver.uc_gui_click_captcha(); time.sleep(2)
            except: pass
            
            print("🖱️ Clicking Login Button...")
            try: driver.uc_click('button[type="submit"]')
            except: driver.click('button[type="submit"]')
                
            print("⏳ Waiting for Dashboard to load...")
            timeout_counter = 30
            while "login" in driver.current_url and timeout_counter > 0:
                time.sleep(1)
                timeout_counter -= 1
                
            if "login" in driver.current_url:
                print("❌ Login Failed! Restarting process...")
                driver.quit()
                time.sleep(10)
                continue
                
            print("✅ Login Successful! Moving to 'My SMS' Page (Video Logic)...")
            
            # 2. Navigate to the exact page shown in the video
            driver.get("https://www.ivasms.com/portal/sms/received")
            time.sleep(5) # Let the page load
            
            print("📡 Starting 24/7 OTP Scanning Loop...")
            
            # 3. Inject JS to fetch data directly via the browser's authenticated session
            fetch_script = """
            var callback = arguments[arguments.length - 1];
            var csrf = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            var xhr = new XMLHttpRequest();
            xhr.open('POST', 'https://www.ivasms.com/portal/sms/received/getsms', true);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            xhr.setRequestHeader('X-CSRF-TOKEN', csrf);
            xhr.onreadystatechange = function() {
                if (xhr.readyState == 4) {
                    callback({status: xhr.status, text: xhr.responseText});
                }
            };
            var today = new Date().toISOString().split('T')[0];
            xhr.send('start=' + today + '&end=' + today);
            """
            
            driver.set_script_timeout(30)
            
            error_streak = 0
            
            # Inner scanning loop (stays on the page and scans every 5 seconds)
            while error_streak < 5:
                try:
                    result = driver.execute_async_script(fetch_script)
                    status = result.get('status')
                    response_text = result.get('text')
                    
                    if status == 200:
                        try:
                            json_data = json.loads(response_text)
                        except ValueError:
                            # If it returns HTML (like empty inbox), ignore gracefully
                            if "No SMS found" in response_text or "sms-empty" in response_text:
                                if is_first_run:
                                    print("📭 Inbox is currently empty. Waiting for new OTPs...")
                                    is_first_run = False
                                error_streak = 0
                                time.sleep(6)
                                continue
                            else:
                                print(f"🚨 Received unexpected HTML. Refreshing page...")
                                driver.refresh()
                                time.sleep(5)
                                error_streak += 1
                                continue
                                
                        sms_list = json_data.get('data', [])
                        
                        if is_first_run:
                            print(f"📥 Found {len(sms_list)} old OTPs in inbox. Forwarding them now...")
                            is_first_run = False

                        for sms in reversed(sms_list):
                            msg_id = str(sms.get('id', ''))
                            
                            service_raw = safe_text(sms.get('originator', sms.get('sender', 'Unknown')))
                            term_data = sms.get('termination', {})
                            raw_number = str(sms.get('number', sms.get('receiver', term_data.get('test_number', 'Unknown'))))
                            full_text = safe_text(sms.get('messagedata', sms.get('message', 'No Text')))
                            
                            msg_signature = f"{raw_number}_{service_raw}_{full_text}"
                            
                            if msg_id and msg_id not in seen_messages and msg_signature not in seen_signatures:
                                
                                if len(seen_signatures) > 1000:
                                    seen_signatures.clear()
                                    seen_messages.clear()
                                    
                                seen_messages.add(msg_id)
                                seen_signatures.add(msg_signature)
                                
                                country_info, exact_range = get_country_and_exact_range(raw_number, "")
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
                                    # ⚠️ SIlent Message (disable_notification=True)
                                    bot.send_message(GROUP_ID, msg_body, parse_mode="HTML", reply_markup=markup, disable_notification=True)
                                    print(f"✅ PAID OTP Sent >> {service_title} | Number: {exact_range}")
                                    time.sleep(2.5) 
                                except Exception as e:
                                    print(f"❌ Telegram Error: {e}")
                                    
                        error_streak = 0 # Reset error count if successful
                        
                    elif status in [401, 403, 419]:
                        print(f"🚨 Session Expired (Code {status}). Breaking loop to re-login...")
                        break 
                    else:
                        error_streak += 1
                        print(f"⚠️ API Error {status}. Retrying...")
                        
                except Exception as e:
                    print(f"⚠️ Script Execution Error: {e}")
                    error_streak += 1
                    
                time.sleep(5) # ⚠️ প্রতি ৫ সেকেন্ড পরপর "Get SMS" বাটনের কাজ করবে
                
            print("🔄 Browser Session lost or timed out. Restarting the whole process...")
            driver.quit()
            
        except Exception as e:
            print(f"🔥 Critical System Error! Self-healing in 10s... Details: {e}")
            if driver:
                try: driver.quit()
                except: pass
            time.sleep(10)

if __name__ == "__main__":
    print("🤖 Paid SMS Bot is turning on (Video Logic Applied!)...")
    threading.Thread(target=run_smart_bot, daemon=True).start()
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
        except Exception:
            time.sleep(3)
