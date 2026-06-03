import os
import time
import json
import re
import threading
import html
import telebot
import logging
import traceback
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
    "TIKTOK": "🎵 TikTok", "GOOGLE": "🔴 Google"
}
ALLOWED_SERVICES = list(SERVICE_LOGOS.keys())
BLOCKED_SERVICES = ["TIKTOKADS"] 

# ==========================================
# 🌍 SUPER MASSIVE COUNTRY DICTIONARY (270+ Codes)
# ==========================================
COUNTRY_DICT = {
    "1": ("USA/Canada", "🇺🇸/🇨🇦"), "7": ("Russia", "🇷🇺"), "20": ("Egypt", "🇪🇬"), 
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
# 🤖 AI CORE: 100% HUMAN SIMULATOR (BROWSER ONLY)
# ==========================================
def run_smart_bot():
    global is_first_run, seen_messages, seen_signatures
    driver = None
    
    while True:
        try:
            print("🚀 Booting up invisible AI Browser (Human Mode)...")
            driver = Driver(uc=True, headless=False)
            driver.set_page_load_timeout(60)
            
            # ১. লগইন প্রসেস
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
                print("❌ Login Failed! Restarting process...")
                driver.quit()
                time.sleep(10)
                continue
                
            print("✅ Login Successful! Like a human, moving to 'My SMS' Page...")
            
            # ২. মানুষের মতো ইনবক্স পেজে যাওয়া
            driver.get("https://www.ivasms.com/portal/sms/received")
            time.sleep(5) 
            
            print("📡 Starting 24/7 OTP Scanning Loop inside the Browser...")
            
            # ৩. ব্রাউজারের ভেতর থেকে সিকিউর রিকোয়েস্ট পাঠানো (No API Error)
            fetch_script = """
            var callback = arguments[arguments.length - 1];
            var csrf = document.querySelector('meta[name="csrf-token"]');
            if (!csrf) { callback({status: 500, text: "No CSRF"}); return; }
            
            var xhr = new XMLHttpRequest();
            xhr.open('POST', 'https://www.ivasms.com/portal/sms/received/getsms', true);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            xhr.setRequestHeader('X-CSRF-TOKEN', csrf.getAttribute('content'));
            
            xhr.onreadystatechange = function() {
                if (xhr.readyState == 4) {
                    callback({status: xhr.status, text: xhr.responseText});
                }
            };
            
            var today = new Date().toISOString().split('T')[0];
            xhr.send('_token=' + encodeURIComponent(csrf.getAttribute('content')) + '&start=' + today + '&end=' + today);
            """
            
            driver.set_script_timeout(30)
            error_streak = 0
            
            # ৪. স্ক্যানিং লুপ (ব্রাউজারের ভেতরেই ঘুরবে)
            while error_streak < 5:
                try:
                    result = driver.execute_async_script(fetch_script)
                    status = result.get('status')
                    response_text = result.get('text')
                    
                    if status == 200:
                        try:
                            json_data = json.loads(response_text)
                        except ValueError:
                            if "No SMS found" in response_text or "sms-empty" in response_text:
                                if is_first_run:
                                    print("📭 Inbox is currently empty. Waiting for new OTPs...")
                                    is_first_run = False
                                error_streak = 0
                                time.sleep(6)
                                continue
                            else:
                                print(f"🚨 Received unexpected HTML. Refreshing the inbox page...")
                                driver.refresh()
                                time.sleep(5)
                                error_streak += 1
                                continue
                                
                        sms_list = json_data.get('data', [])
                        
                        if is_first_run:
                            print(f"📥 Found {len(sms_list)} old OTPs. Forwarding them now...")
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
                                    # ⚠️ Muted Message for Paid Inbox
                                    bot.send_message(GROUP_ID, msg_body, parse_mode="HTML", reply_markup=markup, disable_notification=True)
                                    print(f"✅ PAID OTP Sent >> {service_title} | Number: {exact_range}")
                                    time.sleep(2.5) 
                                except Exception as e:
                                    print(f"❌ Telegram Error: {e}")
                                    
                        error_streak = 0 
                        
                    elif status in [401, 403, 419]:
                        print(f"🚨 Session Expired (Code {status}). Breaking loop to re-login...")
                        break 
                    else:
                        error_streak += 1
                        print(f"⚠️ API Error {status}. Retrying...")
                        
                except Exception as e:
                    print(f"⚠️ Script Execution Error: {e}")
                    error_streak += 1
                    
                time.sleep(5) # ⚠️ প্রতি ৫ সেকেন্ড পরপর ইনবক্স স্ক্যান করবে
                
            print("🔄 Browser Session lost or timed out. Restarting the whole process...")
            driver.quit()
            
        except Exception as e:
            print(f"🔥 Critical System Error! Self-healing in 10s... Details: {e}")
            if driver:
                try: driver.quit()
                except: pass
            time.sleep(10)

if __name__ == "__main__":
    print("🤖 Paid SMS Bot is turning on (100% Human Simulator Applied!)...")
    threading.Thread(target=run_smart_bot, daemon=True).start()
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
        except Exception:
            time.sleep(3)
