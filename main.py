import os
import time
import re
import random
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# --- ADAPTIVE CONFIGURATION ---
THREADS = 2           
BASE_BURST = 20       # High speed target
BASE_SPEED = 0.2      # Fast injection
BASE_DELAY = 1.0      # Short breather
SESSION_DURATION = 1200 

GLOBAL_SENT = 0
COUNTER_LOCK = threading.Lock()

def log_status(agent_id, msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] 🤖 Agent {agent_id}: {msg}", flush=True)

def log_speed(agent_id, current_sent, start_time, mode="Normal"):
    elapsed = time.time() - start_time
    if elapsed == 0: elapsed = 1
    speed = current_sent / elapsed
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    with COUNTER_LOCK:
        total = GLOBAL_SENT
    print(f"[{timestamp}] ⚡ Agent {agent_id} | Mode: {mode} | Total: {total} | Speed: {speed:.1f} msg/s", flush=True)

def get_driver(agent_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    mobile_emulation = {
        "deviceMetrics": { "width": 393, "height": 851, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    chrome_options.add_argument(f"--user-data-dir=/tmp/chrome_v54_{agent_id}_{random.randint(100,999)}")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def find_mobile_box(driver):
    selectors = ["//textarea", "//div[@role='textbox']", "//div[@contenteditable='true']"]
    for xpath in selectors:
        try: 
            el = driver.find_element(By.XPATH, xpath)
            if el.is_displayed(): return el
        except: continue
    return None

def adaptive_inject(driver, element, text):
    """
    🔥 V54: ADAPTIVE INJECTION
    Returns True if successful, False if blocked.
    """
    try:
        element.click()
        driver.execute_script("""
            var el = arguments[0];
            el.focus();
            document.execCommand('insertText', false, arguments[1]);
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        """, element, text)
        time.sleep(0.1)
        
        btn = driver.find_element(By.XPATH, "//div[contains(text(), 'Send')] | //button[text()='Send']")
        btn.click()
        return True
    except:
        try:
            element.send_keys(Keys.ENTER)
            return True
        except:
            return False

def extract_session_id(raw_cookie):
    match = re.search(r'sessionid=([^;]+)', raw_cookie)
    return match.group(1).strip() if match else raw_cookie.strip()

def run_life_cycle(agent_id, cookie, target, messages):
    driver = None
    sent_in_this_life = 0
    start_time = time.time()
    recovery_mode = False
    
    try:
        log_status(agent_id, "🚀 Phoenix V54 (Adaptive Engine)...")
        driver = get_driver(agent_id)
        driver.get("https://www.instagram.com/")
        time.sleep(2)
        
        clean_session = extract_session_id(cookie)
        driver.add_cookie({'name': 'sessionid', 'value': clean_session, 'path': '/', 'domain': '.instagram.com'})
        driver.refresh()
        time.sleep(4) 
        
        driver.get(f"https://www.instagram.com/direct/t/{target}/")
        time.sleep(6)

        while (time.time() - start_time) < SESSION_DURATION:
            msg_box = find_mobile_box(driver)
            if not msg_box:
                log_status(agent_id, "⚠️ Box missing. Entering Recovery...")
                time.sleep(30) # Wait for UI to return
                driver.refresh()
                time.sleep(5)
                continue

            # Set dynamic speed based on status
            current_burst = 5 if recovery_mode else BASE_BURST
            current_speed = 1.0 if recovery_mode else BASE_SPEED
            current_delay = 5.0 if recovery_mode else BASE_DELAY

            success_count = 0
            for _ in range(current_burst):
                msg = random.choice(messages)
                if adaptive_inject(driver, msg_box, f"{msg} "):
                    success_count += 1
                    sent_in_this_life += 1
                    with COUNTER_LOCK:
                        global GLOBAL_SENT
                        GLOBAL_SENT += 1
                    time.sleep(current_speed)
                else:
                    break # Break burst if one fails

            # Logic: If entire burst failed, turn on recovery
            if success_count == 0:
                recovery_mode = True
                log_status(agent_id, "🐢 Rate Limit Detected. Slowing down...")
            else:
                recovery_mode = False

            log_speed(agent_id, sent_in_this_life, start_time, "Recovery" if recovery_mode else "High-Speed")
            time.sleep(current_delay)

    except Exception as e:
        log_status(agent_id, f"❌ Crash: {e}")
    finally:
        if driver: driver.quit()

def main():
    cookie = os.environ.get("INSTA_COOKIE", "").strip()
    target = os.environ.get("TARGET_THREAD_ID", "").strip()
    messages = os.environ.get("MESSAGES", "Hello").split("|")
    if not cookie: return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(run_life_cycle, i+1, cookie, target, messages)

if __name__ == "__main__":
    main()
