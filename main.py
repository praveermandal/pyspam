import os
import time
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
BURST_SIZE = 5        
BURST_DELAY = 1.0     
CYCLE_DELAY = 3.0     
SESSION_DURATION = 1200 
REFRESH_INTERVAL = 300 
LOG_FILE = "message_log.txt"

GLOBAL_SENT = 0
COUNTER_LOCK = threading.Lock()

def write_log(msg):
    try:
        with open(LOG_FILE, "a") as f: f.write(msg + "\n")
    except: pass

def log_status(agent_id, msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] 🤖 Agent {agent_id}: {msg}"
    print(entry, flush=True)
    write_log(entry)

def log_speed(agent_id, current_sent, start_time):
    elapsed = time.time() - start_time
    if elapsed == 0: elapsed = 1
    speed = current_sent / elapsed
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    with COUNTER_LOCK:
        total = GLOBAL_SENT
    entry = f"[{timestamp}] ⚡ Agent {agent_id} | Session Total: {total} | Speed: {speed:.1f} msg/s"
    print(entry, flush=True)
    write_log(entry)

def get_driver(agent_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # 🚨 V38: SESSION HIJACK CONFIG
    # We must look EXACTLY like a phone for the cookie to work
    mobile_emulation = {
        "deviceMetrics": { "width": 393, "height": 851, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    # Disable Automation Flags that trigger 'Suspicious Activity'
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    chrome_options.add_argument(f"--user-data-dir=/tmp/chrome_v38_{agent_id}_{random.randint(100,999)}")
    return webdriver.Chrome(options=chrome_options)

def clear_popups(driver):
    popups = [
        "//button[text()='Not Now']",
        "//button[text()='Cancel']",
        "//div[text()='Not now']",
        "//button[contains(text(), 'Use the App')]/following-sibling::button", # Close App upsell
        "//button[contains(@aria-label, 'Close')]"
    ]
    for xpath in popups:
        try:
            driver.find_element(By.XPATH, xpath).click()
            time.sleep(1)
        except: pass

def find_mobile_box(driver):
    selectors = [
        "//textarea", 
        "//div[@role='textbox']",
        "//div[contains(@aria-label, 'Message')]"
    ]
    for xpath in selectors:
        try: return driver.find_element(By.XPATH, xpath)
        except: continue
    return None

def mobile_js_inject(driver, element, text):
    driver.execute_script("""
        var elm = arguments[0], txt = arguments[1];
        elm.value = txt;
        elm.dispatchEvent(new Event('input', {bubbles: true}));
    """, element, text)
    time.sleep(0.5)
    element.send_keys(" ")
    element.send_keys(Keys.BACK_SPACE)
    time.sleep(0.5) 
    try:
        send_btn = driver.find_element(By.XPATH, "//div[contains(text(), 'Send')] | //button[text()='Send']")
        send_btn.click()
    except:
        element.send_keys(Keys.ENTER)

def run_life_cycle(agent_id, cookie, target, messages):
    driver = None
    sent_in_this_life = 0
    start_time = time.time()
    
    try:
        log_status(agent_id, "🚀 Phoenix V38 (Session Hijack)...")
        driver = get_driver(agent_id)
        
        # 1. Go to Domain
        driver.get("https://www.instagram.com/")
        time.sleep(3)
        
        # 2. Inject Cookie DIRECTLY (Skip Login Page)
        if cookie:
            try:
                clean_session = cookie.split("sessionid=")[1].split(";")[0] if "sessionid=" in cookie else cookie
                driver.add_cookie({'name': 'sessionid', 'value': clean_session, 'path': '/'})
                log_status(agent_id, "🍪 Cookie Injected.")
            except:
                log_status(agent_id, "❌ Error parsing cookie!")
                return
        
        # 3. Reload to Activate Cookie
        driver.refresh()
        time.sleep(5)
        
        # 4. Check if Cookie worked
        # If we see "Log In" button, the cookie is DEAD
        if "login" in driver.current_url or "Log In" in driver.title:
            log_status(agent_id, "💀 Cookie is DEAD/Expired. Stopping Agent.")
            driver.save_screenshot(f"dead_cookie_agent_{agent_id}.png")
            return

        # 5. Navigate to Target
        target_url = f"https://www.instagram.com/direct/t/{target}/"
        log_status(agent_id, "🔍 Navigating to Target...")
        driver.get(target_url)
        time.sleep(8)
        
        clear_popups(driver)
        
        # 6. Verify we are NOT in the Inbox list
        if "/inbox" in driver.current_url and "/t/" not in driver.current_url:
            log_status(agent_id, "⚠️ Redirected to Inbox. Checking for 'Not Now' popup...")
            clear_popups(driver)
            driver.get(target_url) # Try forcing URL one more time
            time.sleep(8)

        msg_box = find_mobile_box(driver)
        
        if not msg_box:
            log_status(agent_id, "❌ Chat box not found.")
            driver.save_screenshot(f"box_not_found_agent_{agent_id}.png")
            
            # If we are stuck on a challenge page
            if "challenge" in driver.current_url:
                log_status(agent_id, "🚨 ACCOUNT CHALLENGED (Phone Verification Req).")
            return

        log_status(agent_id, "✅ Session Active. Sending...")

        while (time.time() - start_time) < SESSION_DURATION:
            try:
                for _ in range(BURST_SIZE):
                    msg = random.choice(messages)
                    mobile_js_inject(driver, msg_box, f"{msg} ")
                    sent_in_this_life += 1
                    with COUNTER_LOCK:
                        global GLOBAL_SENT
                        GLOBAL_SENT += 1
                    time.sleep(random.uniform(0.1, 0.3))
                
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
        # Note: Username/Pass removed. We rely 100% on cookie.
        run_life_cycle(agent_id, cookie, target, messages)
        time.sleep(10)

def main():
    with open(LOG_FILE, "w") as f: f.write("PHOENIX V38 START\n")
    print("🔥 V38 SESSION HIJACK | COOKIE ONLY", flush=True)
    
    cookie = os.environ.get("INSTA_COOKIE", "").strip()
    target = os.environ.get("TARGET_THREAD_ID", "").strip()
    messages = os.environ.get("MESSAGES", "Hello").split("|")

    if not cookie: 
        print("❌ CRITICAL: INSTA_COOKIE Missing!")
        return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(agent_worker, i+1, cookie, target, messages)

if __name__ == "__main__":
    main()
