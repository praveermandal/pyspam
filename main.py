# -*- coding: utf-8 -*-
# 🚀 PHOENIX V100.45 (NUCLEAR REFRESH)
# 🛡️ BY PRAVEERFUCKS | STABLE 24/7 MAX SPEED
# ⚡ FIX: DOM BLOAT RECOVERY | AUTOMATIC MEMORY PURGE

import os, time, random, sys, string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- ⚡ CONFIGURATION ---
TABS_PER_MACHINE = 5  
PURGE_INTERVAL = 120  # 🔥 Hard refresh every 120 seconds to prevent slowdown
STRIKE_SPEED = 15      # 15ms JS Pulse

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.page_load_strategy = 'eager'
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_experimental_option("mobileEmulation", {"deviceName": "iPad Pro"})
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(options=options, service=service)

def deploy_js_engine(driver, target, msg_list):
    """Launches tabs and injects the high-speed JS striker."""
    print(f"🚀 Initializing {TABS_PER_MACHINE} Hyper-Tabs...")
    
    # 1. Open Tabs
    for i in range(TABS_PER_MACHINE):
        driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target}/', '_blank');")
        time.sleep(5) # Hydration stagger

    handles = driver.window_handles[1:]
    
    # 2. Inject Native JS Engine
    for handle in handles:
        driver.switch_to.window(handle)
        driver.execute_script("""
            const messages = arguments[0];
            const pulse = arguments[1];
            
            window.strikeInterval = setInterval(() => {
                const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                if (box) {
                    const rawMsg = messages[Math.floor(Math.random() * messages.length)];
                    const salt = Math.random().toString(36).substring(7);
                    
                    box.focus();
                    document.execCommand('insertText', false, `${rawMsg} [${salt}]`);
                    box.dispatchEvent(new Event('input', { bubbles: true }));

                    const enter = new KeyboardEvent('keydown', {
                        bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                    });
                    box.dispatchEvent(enter);

                    // Instant wipe to stop the 'Loading' spiral
                    setTimeout(() => { box.innerHTML = ""; }, 1);
                }
            }, pulse);
        """, msg_list, STRIKE_SPEED)

def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target = os.environ.get("TARGET_THREAD_ID")
    msg_list = os.environ.get("MESSAGES", "STRIKE|ACTIVE").split("|")
    machine_id = os.environ.get("MACHINE_ID", "1")

    driver = get_driver()
    try:
        # Initial Handshake
        driver.get("https://www.instagram.com/")
        driver.add_cookie({'name': 'sessionid', 'value': cookie.strip(), 'domain': '.instagram.com'})
        
        while True:
            deploy_js_engine(driver, target, msg_list)
            
            print(f"🔥 MACHINE {machine_id}: FIRING AT {STRIKE_SPEED}ms. PURGE IN {PURGE_INTERVAL}s...")
            time.sleep(PURGE_INTERVAL)
            
            # ♻️ THE NUCLEAR PURGE: Close all worker tabs to free RAM
            print("♻️ MEMORY LIMIT REACHED: PURGING DOM BLOAT...")
            all_handles = driver.window_handles
            for i in range(1, len(all_handles)):
                driver.switch_to.window(all_handles[i])
                driver.close()
            
            # Reset back to home and refresh
            driver.switch_to.window(all_handles[0])
            driver.refresh()
            time.sleep(5)

    except Exception as e:
        print(f"⚠️ SYSTEM REBOOT: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
