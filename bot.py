import os
import time
import json
import re
import threading
import html
import urllib.parse
import telebot
import cloudscraper
from seleniumbase import Driver

# ==========================================
# ⚙️ ADVANCED CONFIGURATION (From Secrets)
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

GROUP_ID = "-1003949942852"
USER_BOT_USERNAME = "YourOTPBot"

API_URL = "https://www.ivasms.com/portal/sms/test/sms?draw=1&columns%5B0%5D%5Bdata%5D=range&columns%5B0%5D%5Borderable%5D=false&columns%5B1%5D%5Bdata%5D=termination.test_number&columns%5B1%5D%5Bsearchable%5D=false&columns%5B1%5D%5Borderable%5D=false&columns%5B2%5D%5Bdata%5D=originator&columns%5B2%5D%5Borderable%5D=false&columns%5B3%5D%5Bdata%5D=messagedata&columns%5B3%5D%5Borderable%5D=false&columns%5B4%5D%5Bdata%5D=senttime&columns%5B4%5D%5Bsearchable%5D=false&columns%5B4%5D%5Borderable%5D=false&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=asc&start=0&length=25&search%5Bvalue%5D=&_=1778741963472"

# ==========================================
# 🎯 SERVICE FILTERS & LOGOS
# ==========================================
SERVICE_LOGOS = {
    "WHATSAPP": "🟢 WhatsApp", "FACEBOOK": "📘 Facebook", "TELEGRAM": "✈️ Telegram",
    "TIKTOK": "🎵 TikTok", "GOOGLE": "🔴 Google"
}
ALLOWED_SERVICES = list(SERVICE_LOGOS.keys())
BLOCKED_SERVICES = ["TIKTOKADS"] # TikTokAds ব্লক করা হলো

# ==========================================
# 🌍 COMPLETE COUNTRY DICTIONARY (250+ Countries)
# ==========================================
COUNTRY_DICT = {
    "1": ("USA/Canada", "🇺🇸/🇨🇦"), "7": ("Russia", "🇷🇺"), "20": ("Egypt", "🇪🇬"), 
    "27": ("South Africa", "🇿🇦"), "30": ("Greece", "🇬🇷"), "31": ("Netherlands", "🇳🇱"), 
    "32": ("Belgium", "🇧🇪"), "33": ("France", "🇫🇷"), "34": ("Spain", "🇪🇸"), 
    "36": ("Hungary", "🇭🇺"), "39": ("Italy", "🇮🇹"), "40": ("Romania", "🇷🇴"), 
    "41": ("Switzerland", "🇨🇭"), "43": ("Austria", "🇦🇹"), "44": ("UK", "🇬🇧"), 
    "45": ("Denmark", "🇩🇰"), "46": ("Sweden", "🇸🇪"), "47": ("Norway", "🇳🇴"), 
    "48": ("Poland", "🇵🇱"), "49": ("Germany", "🇩🇪"), "51": ("Peru", "🇵🇪"), 
    "52": ("Mexico", "🇲🇽"), "53": ("Cuba", "🇨🇺"), "54": ("Argentina", "🇦🇷"), 
    "55": ("Brazil", "🇧🇷"), "56": ("Chile", "🇨🇱"), "57": ("Colombia", "🇨🇴"), 
    "58": ("Venezuela", "🇻🇪"), "60": ("Malaysia", "🇲🇾"), "61": ("Australia", "🇦🇺"), 
    "62": ("Indonesia", "🇮🇩"), "63": ("Philippines", "🇵🇭"), "64": ("New Zealand", "🇳🇿"), 
    "65": ("Singapore", "🇸🇬"), "66": ("Thailand", "🇹🇭"), "81": ("Japan", "🇯🇵"), 
    "82": ("South Korea", "🇰🇷"), "84": ("Vietnam", "🇻🇳"), "86": ("China", "🇨🇳"), 
    "90": ("Turkey", "🇹🇷"), "91": ("India", "🇮🇳"), "92": ("Pakistan", "🇵🇰"), 
    "93": ("Afghanistan", "🇦🇫"), "94": ("Sri Lanka", "🇱🇰"), "95": ("Myanmar", "🇲🇲"), 
    "98": ("Iran", "🇮🇷"), "211": ("South Sudan", "🇸🇸"), "212": ("Morocco", "🇲🇦"), 
    "213": ("Algeria", "🇩🇿"), "216": ("Tunisia", "🇹🇳"), "218": ("Libya", "🇱🇾"), 
    "220": ("Gambia", "🇬🇲"), "221": ("Senegal", "🇸🇳"), "222": ("Mauritania", "🇲🇷"), 
    "223": ("Mali", "🇲🇱"), "224": ("Guinea", "🇬🇳"), "225": ("Ivory Coast", "🇨🇮"), 
    "226": ("Burkina Faso", "🇧🇫"), "227": ("Niger", "🇳🇪"), "228": ("Togo", "🇹🇬"), 
    "229": ("Benin", "🇧🇯"), "230": ("Mauritius", "🇲🇺"), "231": ("Liberia", "🇱🇷"), 
    "232": ("Sierra Leone", "🇸🇱"), "233": ("Ghana", "🇬🇭"), "234": ("Nigeria", "🇳🇬"), 
    "235": ("Chad", "🇹🇩"), "236": ("CAR", "🇨🇫"), "237": ("Cameroon", "🇨🇲"), 
    "238": ("Cape Verde", "🇨🇻"), "239": ("Sao Tome", "🇸🇹"), "240": ("Equatorial Guinea", "🇬🇶"), 
    "241": ("Gabon", "🇬🇦"), "242": ("Congo", "🇨🇬"), "243": ("DR Congo", "🇨🇩"), 
    "244": ("Angola", "🇦🇴"), "245": ("Guinea-Bissau", "🇬🇼"), "246": ("Diego Garcia", "🇮🇴"), 
    "248": ("Seychelles", "🇸🇨"), "249": ("Sudan", "🇸🇩"), "250": ("Rwanda", "🇷🇼"), 
    "251": ("Ethiopia", "🇪🇹"), "252": ("Somalia", "🇸🇴"), "253": ("Djibouti", "🇩🇯"), 
    "254": ("Kenya", "🇰🇪"), "255": ("Tanzania", "🇹🇿"), "256": ("Uganda", "🇺🇬"), 
    "257": ("Burundi", "🇧🇮"), "258": ("Mozambique", "🇲🇿"), "260": ("Zambia", "🇿🇲"), 
    "261": ("Madagascar", "🇲🇬"), "262": ("Reunion", "🇷🇪"), "263": ("Zimbabwe", "🇿🇼"), 
    "264": ("Namibia", "🇳🇦"), "265": ("Malawi", "🇲🇼"), "266": ("Lesotho", "🇱🇸"), 
    "267": ("Botswana", "🇧🇼"), "268": ("Eswatini", "🇸🇿"), "269": ("Comoros", "🇰🇲"), 
    "290": ("St Helena", "🇸🇭"), "291": ("Eritrea", "🇪🇷"), "297": ("Aruba", "🇦🇼"),
    "298": ("Faroe Islands", "🇫🇴"), "299": ("Greenland", "🇬🇱"), "350": ("Gibraltar", "🇬🇮"),
    "351": ("Portugal", "🇵🇹"), "352": ("Luxembourg", "🇱🇺"), "353": ("Ireland", "🇮🇪"), 
    "354": ("Iceland", "🇮🇸"), "355": ("Albania", "🇦🇱"), "356": ("Malta", "🇲🇹"), 
    "357": ("Cyprus", "🇨🇾"), "358": ("Finland", "🇫🇮"), "359": ("Bulgaria", "🇧🇬"), 
    "370": ("Lithuania", "🇱🇹"), "371": ("Latvia", "🇱🇻"), "372": ("Estonia", "🇪🇪"), 
    "373": ("Moldova", "🇲🇩"), "374": ("Armenia", "🇦🇲"), "375": ("Belarus", "🇧🇾"), 
    "376": ("Andorra", "🇦🇩"), "377": ("Monaco", "🇲🇨"), "378": ("San Marino", "🇸🇲"),
    "380": ("Ukraine", "🇺🇦"), "381": ("Serbia", "🇷🇸"), "382": ("Montenegro", "🇲🇪"),
    "383": ("Kosovo", "🇽🇰"), "385": ("Croatia", "🇭🇷"), "386": ("Slovenia", "🇸🇮"),
    "387": ("Bosnia", "🇧🇦"), "389": ("North Macedonia", "🇲🇰"), "420": ("Czechia", "🇨🇿"), 
    "421": ("Slovakia", "🇸🇰"), "423": ("Liechtenstein", "🇱🇮"), "500": ("Falkland", "🇫🇰"),
    "501": ("Belize", "🇧🇿"), "502": ("Guatemala", "🇬🇹"), "503": ("El Salvador", "🇸🇻"), 
    "504": ("Honduras", "🇭🇳"), "505": ("Nicaragua", "🇳🇮"), "506": ("Costa Rica", "🇨🇷"), 
    "507": ("Panama", "🇵🇦"), "509": ("Haiti", "🇭🇹"), "590": ("Guadeloupe", "🇬🇵"),
    "591": ("Bolivia", "🇧🇴"), "592": ("Guyana", "🇬🇾"), "593": ("Ecuador", "🇪🇨"), 
    "594": ("French Guiana", "🇬🇫"), "595": ("Paraguay", "🇵🇾"), "596": ("Martinique", "🇲🇶"),
    "597": ("Suriname", "🇸🇷"), "598": ("Uruguay", "🇺🇾"), "599": ("Curacao", "🇨🇼"),
    "852": ("Hong Kong", "🇭🇰"), "853": ("Macau", "🇲🇴"), "855": ("Cambodia", "🇰🇭"), 
    "856": ("Laos", "🇱🇦"), "880": ("Bangladesh", "🇧🇩"), "886": ("Taiwan", "🇹🇼"),
    "960": ("Maldives", "🇲🇻"), "961": ("Lebanon", "🇱🇧"), "962": ("Jordan", "🇯🇴"), 
    "963": ("Syria", "🇸🇾"), "964": ("Iraq", "🇮🇶"), "965": ("Kuwait", "🇰🇼"), 
    "966": ("Saudi Arabia", "🇸🇦"), "967": ("Yemen", "🇾🇪"), "968": ("Oman", "🇴🇲"), 
    "970": ("Palestine", "🇵🇸"), "971": ("UAE", "🇦🇪"), "972": ("Israel", "🇮🇱"), 
    "973": ("Bahrain", "🇧🇭"), "974": ("Qatar", "🇶🇦"), "975": ("Bhutan", "🇧🇹"),
    "976": ("Mongolia", "🇲🇳"), "977": ("Nepal", "🇳🇵"), "992": ("Tajikistan", "🇹🇯"),
    "993": ("Turkmenistan", "🇹🇲"), "994": ("Azerbaijan", "🇦🇿"), "995": ("Georgia", "🇬🇪"),
    "996": ("Kyrgyzstan", "🇰🇬"), "998": ("Uzbekistan", "🇺🇿")
}

bot = telebot.TeleBot(BOT_TOKEN)
try:
    bot.remove_webhook()
except Exception:
    pass

seen_messages = set()
is_first_run = True

# 🧠 SMART AI MEMORY (For High Active Ranges)
range_activity_tracker = {}
TIME_WINDOW = 900 # 15 minutes window
MIN_OTP_THRESHOLD = 3 # Minimum 3 OTPs required to post
HIGH_ACTIVE_THRESHOLD = 5 # 5+ OTPs marks it as HIGHLY ACTIVE

@bot.message_handler(commands=['setbot'])
def set_bot_username(message):
    global USER_BOT_USERNAME
    try:
        if str(message.chat.id) == GROUP_ID:
            text = message.text.split()
            if len(text) > 1:
                USER_BOT_USERNAME = text[1].replace('https://t.me/', '').replace('@', '')
                bot.reply_to(message, f"✅ <b>Bot Link Updated:</b> @{USER_BOT_USERNAME}", parse_mode="HTML")
    except Exception:
        pass

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
            if country_name.lower() != "active": 
                country_info = f"{country_name} 🏳️"
                
    return country_info, exact_range

def get_clean_service(text):
    if not text: 
        return "Unknown"
    text = re.split(r'<script|function|\$\(', str(text), flags=re.IGNORECASE)[0]
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'[^a-zA-Z0-9\s\-]', '', text).strip().upper()

def safe_text(text):
    if not text: 
        return "Unknown"
    text = str(text)
    text = re.split(r'<script|function|\$\(', text, flags=re.IGNORECASE)[0]
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = text.replace('<', ' ').replace('>', ' ').replace('&', 'and')
    return re.sub(r'\s+', ' ', text).strip()

# ==========================================
# 🌐 STEP 1: AUTO-LOGIN & STEAL COOKIE & XSRF
# ==========================================
def get_fresh_cookies():
    print("🚀 Launching invisible Browser to get fresh Cookies...")
    driver = None
    try:
        driver = Driver(uc=True, headless=False)
        driver.set_page_load_timeout(45)
        
        print("🔐 Navigating to iVASMS login...")
        try:
            driver.get("https://www.ivasms.com/login")
        except Exception:
            pass
        
        try:
            driver.uc_gui_click_captcha()
            time.sleep(2)
        except Exception:
            pass
        
        print("⏳ Waiting for Email Field...")
        driver.wait_for_element('input[name="email"]', timeout=30)
        
        print("✅ CF bypassed! Entering credentials...")
        driver.type('input[name="email"]', EMAIL)
        driver.type('input[name="password"]', PASSWORD)
        
        print("⏳ Waiting 7 seconds for embedded Turnstile Captcha to auto-resolve...")
        time.sleep(7)
        
        print("🤖 Attempting to click Turnstile just in case...")
        try:
            driver.uc_gui_click_captcha()
            time.sleep(3)
        except Exception:
            pass
        
        print("🖱️ Clicking Login Submit Button...")
        try:
            driver.uc_click('button[type="submit"]')
        except Exception:
            driver.click('button[type="submit"]')
            
        print("⏳ Waiting to reach the dashboard...")
        timeout_counter = 30
        while "login" in driver.current_url and timeout_counter > 0:
            time.sleep(1)
            timeout_counter -= 1
            
        if "login" in driver.current_url:
            print("❌ Still on login page! Check Email/Password or CF blocked it.")
            driver.quit()
            return None, None, None
            
        print("✅ Dashboard Reached! Letting cookies settle for 5 seconds...")
        time.sleep(5) 
        
        cookies = driver.get_cookies()
        user_agent = driver.execute_script("return navigator.userAgent;")
        
        cookie_dict = {}
        xsrf_token = ""
        for c in cookies:
            cookie_dict[c['name']] = c['value']
            if c['name'] == 'XSRF-TOKEN':
                xsrf_token = urllib.parse.unquote(c['value'])
        
        print("🍪 Fresh Authenticated Cookies & XSRF Token Successfully Grabbed!")
        driver.quit() 
        return cookie_dict, user_agent, xsrf_token
        
    except Exception as e:
        print(f"❌ Failed to grab cookies: {e}")
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        return None, None, None

# ==========================================
# 📡 STEP 2: 24/7 FAST SCRAPING & AI TRACKING
# ==========================================
def monitor_ranges():
    global is_first_run, range_activity_tracker
    
    while True:
        cookie_dict, user_agent, xsrf_token = get_fresh_cookies()
        
        if not cookie_dict:
            print("🔄 Auto-Login failed. Retrying in 30 seconds...")
            time.sleep(30)
            continue
            
        print("⚡ Handing over cookies to Cloudscraper for 24/7 fast scanning...")
        scraper = cloudscraper.create_scraper()
        scraper.cookies.update(cookie_dict)
        
        headers = {
            "User-Agent": user_agent,
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest", 
            "X-XSRF-TOKEN": xsrf_token,
            "Origin": "https://www.ivasms.com",
            "Referer": "https://www.ivasms.com/portal/sms/test/sms"
        }
        
        error_count = 0
        
        while error_count < 5:
            try:
                response = scraper.get(API_URL, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    json_data = response.json()
                    sms_list = json_data.get('data', [])
                    
                    if is_first_run:
                        print(f"📥 Found {len(sms_list)} old ranges. Pre-loading Active Tracker silently...")
                        for sms in sms_list:
                            seen_messages.add(str(sms.get('id', '')))
                            term_data = sms.get('termination', {})
                            raw_number = str(term_data.get('test_number', sms.get('test_number', 'Unknown')))
                            _, exact_range = get_country_and_exact_range(raw_number, "")
                            range_activity_tracker[exact_range] = range_activity_tracker.get(exact_range, 0) + 1
                            
                        is_first_run = False
                        time.sleep(5)
                        continue

                    current_time = time.time()

                    for sms in reversed(sms_list):
                        msg_id = str(sms.get('id', ''))
                        
                        if msg_id and msg_id not in seen_messages:
                            service_raw = safe_text(sms.get('originator', 'Unknown')).upper()
                            
                            # 🚫 Block unwanted services like TIKTOKADS
                            if any(blocked in service_raw for blocked in BLOCKED_SERVICES):
                                seen_messages.add(msg_id)
                                continue

                            # ⚠️ Ensure only Allowed Services pass
                            if not any(allowed in service_raw for allowed in ALLOWED_SERVICES):
                                seen_messages.add(msg_id)
                                continue 
                            
                            term_data = sms.get('termination', {})
                            raw_number = str(term_data.get('test_number', sms.get('test_number', 'Unknown')))
                            range_count_text = safe_text(sms.get('range', 'Active')) 
                            
                            country_info, exact_range = get_country_and_exact_range(raw_number, range_count_text)
                            
                            # 🧠 15-MINUTE AI SLIDING WINDOW MEMORY 
                            if exact_range not in range_activity_tracker:
                                range_activity_tracker[exact_range] = []
                            
                            range_activity_tracker[exact_range].append(current_time)
                            range_activity_tracker[exact_range] = [t for t in range_activity_tracker[exact_range] if current_time - t <= TIME_WINDOW]
                            
                            recent_otp_count = len(range_activity_tracker[exact_range])
                            
                            # If not highly active, monitor silently
                            if recent_otp_count < MIN_OTP_THRESHOLD:
                                seen_messages.add(msg_id)
                                print(f"👀 Monitoring Range >> {exact_range} (Hit {recent_otp_count}/{MIN_OTP_THRESHOLD} for Active)")
                                continue
                            
                            if recent_otp_count >= HIGH_ACTIVE_THRESHOLD:
                                title_header = "🔥 <b>HIGHLY ACTIVE RANGE</b> 🔥"
                            else:
                                title_header = "✅ <b>ACTIVE NEW RANGE</b>"
                                
                            service_display = SERVICE_LOGOS.get(service_raw, f"🌐 {service_raw}")
                            full_text = safe_text(sms.get('messagedata', 'No Text'))

                            msg_body = (
                                f"{title_header}\n"
                                f"━━━━━━━━━━━━━━━━━━━\n"
                                f"🌍 <b>Country:</b> {country_info}\n"
                                f"🎯 <b>Range:</b> {exact_range}\n"
                                f"⚙️ <b>Service:</b> {service_display}\n"
                                f"📊 <b>Recent OTPs:</b> {recent_otp_count} (Last 15m)\n"
                                f"━━━━━━━━━━━━━━━━━━━\n"
                                f"💬 <b>SMS Code:</b>\n"
                                f"<i>{full_text}</i>"
                            )
                            
                            markup = telebot.types.InlineKeyboardMarkup()
                            try:
                                copy_action = telebot.types.CopyTextButton(text=exact_range)
                                btn_copy = telebot.types.InlineKeyboardButton("📋 RANGE", copy_text=copy_action)
                            except AttributeError:
                                btn_copy = telebot.types.InlineKeyboardButton("📋 RANGE", switch_inline_query_current_chat=exact_range)
                                
                            btn_bot = telebot.types.InlineKeyboardButton("🤖 BOTLINK", url=f"https://t.me/{USER_BOT_USERNAME}")
                            markup.row(btn_copy, btn_bot)
                            
                            try:
                                bot.send_message(GROUP_ID, msg_body, parse_mode="HTML", reply_markup=markup)
                                seen_messages.add(msg_id)
                                print(f"✅ OTP Sent (Hits: {recent_otp_count}) >> {service_raw} | Range: {exact_range}")
                                time.sleep(3.5) 
                            except Exception as e:
                                if "Too Many Requests" in str(e):
                                    retry_match = re.search(r'retry after (\d+)', str(e))
                                    wait_time = int(retry_match.group(1)) if retry_match else 10
                                    print(f"⏳ Telegram Anti-Spam (429)! Pausing for {wait_time} seconds...")
                                    time.sleep(wait_time + 1)
                                else:
                                    print(f"❌ Telegram Error: {e}")
                                
                    error_count = 0 
                    
                elif response.status_code in [401, 403, 419]:
                    print(f"🚨 Session Expired (Code {response.status_code}). Restarting auto-login...")
                    break 
                else:
                    error_count += 1
                        
            except Exception as e:
                print(f"⚠️ Fetch Error: {e}")
                error_count += 1
                
            time.sleep(10)
            
        print("🔄 Connection lost or Session expired. Going back to Steal Cookies...")

if __name__ == "__main__":
    print("🤖 Master Hybrid Bot is turning on with AI Active Range Tracker...")
    threading.Thread(target=monitor_ranges, daemon=True).start()
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
        except Exception:
            time.sleep(3)
