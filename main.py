# -*- coding: utf-8 -*-
# 🚀 PROJECT: PHOENIX V100.31 (DIRECT-DISPATCH)
# 🛡️ CREDITS: PRAVEERFUCKS | 24/7 ULTRA-MATRIX
# ⚡ FIX: DOM LOADING LAG | REACT STATE PURGE | AUTO-MEMORY RECOVERY

import os, time, random, sys, string, json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- ⚡ SPEED CONFIG ---
STRIKE_DELAY = 0.01  # 10ms Pulse
REFRESH_INTERVAL = 120 # Auto-refresh every 2 mins to clear DOM lag

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.page_load_strategy = 'eager' # Don't wait for images
    
    # Block heavy assets to keep GitHub RAM free
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # iPad Pro Emulation for stable DOM
    mobile_emulation = { "deviceName": "iPad Pro" }
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    # Automatic driver management
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=options, service=service)
    return driver

def direct_dispatch(driver, text):
    """V31: Force-injects text and purges the React state instantly."""
    try:
        salt = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
        final_text = f"{text} [{random.randint(1000, 9999)}]-{salt}"
        
        driver.execute_script("""
            const box = document.querySelector('div[role="textbox"], textarea, [contenteditable="true"]');
            if (box) {
                box.focus();
                
                // 1. Native Injection (Fastest Method)
                document.execCommand('insertText', false, arguments[0]);
                
                // 2. Trigger Input Event for React
                box.dispatchEvent(new Event('input', { bubbles: true }));

                // 3. Hardware-Level Enter (Zero-Lag)
                const enter = new KeyboardEvent('keydown', {
                    bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                });
                box.dispatchEvent(enter);
                
                // 4. 🔥 THE DOM PURGE: Kills the loading circle immediately
                setTimeout(() => {
                    box.innerHTML = "";
                    box.innerText = "";
                    if(box.value) box.value = "";
                }, 5); 
            }
        """, final_text)
        return True
    except: return False

def main():
    # Fetch credentials from GitHub Secrets
    cookie = os.environ.get("INSTA_COOKIE")
    target = os.environ.get("TARGET_THREAD_ID")
    messages_raw = os.environ.get("MESSAGES")
    
    if not cookie or not target:
        print("❌ CRITICAL: Missing Env Variables (Secrets).")
        return

    msg_list = messages_raw.split("|")
    machine_id = os.environ.get("MACHINE_ID", "1")
    
    print(f"🚀 PHOENIX V100.31 ACTIVE | MACHINE {machine_id}")
    
    driver = get_driver()
    try:
        driver.get(f"https://www.instagram.com/direct/t/{target}/")
        driver.add_cookie({'name': 'sessionid', 'value': cookie.strip(), 'domain': '.instagram.com'})
        driver.refresh()
        
        time.sleep(12) # Wait for initial DOM hydration
        
        start_time = time.time()
        while True:
            # Check if it's time to refresh memory
            if time.time() - start_time > REFRESH_INTERVAL:
                print(f"\n♻️ RECOVERING MEMORY (MACHINE {machine_id})...")
                driver.refresh()
                time.sleep(10)
                start_time = time.time()

            if direct_dispatch(driver, random.choice(msg_list)):
                sys.stdout.write("🚀")
                sys.stdout.flush()
            
            time.sleep(STRIKE_DELAY)
            
    except Exception as e:
        print(f"\n⚠️ REBOOTING AGENT: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
