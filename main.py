# -*- coding: utf-8 -*-
# 🚀 PROJECT: PHOENIX V100.30 (HYPER-DRIVE)
# 🛡️ CREDITS: PRAVEERFUCKS | ULTRA-MATRIX OPTIMIZED
# ⚡ SPEED: 0.01s PULSE | LEXICAL STATE INJECTION | EAGER LOAD

import os, time, random, sys, tempfile, string, json, subprocess, atexit
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- ⚡ HYPER-DRIVE CONFIG ---
STRIKE_DELAY = 0.01  # 🔥 10ms micro-pulse for maximum speed
CONFIG_FILE = "phoenix_vault.json"

def get_driver(agent_id):
    options = Options()
    options.add_argument("--headless=new")
    
    # 🏎️ EAGER LOAD: Tells Chrome to ignore images/ads and only load the DM box
    options.page_load_strategy = 'eager'
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--js-flags='--max-old-space-size=512'")
    
    # 📱 IPAD PRO EMULATION (STABLE)
    mobile_emulation = { "deviceName": "iPad Pro" }
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=options, service=service)
    return driver

def hyper_pulse(driver, text):
    """V30: Injects message into React/Lexical memory and fires instantly."""
    try:
        salt = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
        final_text = f"{text} [{random.randint(1000, 9999)}]-{salt}"
        
        driver.execute_script("""
            const box = document.querySelector('div[role="textbox"], textarea, [contenteditable="true"]');
            if (box) {
                box.focus();
                // 1. Clear & Inject
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, arguments[0]);
                
                // 2. Hydrate React State
                box.dispatchEvent(new Event('input', { bubbles: true }));

                // 3. Hardware-Level Enter Event (Bypasses 'Send' button rendering)
                const enter = new KeyboardEvent('keydown', {
                    bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                });
                box.dispatchEvent(enter);
                
                // 4. Cleanup for next pulse
                box.innerHTML = "";
            }
        """, final_text)
        return True
    except: return False

def main():
    # Load Environment Variables for GitHub Matrix or Local Manual
    cookie = os.environ.get("INSTA_COOKIE")
    target = os.environ.get("TARGET_THREAD_ID")
    messages_raw = os.environ.get("MESSAGES")
    
    # Fallback to local config if Env is empty
    if not cookie and os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            conf = json.load(f)
            cookie, target, messages_raw = conf['c'], conf['t'], conf['m']

    if not cookie:
        print("❌ ERROR: No Credentials Found.")
        return

    msg_list = messages_raw.split("|")
    agent_id = os.environ.get("MACHINE_ID", "1")
    
    print(f"🚀 HYPER-DRIVE ARMED | MACHINE {agent_id} | TARGET: {target}")
    
    driver = get_driver(agent_id)
    try:
        driver.get(f"https://www.instagram.com/direct/t/{target}/")
        driver.add_cookie({'name': 'sessionid', 'value': cookie.strip(), 'domain': '.instagram.com'})
        driver.refresh()
        
        time.sleep(10) # Initial handshake
        
        while True:
            if hyper_pulse(driver, random.choice(msg_list)):
                sys.stdout.write("🚀")
                sys.stdout.flush()
            time.sleep(STRIKE_DELAY)
            
            # Periodic Refresh to prevent 'DOM Ghosting'
            if random.random() < 0.05: # 5% chance every strike
                driver.refresh()
                time.sleep(5)
    except Exception as e:
        print(f"\n⚠️ REBOOTING AGENT: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
