# -*- coding: utf-8 -*-
# 🚀 PROJECT: PHOENIX V100.32 (QUANTUM-STRIKE)
# 🛡️ CREDITS: PRAVEERFUCKS | 120-AGENT OVERCLOCK
# ⚡ FIX: PARALLEL TAB INJECTION | SURPASSING PACKET SPEED

import os, time, random, sys, string, threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- ⚡ QUANTUM CONFIG ---
STRIKE_DELAY = 0.005 # 5ms Ultra-Pulse
PARALLEL_TABS = 3    # 🔥 3 Tabs per Machine (20 machines = 60 agents)

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.page_load_strategy = 'eager'
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    mobile_emulation = { "deviceName": "iPad Pro" }
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=options, service=service)
    return driver

def quantum_dispatch(driver, tab_handle, text, msg_list):
    """V32: Infinite parallel injection loop for a specific tab."""
    driver.switch_to.window(tab_handle)
    while True:
        try:
            salt = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
            payload = f"{random.choice(msg_list)} [{random.randint(1000, 9999)}]-{salt}"
            
            driver.execute_script("""
                const box = document.querySelector('div[role="textbox"], textarea, [contenteditable="true"]');
                if (box) {
                    box.focus();
                    document.execCommand('insertText', false, arguments[0]);
                    box.dispatchEvent(new Event('input', { bubbles: true }));
                    const enter = new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', code: 'Enter', keyCode: 13 });
                    box.dispatchEvent(enter);
                    setTimeout(() => { box.innerHTML = ""; }, 5);
                }
            """, payload)
            sys.stdout.write("⚡")
            sys.stdout.flush()
            time.sleep(STRIKE_DELAY)
        except:
            break

def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target = os.environ.get("TARGET_THREAD_ID")
    msg_list = os.environ.get("MESSAGES").split("|")
    
    driver = get_driver()
    try:
        driver.get("https://www.instagram.com/")
        driver.add_cookie({'name': 'sessionid', 'value': cookie.strip(), 'domain': '.instagram.com'})
        
        # 🚀 SPAWN PARALLEL WORKER TABS
        handles = []
        for i in range(PARALLEL_TABS):
            driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target}/', '_blank');")
            time.sleep(5) # Staggered tab hydration
        
        handles = driver.window_handles[1:] # Skip the home page
        
        threads = []
        for handle in handles:
            t = threading.Thread(target=quantum_dispatch, args=(driver, handle, "", msg_list))
            t.daemon = True
            t.start()
            threads.append(t)

        # Keep main thread alive
        while True:
            time.sleep(10)
            
    except Exception as e:
        print(f"⚠️ QUANTUM ERROR: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
