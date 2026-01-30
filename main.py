import os
import time
import re
import random
import datetime
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
THREADS = 2           
BURST_SIZE = 10       
BURST_SPEED = 0.4     
CYCLE_DELAY = 2.0     
SESSION_DURATION = 1200 
LOG_FILE = "message_log.txt"

GLOBAL_SENT = 0
COUNTER_LOCK = threading.Lock()

def log_status(agent_id, msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] 🤖 Agent {agent_id}: {msg}"
    print(entry, flush=True)

def log_speed(agent_id, current_sent, start_time):
    elapsed = time.time() - start_time
    if elapsed == 0: elapsed = 1
    speed = current_sent / elapsed
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    with COUNTER_LOCK:
        total = GLOBAL_SENT
    entry = f"[{timestamp}] ⚡ Agent {agent_id} | Total: {total} | Speed: {speed:.1f} msg/s"
    print(entry, flush=True)

def get_driver(agent_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # 📉 V53: LIGHTWEIGHT MODE
    prefs = {
        "profile.managed_default_content_settings.images": 2, 
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.geolocation": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # STEALTH
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # MOBILE EMULATION (Pixel 5)
    mobile_emulation = {
        "deviceMetrics": { "width": 393, "height": 851, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    chrome_options.add_argument(f"--user-data-dir=/tmp/chrome_v53_{agent_id}_{random.randint(100,999)}")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # CDP PATCH
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    
    return driver

def find_mobile_box(driver):
    selectors = [
        "//textarea", 
        "//div[@role='textbox']", 
        "//div[@contenteditable='true']"
    ]
    for xpath in selectors:
        try: 
            el = driver.find_element(By.XPATH, xpath)
            if el.is_displayed(): return el
        except: continue
    return None

def automa_inject(driver, element, text):
    try:
        element.click()
        driver.execute_script("""
            var el = arguments[0];
            el.focus();
            document.execCommand('insertText', false, arguments[1]);
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        """, element, text)
        time.sleep(0.15)
        try:
            driver.find_element(By.XPATH, "//div[contains(text(), 'Send')] | //button[text()='Send']").click()
        except:
            element.send_keys(Keys.ENTER)
        return True
    except:
        return False

def extract_session_id(raw_cookie):
    """
    🔥 V53: SMART PARSER
    Extracts the session ID regardless of format (JSON, Header, Raw)
    """
    if not raw_cookie: return None
    
    # 1. Try Regex for standard ID format (30+ chars, mostly alphanumeric/percent)
    # Looks for pattern like: 54321%3A... or 54321:...
    match = re.search(r'sessionid=([^;]+)', raw_cookie)
    if match:
        return match.group(1).strip()
        
    # 2. Fallback: Assume the user pasted JUST the ID
    if len(raw_cookie) > 20 and "sessionid" not in raw_cookie:
        return raw_cookie.strip()
        
    return None

def run_life_cycle(agent_id, cookie, target, messages):
    driver = None
    sent_in_this_life = 0
    start_time = time.time()
    
    try:
        log_status(agent_id, "🚀 Phoenix V53 (Smart Cookie Parser)...")
        driver = get_driver(agent_id)
        
        driver.get("https://www.instagram.com/")
        time.sleep(2)
        
        # 🍪 V53: SMART PARSING
        clean_session = extract_session_id(cookie)
        if not clean_session:
            log_status(agent_id, "❌ FATAL: Could not parse Session ID from secret.")
            return

        try:
            driver.add_cookie({
                'name': 'sessionid', 
                'value': clean_session, 
                'path': '/', 
                'domain': '.instagram.com'
            })
        except Exception as e:
            log_status(agent_id, f"❌ Cookie Injection Error: {e}")
            return
        
        driver.refresh()
        time.sleep(3) 
        
        if "login" in driver.current_url:
            log_status(agent_id, "💀 Cookie Expired (Redirected to Login).")
            return

        target_url = f"https://www.instagram.com/direct/t/{target}/"
        log_status(agent_id, "🔍 Navigating...")
        driver.get(target_url)
        time.sleep(5)
        
        try:
            driver.execute_script("document.querySelectorAll('div[role=dialog]').forEach(e => e.remove());")
            driver.find_element(By.XPATH, "//button[text()='Not Now']").click()
        except: pass
        
        msg_box = find_mobile_box(driver)
        
        if not msg_box:
            log_status(agent_id, "❌ Box not found.")
            return

        log_status(agent_id, "✅ Automa Active. Sending...")

        while (time.time() - start_time) < SESSION_DURATION:
            try:
                for _ in range(BURST_SIZE):
                    msg = random.choice(messages)
                    automa_inject(driver, msg_box, f"{msg} ")
                    
                    sent_in_this_life += 1
                    with COUNTER_LOCK:
                        global GLOBAL_SENT
                        GLOBAL_SENT += 1
                    
                    time.sleep(BURST_SPEED)
                
                log_speed(agent_id, sent_in_this_life, start_time)
                time.sleep(CYCLE_DELAY)
            except:
                break

    except Exception as e:
        log_status(agent_id, f"❌ Crash: {e}")
    finally:
        if driver: driver.quit()

def agent_worker(agent_id, cookie, target, messages):
    while True:
        run_life_cycle(agent_id, cookie, target, messages)
        time.sleep(5)

def main():
    print("🔥 V53 SMART COOKIE PARSER | AUTOMA MODE", flush=True)
    
    cookie = os.environ.get("INSTA_COOKIE", "").strip()
    target = os.environ.get("TARGET_THREAD_ID", "").strip()
    messages = os.environ.get("MESSAGES", "Hello").split("|")

    if not cookie:
        print("❌ CRITICAL: INSTA_COOKIE is missing.")
        return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(agent_worker, i+1, cookie, target, messages)

if __name__ == "__main__":
    main()
