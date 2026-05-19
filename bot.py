import os
import time
import json
import re
import threading
import html
import telebot
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

# ==========================================
# 🌍 MASSIVE COUNTRY DICTIONARY (230+ Countries)
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
    "92": ("Pakistan", "🇵🇰"), "98": ("Iran", "🇮🇷"), "212": ("Morocco", "🇲🇦"), 
    "234": ("Nigeria", "🇳🇬"), "254": ("Kenya", "🇰🇪"), "351": ("Portugal", "🇵🇹"), 
    "380": ("Ukraine", "🇺🇦"), "880": ("Bangladesh", "🇧🇩"), "966": ("Saudi Arabia", "🇸🇦"), 
    "971": ("UAE", "🇦🇪"), "998": ("Uzbekistan", "🇺🇿"), "249": ("Sudan", "🇸🇩")
}

# ==========================================
# 🚀 SMART BOT LOGIC
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN)
seen_messages = set()
is_first_run = True

@bot.message_handler(commands=['setbot'])
def set_bot_username(message):
    global USER_BOT_USERNAME
    try:
        if str(message.chat.id) == GROUP_ID:
            user_status = bot.get_chat_member(message.chat.id, message.from_user.id).status
            if user_status in ['creator', 'administrator']:
                text = message.text.split()
                if len(text) > 1:
                    new_username = text[1].replace('https://t.me/', '').replace('@', '')
                    USER_BOT_USERNAME = new_username
                    bot.reply_to(message, f"✅ <b>Bot Link Updated!</b>\nRedirecting to: <b>@{USER_BOT_USERNAME}</b>.", parse_mode="HTML")
    except Exception as e:
        pass

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
            country_info = f"{' '.join(letters_only).title()} 🏳️"

    return country_info, exact_range

def get_clean_service(text):
    if not text: return "Unknown"
    text = re.split(r'<script|function|\$\(', str(text), flags=re.IGNORECASE)[0]
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'[^a-zA-Z0-9\s\-]', '', text).strip().upper()

def get_clean_message(text):
    if not text: return "No Text"
    text = re.split(r'function', str(text), flags=re.IGNORECASE)[0]
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    return re.sub(r'\s+', ' ', text).replace('<', '').replace('>', '').strip()

# ==========================================
# 🌐 SELENIUMBASE AUTO-LOGIN & XHR SCRAPER
# ==========================================

def monitor_ranges():
    global is_first_run
    
    print("🚀 Booting up invisible Chrome Browser (SeleniumBase UC Mode)...")
    
    try:
        driver = Driver(uc=True, headless=False)
        
        print("🔐 Navigating to iVASMS login page...")
        driver.uc_open_with_reconnect("https://www.ivasms.com/login", 5)
        
        print("⏳ Bypassing Cloudflare Turnstile...")
        try:
            driver.uc_gui_click_captcha()
        except Exception:
            pass 
            
        print("⏳ Waiting for Email Field...")
        driver.wait_for_element('input[name="email"]', timeout=40)
        
        print("✅ Cloudflare bypassed! Entering credentials...")
        driver.type('input[name="email"]', EMAIL)
        driver.type('input[name="password"]', PASSWORD)
        driver.click('button[type="submit"]')
        
        print("✅ Login Clicked! Waiting 15s for dashboard to fully load...")
        time.sleep(15) # লগইন কমপ্লিট হয়ে ড্যাশবোর্ডে যাওয়ার জন্য পর্যাপ্ত সময়
        
        # লগইন সফল হয়েছে কিনা চেক করা
        current_url = driver.get_current_url()
        if "login" in current_url:
            print("⚠️ Warning: Bot might still be on login page. Trying to proceed anyway...")
        else:
            print("✅ Dashboard accessed successfully!")
        
        print("📡 Starting 24/7 Background API Monitoring...")
        
        # 🧠 আল্ট্রা-স্মার্ট XHR Fetch Script (যাতে সার্ভার বোঝে এটা আসল ড্যাশবোর্ড)
        fetch_script = """
        var callback = arguments[arguments.length - 1];
        var xhr = new XMLHttpRequest();
        xhr.open('GET', arguments[0], true);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhr.setRequestHeader('Accept', 'application/json, text/javascript, */*; q=0.01');
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4) {
                callback(xhr.responseText);
            }
        };
        xhr.send();
        """
        
        driver.set_script_timeout(20)

        while True:
            try:
                # ⚠️ ব্রাউজার দিয়ে পেজ রিলোড না করে, ব্যাকগ্রাউন্ড স্ক্রিপ্ট দিয়ে ডাটা আনা হচ্ছে
                page_text = driver.execute_async_script(fetch_script, API_URL)
                
                # JSON এরর চেক করার জন্য স্মার্ট ট্রাই-ক্যাচ
                try:
                    json_data = json.loads(page_text)
                except Exception as json_err:
                    print(f"⚠️ Server didn't return JSON. Received data: {str(page_text)[:100]}...")
                    # যদি সেশন এক্সপায়ার হয়ে যায়, পেজটা রিলোড দিয়ে সেশন ঠিক করবে
                    if "<html" in str(page_text).lower():
                        print("🔄 Session expired or blocked. Refreshing dashboard...")
                        driver.refresh()
                        time.sleep(5)
                    time.sleep(10)
                    continue

                sms_list = json_data.get('data', [])
                
                if is_first_run:
                    print(f"📥 Found {len(sms_list)} old ranges. Saving them quietly...")
                    for sms in sms_list:
                        seen_messages.add(str(sms.get('id', '')))
                    is_first_run = False
                    time.sleep(5)
                    continue

                for sms in reversed(sms_list):
                    msg_id = str(sms.get('id', ''))
                    
                    if msg_id and msg_id not in seen_messages:
                        service = get_clean_service(sms.get('originator', 'Unknown'))
                        
                        if not any(allowed in service for allowed in ALLOWED_SERVICES):
                            seen_messages.add(msg_id)
                            continue 
                        
                        term_data = sms.get('termination', {})
                        raw_number = str(term_data.get('test_number', sms.get('test_number', 'Unknown')))
                        range_count_text = str(sms.get('range', 'Active')) 
                        
                        country_info, exact_range = get_country_and_exact_range(raw_number, range_count_text)
                        service_display = SERVICE_LOGOS.get(service, f"🌐 {service}")
                        full_text = get_clean_message(sms.get('messagedata', 'No Text'))

                        msg_body = (
                            f"✅ <b>ACTIVE NEW RANGE</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━\n"
                            f"🌍 <b>Country:</b> {country_info}\n"
                            f"🎯 <b>Range:</b> {exact_range}\n"
                            f"⚙️ <b>Service:</b> {service_display}\n"
                            f"📊 <b>Range Qty:</b> {range_count_text}\n"
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
                            print(f"✅ Posted >> {service} | Range: {exact_range}")
                        except Exception as e:
                            print(f"❌ Telegram Error: {e}")
                            
            except Exception as e:
                print(f"⚠️ Loop Error (Retrying...): {e}")
                
            time.sleep(10)

    except Exception as e:
        print(f"🔥 Critical Browser Error: {e}")
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    print("🤖 Master Bot is turning on...")
    threading.Thread(target=monitor_ranges, daemon=True).start()
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            time.sleep(3)
