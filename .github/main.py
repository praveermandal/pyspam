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

# --- PHOENIX TURBO CONFIG (SPEED BOOSTED) ---
THREADS = 2           
BURST_SIZE = 10       # [INCREASED] From 8 to 10 messages per burst
BURST_DELAY = 0.03    # [FASTER] From 0.05s to 0.03s (30ms)
CYCLE_DELAY = 0.8     # [FASTER] From 1.0s to 0.8s

# ♻️ THE 5-MINUTE RULE
LIFE_DURATION = 300   # 300 Seconds = 5 Minutes exactly
LOG_FILE = "message_log.txt"

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
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    # Forces a unique temp profile for every single restart
    chrome_options.add_argument(f"--user-data-dir=/tmp/chrome_p_{agent_id}_{random.randint(1,99999)}")
    chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/12{agent_id+8}.0.0.0 Safari/537.36")
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
    start_time = time.time()
    
    try:
        log_status(agent_id, "🔥 Refreshing Browser Engine...")
        driver = get_driver(agent_id)
        
        driver.get("https://www.instagram.com/")
        clean_session = session_id.split("sessionid=")[1].split(";")[0] if "sessionid=" in session_id else session_id
        driver.add_cookie({'name': 'sessionid', 'value': clean_session, 'domain': '.instagram.com', 'path': '/'})
        driver.refresh()
        time.sleep(5)

        driver.get(f"https://www.instagram.com/direct/t/{target_input}/")
        time.sleep(5)
        
        box_xpath = "//div[@contenteditable='true']"
        msg_box = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, box_xpath)))

        # 5-MINUTE TIMER LOOP
        while (time.time() - start_time) < LIFE_DURATION:
            try:
                for _ in range(BURST_SIZE):
                    msg = random.choice(messages)
                    jitter = "⠀" * random.randint(0, 1)
                    instant_inject(driver, msg_box, f"{msg}{jitter}")
                    msg_box.send_keys(Keys.ENTER)
                    sent_in_this_life += 1
                    time.sleep(BURST_DELAY)
                
                log_speed(agent_id, sent_in_this_life, start_time)
                time.sleep(CYCLE_DELAY)

            except Exception:
                break # Restart on any minor error
                
    except Exception as e:
        log_status(agent_id, f"Life Cycle Error: {e}")
    finally:
        if driver:
            try: 
                driver.quit()
                log_status(agent_id, f"Successfully retired. Sent: {sent_in_this_life}")
            except: pass
        # Clean up temp folder immediately
        try: shutil.rmtree(f"/tmp/chrome_p_{agent_id}", ignore_errors=True)
        except: pass

def agent_worker(agent_id, session_id, target_input, messages):
    while True:
        run_life_cycle(agent_id, session_id, target_input, messages)
        time.sleep(2) # 2s breather before rebirth

def main():
    print(f"🚀 V18.3 PHOENIX TURBO | 5-MIN REBIRTH | {THREADS} AGENTS", flush=True)
    
    session_id = os.environ.get("INSTA_SESSION", "").strip()
    target_input = os.environ.get("TARGET_THREAD_ID", "").strip()
    messages = os.environ.get("MESSAGES", "Hello").split("|")

    if not session_id: return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(agent_worker, i+1, session_id, target_input, messages)

if __name__ == "__main__":
    main()
