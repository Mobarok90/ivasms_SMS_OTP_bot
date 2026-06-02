import os
import time
import json
import re
import threading
import html
import urllib.parse
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

# আপনার দেওয়া পেইড ইনবক্সের API
API_URL = "https://www.ivasms.com/portal/sms/received/getsms"

# ==========================================
# 🎯 SERVICE FILTERS & LOGOS
# ==========================================
SERVICE_LOGOS = {
    "WHATSAPP": "🟢 WhatsApp", "FACEBOOK": "📘 Facebook", "TELEGRAM": "✈️ Telegram",
    "TIKTOK": "🎵 TikTok", "GOOGLE": "🔴 Google"
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

def get_country_and_exact_range(number, range_text):
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
# 🌐 STEP 1: AUTO-LOGIN & STEAL COOKIE
# ==========================================
def get_fresh_cookies():
    print("🚀 Launching invisible Browser to login to Paid Account...")
    driver = None
    try:
        driver = Driver(uc=True, headless=False)
        driver.set_page_load_timeout(60)
        
        print("🔐 Navigating to iVASMS login...")
        try: driver.get("https://www.ivasms.com/login")
        except: pass
        
        try: driver.uc_gui_click_captcha(); time.sleep(2)
        except: pass
        
        print("⏳ Waiting for Email Field...")
        driver.wait_for_element('input[name="email"]', timeout=30)
        
        print("✅ CF bypassed! Entering credentials...")
        driver.type('input[name="email"]', EMAIL)
        driver.type('input[name="password"]', PASSWORD)
        
        print("⏳ Waiting 8 seconds for Turnstile to auto-resolve...")
        time.sleep(8)
        
        print("🤖 Attempting to click Turnstile just in case...")
        try: driver.uc_gui_click_captcha(); time.sleep(3)
        except: pass
        
        print("🖱️ Clicking Login Submit Button...")
        try: driver.uc_click('button[type="submit"]')
        except: driver.click('button[type="submit"]')
            
        print("⏳ Waiting to reach the dashboard...")
        timeout_counter = 40
        while "login" in driver.current_url and timeout_counter > 0:
            time.sleep(1)
            timeout_counter -= 1
            
        if "login" in driver.current_url:
            print("❌ Login Failed! Cloudflare blocked or wrong password.")
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
        
        print("🍪 Fresh Authenticated Cookies Grabbed!")
        driver.quit() 
        return cookie_dict, user_agent, xsrf_token
        
    except Exception as e:
        print(f"❌ Failed to grab cookies: {e}")
        if driver:
            try: driver.quit()
            except: pass
        return None, None, None

# ==========================================
# 📡 STEP 2: 24/7 INBOX SCANNING
# ==========================================
def monitor_ranges():
    global is_first_run, seen_messages, seen_signatures
    
    while True:
        try:
            cookie_dict, user_agent, xsrf_token = get_fresh_cookies()
            
            if not cookie_dict:
                print("🔄 Auto-Login failed. Retrying in 30 seconds...")
                time.sleep(30)
                continue
                
            print("⚡ Scanning Paid Inbox for new OTPs...")
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
            
            # ডেট ফিল্টার (আজকের ডেট পাঠানো হচ্ছে)
            today_str = time.strftime("%Y-%m-%d")
            payload = {
                "draw": "1",
                "start": "0",
                "length": "100",
                "start_date": today_str,
                "end_date": today_str
            }
            
            error_count = 0
            
            while error_count < 5:
                try:
                    response = scraper.post(API_URL, headers=headers, data=payload, timeout=20)
                    
                    if response.status_code == 200:
                        
                        # ⚠️ SMART EMPTY INBOX DETECTOR
                        if "No SMS found" in response.text or "sms-empty" in response.text:
                            if is_first_run:
                                print("📭 Inbox is currently empty. Waiting peacefully for new OTPs...")
                                is_first_run = False
                            error_count = 0 # কোনো এরর ধরবে না
                            time.sleep(6) # ৬ সেকেন্ড পর আবার চেক করবে
                            continue
                            
                        try:
                            json_data = response.json()
                        except ValueError:
                            print(f"🚨 API returned unexpected HTML. Snippet: {response.text[:150]}")
                            break 
                            
                        sms_list = json_data.get('data', [])
                        
                        if is_first_run:
                            print(f"📥 Found {len(sms_list)} OTPs in inbox. Forwarding them to the group...")
                            is_first_run = False

                        for sms in reversed(sms_list):
                            msg_id = str(sms.get('id', ''))
                            
                            service_raw = safe_text(sms.get('originator', 'Unknown'))
                            term_data = sms.get('termination', {})
                            raw_number = str(term_data.get('test_number', sms.get('test_number', 'Unknown')))
                            full_text = safe_text(sms.get('messagedata', 'No Text'))
                            
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
                                    bot.send_message(GROUP_ID, msg_body, parse_mode="HTML", reply_markup=markup, disable_notification=False)
                                    print(f"✅ PAID OTP Sent >> {service_title} | Number: {exact_range}")
                                    time.sleep(2.5) 
                                except Exception as e:
                                    if "Too Many Requests" in str(e):
                                        print("⏳ Telegram Anti-Spam! Pausing for 15 seconds...")
                                        time.sleep(15)
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
                    
                time.sleep(6) # ইনবক্স চেক করার গ্যাপ
                
            print("🔄 Connection lost or Session expired. Going back to Steal Cookies...")
            
        except Exception as e:
            print(f"🔥 Critical System Error! Self-healing in 10s... Details: {e}")
            time.sleep(10)

if __name__ == "__main__":
    print("🤖 Paid SMS Bot is turning on with Smart Empty Inbox Detector...")
    threading.Thread(target=monitor_ranges, daemon=True).start()
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
        except Exception:
            time.sleep(3)
