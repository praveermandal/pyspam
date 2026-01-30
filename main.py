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
from selenium.webdriver.common.action_chains import ActionChains

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
    chrome_options.add_argument("--incognito")
    
    # MANUAL MOBILE METRICS (Pixel 5)
    mobile_emulation = {
        "deviceMetrics": { "width": 393, "height": 851, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 12; Pixel 5 Build/SP1A.210812.016.A1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f"--user-data-dir=/tmp/chrome_v36_{agent_id}_{random.randint(100,999)}")
    return webdriver.Chrome(options=chrome_options)

def bypass_blockers(driver, agent_id):
    """
    V36: BLIND BYPASS
    Presses TAB + ENTER repeatedly to clear generic overlays (Cookie walls/App upsells)
    """
    log_status(agent_id, "🔨 Attempting Blind Bypass (Tab+Enter)...")
    try:
        actions = ActionChains(driver)
        # Tab 2 times then Enter (Common for 'Allow Cookies' buttons)
        actions.send_keys(Keys.TAB * 2).send_keys(Keys.ENTER).perform()
        time.sleep(2)
        
        # Try finding 'Log In' link on home page
        try:
            login_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Log In')] | //button[contains(text(), 'Log In')]")
            login_link.click()
            time.sleep(3)
        except: pass
        
    except: pass

def full_login_flow(driver, agent_id, username, password):
    log_status(agent_id, "🔑 Navigating to Login...")
    try:
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(5)
        
        # Check Title
        log_status(agent_id, f"📄 Page: {driver.title}")
        
        # 1. First Attempt to find Username
        try:
            user_input = driver.find_element(By.NAME, "username")
        except:
            # 🚨 BLOCKED? TRIGGER V36 BYPASS
            log_status(agent_id, "⚠️ Login field hidden. Running Modal Breaker...")
            bypass_blockers(driver, agent_id)
            
            # Retry finding username
            try:
                user_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
            except:
                log_status(agent_id, "❌ Still Blocked. Dumping Screenshot.")
                driver.save_screenshot(f"blocked_agent_{agent_id}.png")
                return False

        # 2. Login Process
        user_input.send_keys(username)
        time.sleep(1)
        
        pass_input = driver.find_element(By.NAME, "password")
        pass_input.send_keys(password)
        time.sleep(1)
        pass_input.send_keys(Keys.ENTER)
            
        log_status(agent_id, "⏳ Verifying Login...")
        time.sleep(12)
        
        if "login" in driver.current_url:
            log_status(agent_id, "❌ Login Failed.")
            return False
            
        log_status(agent_id, "✅ Login Success.")
        return True

    except Exception as e:
        log_status(agent_id, f"❌ Login Exception: {e}")
        return False

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

def run_life_cycle(agent_id, user, pw, target, messages):
    driver = None
    sent_in_this_life = 0
    start_time = time.time()
    
    try:
        log_status(agent_id, "🚀 Phoenix V36 (Modal Breaker)...")
        driver = get_driver(agent_id)
        
        if not full_login_flow(driver, agent_id, user, pw):
            return

        target_url = f"https://www.instagram.com/direct/t/{target}/"
        driver.get(target_url)
        time.sleep(8)
        
        # Run bypass again just in case 'Use App' popup appears
        bypass_blockers(driver, agent_id)
        
        msg_box = find_mobile_box(driver)
        
        if not msg_box:
            log_status(agent_id, "❌ Chat box not found.")
            driver.save_screenshot(f"box_not_found_agent_{agent_id}.png")
            return

        log_status(agent_id, "✅ Target Locked. Sending...")

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
        log_status(agent_id, f"❌ Agent Crash: {e}")
    finally:
        if driver: driver.quit()

def agent_worker(agent_id, user, pw, target, messages):
    while True:
        run_life_cycle(agent_id, user, pw, target, messages)
        time.sleep(10)

def main():
    with open(LOG_FILE, "w") as f: f.write("PHOENIX V36 START\n")
    print("🔥 V36 MODAL BREAKER | STANDING BY", flush=True)
    
    user = os.environ.get("INSTA_USER", "").strip()
    pw = os.environ.get("INSTA_PASS", "").strip()
    target = os.environ.get("TARGET_THREAD_ID", "").strip()
    messages = os.environ.get("MESSAGES", "Hello").split("|")

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(agent_worker, i+1, user, pw, target, messages)

if __name__ == "__main__":
    main()
