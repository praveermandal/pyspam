import os
import time
import random
import datetime
import shutil
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- HYBRID CONFIGURATION ---
THREADS = 2           
BURST_SIZE = 8        # Balanced size
BURST_DELAY = 0.1     # 100ms (Fast but safe)
CYCLE_DELAY = 1.5     # 1.5s pause

# ♻️ TIMING LOGIC
SESSION_DURATION = 1200  # 20 Minutes (Full Restart)
REFRESH_INTERVAL = 300   # 5 Minutes (Page Refresh Only)
LOG_FILE = "message_log.txt"

# USER AGENT ROTATION
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

def log_status(agent_id, msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] 🤖 Agent {agent_id}: {msg}", flush=True)

def log_speed(agent_id, count, start_time):
    elapsed = time.time() - start_time
    if elapsed == 0: elapsed = 1
    speed = count / elapsed
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] ⚡ Agent {agent_id} | Total: {count} | Speed: {speed:.1f} msg/s"
    print(entry, flush=True)
    try:
        with open(LOG_FILE, "a") as f: f.write(entry + "\n")
    except: pass

def get_driver(agent_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Anti-Detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    
    # Rotate Identity
    agent = random.choice(USER_AGENTS)
    chrome_options.add_argument(f"user-agent={agent}")
    
    # Unique Profile
    chrome_options.add_argument(f"--user-data-dir=/tmp/chrome_p_{agent_id}_{random.randint(1,99999)}")
    
    return webdriver.Chrome(options=chrome_options)

def instant_inject(driver, element, text):
    driver.execute_script("""
        var elm = arguments[0], txt = arguments[1];
        elm.focus();
        document.execCommand('insertText', false, txt);
        elm.dispatchEvent(new Event('input', {bubbles: true}));
    """, element, text)

def run_life_cycle(agent_id, session_id, target_input, messages):
    driver = None
    sent_in_this_life = 0
    session_start_time = time.time()
    last_refresh_time = time.time()
    
    try:
        log_status(agent_id, "🔥 Starting Hybrid Session (20m)...")
        driver = get_driver(agent_id)
        
        # Login
        driver.get("https://www.instagram.com/404") 
        clean_session = session_id.split("sessionid=")[1].split(";")[0] if "sessionid=" in session_id else session_id
        driver.add_cookie({'name': 'sessionid', 'value': clean_session, 'domain': '.instagram.com', 'path': '/'})
        driver.refresh()
        time.sleep(5)

        # Check Login
        driver.get(f"https://www.instagram.com/direct/t/{target_input}/")
        time.sleep(5)
        
        if "login" in driver.current_url:
            log_status(agent_id, "⚠️ Session Expired. Stopping.")
            return

        box_xpath = "//div[@contenteditable='true']"
        try:
            msg_box = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, box_xpath)))
        except:
             return

        # --- THE HYBRID LOOP ---
        while (time.time() - session_start_time) < SESSION_DURATION:
            
            # 1. RAM CHECK: Has it been 5 minutes?
            if (time.time() - last_refresh_time) > REFRESH_INTERVAL:
                log_status(agent_id, "♻️ 5-Minute RAM Flush (Soft Refresh)...")
                driver.refresh()
                time.sleep(5)
                try:
                    msg_box = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, box_xpath)))
                except:
                    break
                last_refresh_time = time.time()

            # 2. SEND MESSAGES
            try:
                for _ in range(BURST_SIZE):
                    msg = random.choice(messages)
                    jitter = "⠀" * random.randint(0, 1)
                    instant_inject(driver, msg_box, f"{msg}{jitter}")
                    msg_box.send_keys(Keys.ENTER)
                    sent_in_this_life += 1
                    time.sleep(BURST_DELAY)
                
                log_speed(agent_id, sent_in_this_life, session_start_time)
                time.sleep(CYCLE_DELAY)

            except Exception:
                # If element becomes stale, force a refresh loop
                last_refresh_time = 0 
                time.sleep(1)

    except Exception as e:
        log_status(agent_id, f"Error: {e}")
    finally:
        if driver:
            try: driver.quit()
            except: pass
        try: shutil.rmtree(f"/tmp/chrome_p_{agent_id}", ignore_errors=True)
        except: pass

def agent_worker(agent_id, session_id, target_input, messages):
    while True:
        run_life_cycle(agent_id, session_id, target_input, messages)
        time.sleep(10) 

def main():
    print(f"🚀 V19.1 HYBRID | REFRESH 5m | RESTART 20m", flush=True)
    
    session_id = os.environ.get("INSTA_SESSION", "").strip()
    target_input = os.environ.get("TARGET_THREAD_ID", "").strip()
    messages = os.environ.get("MESSAGES", "Hello").split("|")

    if not session_id: return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(agent_worker, i+1, session_id, target_input, messages)

if __name__ == "__main__":
    main()
