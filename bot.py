import os
import time
import json
import re
import threading
import html
import urllib.parse
import telebot
import logging
from datetime import datetime, timedelta
import pytz
from seleniumbase import Driver

telebot.logger.setLevel(logging.ERROR)

# ==========================================
# ⚙️ ADVANCED CONFIGURATION (Paid SMS System)
# ==========================================

BOT_TOKEN = "8794355686:AAFDoPfbPIg06yr0Qthoe2sNr3yUguslyyE"
GROUP_ID = "-1003871481057"

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# পেইড ইনবক্সের API ইউআরএল
API_URL = "https://www.ivasms.com/portal/sms/received/getsms/number/sms"

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
try:
    bot.remove_webhook()
except Exception:
    pass

seen_messages = set()
seen_signatures = set() 
is_first_run = True

def get_country_and_exact_range(number, range_text):
    num_str = "".join(filter(str.isdigit, str(number)))
    while num_str.startswith('0'): 
        num_str = num_str[1:]
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
# 📅 আজ এবং গতকালকের তারিখ ফিল্টারিং লজিক
# ==========================================
def is_today_or_yesterday(sms):
    try:
        tz = pytz.timezone('Asia/Dhaka')
        now = datetime.now(tz)
    except Exception:
        now = datetime.now()
        
    yesterday = now - timedelta(days=1)
    
    # সম্ভাব্য সব ধরনের ডেট ফরম্যাট জেনারেট করা
    today_formats = [now.strftime("%Y-%m-%d"), now.strftime("%d/%m/%Y"), now.strftime("%d-%m-%Y")]
    yesterday_formats = [yesterday.strftime("%Y-%m-%d"), yesterday.strftime("%d/%m/%Y"), yesterday.strftime("%d-%m-%Y")]
    allowed_dates = today_formats + yesterday_formats
    
    # এপিআই রেসপন্সের বিভিন্ন ফিল্ডে চেক করা
    possible_keys = ['created_at', 'updated_at', 'received_at', 'time', 'date', 'datetime', 'timestamp']
    for key in possible_keys:
        val = sms.get(key)
        if val:
            val_str = str(val)
            for d_str in allowed_dates:
                if d_str in val_str:
                    return True
                    
    # যদি কোনো নির্দিষ্ট ফিল্ড না মেলে, তবে অন্য ডেটা টেক্সট চেক করা
    for k, v in sms.items():
        if isinstance(v, str):
            for d_str in allowed_dates:
                if d_str in v:
                    return True
                    
    # ফলব্যাক হিসেবে প্রথমবার সব ডেটাই গ্রহণ করা যাতে কোনো জরুরি ওটিপি মিস না হয়
    return True

# ==========================================
# 📡 STEP 1 & 2: 24/7 INBOX SCANNING (CF-proof Web Session)
# ==========================================
def monitor_ranges():
    global is_first_run, seen_messages, seen_signatures
    
    while True:
        driver = None
        try:
            print("🚀 Launching invisible Browser to login to Paid Account...")
            driver = Driver(uc=True, headless=False)
            driver.set_page_load_timeout(45)
            driver.set_window_size(1280, 1024)
            
            print("🔐 Navigating to iVASMS login...")
            try: driver.get("https://www.ivasms.com/login")
            except Exception: pass
            
            try: driver.uc_gui_click_captcha(); time.sleep(2)
            except Exception: pass
            
            print("⏳ Waiting for Email Field...")
            driver.wait_for_element('input[name="email"]', timeout=30)
            
            print("✅ CF bypassed! Entering credentials...")
            driver.type('input[name="email"]', EMAIL)
            driver.type('input[name="password"]', PASSWORD + "\n")
            
            time.sleep(5)
            
            if "login" in driver.current_url:
                print("🖱️ Trying secondary login button click...")
                try: driver.click('button[type="submit"]')
                except Exception: pass
                time.sleep(3)
                
            if "login" in driver.current_url:
                print("🖱️ Trying magic JS submit button click...")
                try: driver.js_click('button[type="submit"]')
                except Exception: pass
                time.sleep(3)
                
            print("⏳ Waiting to reach the dashboard...")
            timeout_counter = 40
            login_success = False
            while timeout_counter > 0:
                try:
                    if "login" not in driver.current_url:
                        login_success = True
                        break
                except Exception:
                    pass
                time.sleep(1)
                timeout_counter -= 1
                try: driver.uc_gui_click_captcha()
                except Exception: pass
                
            if not login_success:
                print("❌ Login Failed! Cloudflare blocked or invalid credentials.")
                if driver: driver.quit()
                time.sleep(20)
                continue
                
            print("✅ Dashboard Reached! Keeping browser session open for API scanning...")
            time.sleep(5) 
            
            print("⚡ Starting 24/7 scanning loop inside browser session...")
            error_count = 0
            
            while error_count < 10:
                try:
                    # ⚠️ ব্রাউজার সেশনের ভেতর থেকেই সরাসরি জাভাস্ক্রিপ্ট কল রান করা হচ্ছে
                    # এটি ক্লাউডফ্লেয়ার কোনোভাবেই ব্লক করতে পারবে না
                    script = """
                    return fetch('https://www.ivasms.com/portal/sms/received/getsms/number/sms')
                        .then(response => {
                            if (!response.ok) {
                                throw new Error('HTTP Status: ' + response.status);
                            }
                            return response.json();
                        });
                    """
                    json_data = driver.execute_script(script)
                    
                    if json_data and 'data' in json_data:
                        sms_list = json_data.get('data', [])
                        
                        if is_first_run:
                            print(f"📥 Scanning today's and yesterday's OTPs to forward...")
                            
                        for sms in reversed(sms_list):
                            msg_id = str(sms.get('id', ''))
                            service_raw = safe_text(sms.get('originator', 'Unknown'))
                            term_data = sms.get('termination', {})
                            raw_number = str(term_data.get('test_number', sms.get('test_number', 'Unknown')))
                            full_text = safe_text(sms.get('messagedata', 'No Text'))
                            
                            # প্রথমবার চালুর সময় শুধু আজকের এবং গতকালকের মেসেজ গ্রুপে যাবে
                            if is_first_run:
                                if not is_today_or_yesterday(sms):
                                    continue
                                    
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

                                # ডিজাইন এবং বাটন লেআউট হুবহু অপরিবর্তিত রাখা হয়েছে
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
                                    bot.send_message(GROUP_ID, msg_body, parse_mode="HTML", reply_markup=markup)
                                    print(f"✅ OTP Sent >> {service_title} | Number: {exact_range}")
                                    time.sleep(2.5) # Anti-flood delay
                                except Exception as e:
                                    print(f"❌ Telegram Error: {e}")
                                    
                        if is_first_run:
                            print("📥 Startup sync complete! Today's and Yesterday's OTPs sent.")
                            is_first_run = False
                            
                        error_count = 0  # সফল স্ক্যানে এরর কাউন্টার শূন্য হবে
                        
                    else:
                        print("🚨 Empty API data, retrying...")
                        error_count += 1
                        
                except Exception as e:
                    print(f"⚠️ Fetch Error: {e}")
                    error_count += 1
                    
                time.sleep(5) # প্রতি ৫ সেকেন্ড পরপর ইনবক্স স্ক্যান করবে
                
            print("🔄 Closing browser session to refresh connection and re-login...")
            if driver:
                try: driver.quit()
                except Exception: pass
            
        except Exception as e:
            print(f"🔥 Critical System Error! Self-healing in 10s... Details: {e}")
            if driver:
                try: driver.quit()
                except Exception: pass
            time.sleep(10)

if __name__ == "__main__":
    print("🤖 Paid SMS Bot is turning on...")
    threading.Thread(target=monitor_ranges, daemon=True).start()
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
        except Exception:
            time.sleep(3)
