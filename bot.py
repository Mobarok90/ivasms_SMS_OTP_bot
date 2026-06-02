import os
import time
import json
import re
import random
import threading
import html
import urllib.parse
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
    "228": ("Togo", "🇹🇬"), "229": ("Benin", "🇧জয়"), "230": ("Mauritius", "🇲🇺"), 
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
# 📡 24/7 INBOX SCANNING (PAID SMS DIRECT ACCESSED)
# ==========================================
def monitor_ranges():
    global is_first_run, seen_messages, seen_signatures
    
    driver = None
    
    while True:
        try:
            # সেশনটি না থাকলে অথবা ড্রাইভার ক্র্যাশ করলে পুনরায় ব্রাউজার রান করে লগইন করবে
            if not driver:
                print("🚀 Launching invisible Browser to login to Paid Account...")
                driver = Driver(uc=True, headless=False)
                driver.set_page_load_timeout(60)
                
                print("🔐 Navigating to iVASMS login with reconnect...")
                try: 
                    driver.uc_open_with_reconnect("https://www.ivasms.com/login", reconnect_time=5)
                except Exception as e: 
                    print(f"⚠️ Navigation warning: {e}")
                
                print("⏳ Waiting for Email Field...")
                driver.wait_for_element('input[name="email"]', timeout=30)
                
                print("✅ CF bypassed! Entering credentials like a human...")
                driver.type('input[name="email"]', EMAIL)
                time.sleep(random.uniform(1.5, 2.5)) # মানুষের টাইপিং বিহেভিয়ার ডিলে
                
                driver.type('input[name="password"]', PASSWORD)
                time.sleep(random.uniform(1.2, 2.0))
                
                # 🚀 SMART FIX 1: পেজে আসলেই ক্লাউডফ্লেয়ার টার্নস্টাইল আছে কি না চেক করা
                turnstile_present = driver.execute_script("""
                    return !!(document.querySelector('.cf-turnstile') || 
                              document.querySelector('#cf-turnstile') || 
                              document.querySelector('iframe[src*="challenges.cloudflare.com"]'));
                """)
                
                if turnstile_present:
                    print("⏳ Cloudflare Turnstile detected. Waiting for auto-solve...")
                    turnstile_solved = False
                    for _ in range(25):
                        token = driver.execute_script("return document.querySelector('[name=cf-turnstile-response]') ? document.querySelector('[name=cf-turnstile-response]').value : ''")
                        if token and len(token) > 10:
                            print("✅ Cloudflare Turnstile Solved Successfully!")
                            turnstile_solved = True
                            break
                        time.sleep(1)
                    
                    if not turnstile_solved:
                        print("🤖 Attempting manual click on Turnstile...")
                        try: 
                            driver.uc_gui_click_captcha()
                            time.sleep(random.uniform(3.0, 4.0))
                        except: 
                            pass
                else:
                    print("🛡️ No Cloudflare Turnstile CAPTCHA detected on page. Proceeding...")
                
                time.sleep(random.uniform(1.0, 2.0)) # মানুষের সাবমিট ডিলে
                
                print("🖱️ Clicking Login Submit Button...")
                try: driver.uc_click('button[type="submit"]')
                except: driver.click('button[type="submit"]')
                    
                print("⏳ Waiting to reach the dashboard...")
                success = False
                for _ in range(25):
                    current_url = driver.current_url
                    if "/portal" in current_url and "login" not in current_url:
                        success = True
                        break
                    time.sleep(1)
                    
                if not success:
                    print(f"❌ Login Failed! Currently stuck at URL: {driver.current_url}. Retrying login...")
                    try: driver.quit()
                    except: pass
                    driver = None
                    time.sleep(15)
                    continue
                    
                print("✅ Dashboard Reached Successfully! Letting session stabilize...")
                time.sleep(5) 
            
            # 🚀 SMART FIX 2: কোনো স্ক্রিপ্ট ফেচ নয়, ব্রাউজার নিজেই সরাসরি এপিআই ইউআরএল লোড করবে
            print("⚡ Scanning Paid Inbox directly via browser tab...")
            try:
                driver.get("https://www.ivasms.com/portal/live/my_sms")
                time.sleep(2.5) # পেজ লোড সেটেলমেন্ট ডিলে
            except Exception as get_err:
                print(f"⚠️ API navigation error: {get_err}. Restarting driver...")
                try: driver.quit()
                except: pass
                driver = None
                time.sleep(10)
                continue
                
            # ব্রাউজার স্ক্রিন থেকে সরাসরি টেক্সট রিড করা
            try:
                raw_text = driver.find_element("tag name", "body").text.strip()
            except Exception as dom_err:
                print(f"⚠️ Cannot read body text: {dom_err}. Restarting driver...")
                try: driver.quit()
                except: pass
                driver = None
                time.sleep(10)
                continue
                
            # ক্লাউডফ্লেয়ার ব্লকিং ডিটেকশন ও স্বয়ংক্রিয় ক্যাপচা ক্লিক সলভার
            if "cloudflare" in raw_text.lower() or "just a moment" in raw_text.lower() or "security" in raw_text.lower():
                print("🛡️ Cloudflare challenge detected on API URL! Attempting bypass...")
                try:
                    driver.uc_gui_click_captcha()
                    time.sleep(5)
                except:
                    pass
                continue
                
            # যদি সেশন এক্সপায়ার হয়ে লগইন পেজে নিয়ে যায় বা ডাটা ইনভ্যালিড হয়
            if not raw_text.startswith("{") and not raw_text.startswith("["):
                print("🚨 API returned HTML Page instead of JSON! Session expired. Re-logging in...")
                try: driver.quit()
                except: pass
                driver = None
                time.sleep(5)
                continue
                
            # ডাটা সফলভাবে পার্স করা
            try:
                json_data = json.loads(raw_text)
            except Exception as parse_err:
                print(f"🚨 JSON Parse Exception: {parse_err}. Raw text received: {raw_text[:150]}")
                time.sleep(6)
                continue
                
            # JSON Data Handle
            if isinstance(json_data, dict):
                sms_list = json_data.get('data', [])
            elif isinstance(json_data, list):
                sms_list = json_data
            else:
                sms_list = []
                
            if not sms_list or len(sms_list) == 0:
                if is_first_run:
                    print("📭 Inbox is currently empty. Waiting peacefully for new OTPs...")
                    is_first_run = False
                time.sleep(6)
                continue
                
            # Forwarding OTPs
            if is_first_run:
                print(f"📥 Found {len(sms_list)} OTPs in inbox. Forwarding them to the group...")
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
                        # সাইলেন্ট মেসেজ (MUTE ON)
                        bot.send_message(GROUP_ID, msg_body, parse_mode="HTML", reply_markup=markup, disable_notification=True)
                        print(f"✅ PAID OTP Sent (Silent) >> {service_title} | Number: {exact_range}")
                        time.sleep(2.5) 
                    except Exception as e:
                        if "Too Many Requests" in str(e):
                            print("⏳ Telegram Anti-Spam! Pausing for 15 seconds...")
                            time.sleep(15)
                        else:
                            print(f"❌ Telegram Error: {e}")
                            
            time.sleep(6) 
            
        except Exception as e:
            print(f"🔥 Critical System Error! Self-healing in 10s... Details: {e}")
            if driver:
                try: driver.quit()
                except: pass
                driver = None
            time.sleep(10)

if __name__ == "__main__":
    print("🤖 Paid SMS Bot is turning on (Priyo Bot Login + Instant Delivery + Mute)...")
    threading.Thread(target=monitor_ranges, daemon=True).start()
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
        except Exception:
            time.sleep(3)
