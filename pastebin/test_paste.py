import os
import time
import random
import string
from playwright.sync_api import sync_playwright

def generate_random_string(length=20):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def main():
    random_text = generate_random_string()
    base_url = os.environ.get('BASE_URL', 'http://hackedyour.info')
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"Navigating to {base_url}...")
        page.goto(base_url)
        page.wait_for_load_state('networkidle')
        
        print("Looking for input area with 'Paste here'...")
        textarea = page.locator('textarea').first
        textarea.wait_for(state="visible", timeout=10000)
        
        box = textarea.bounding_box()
        if not box:
            print("Could not find bounding box for the input field.")
            return

        x = box["x"] + box["width"] / 2
        y = box["y"] + box["height"] / 2
        
        print(f"Clicking input area at ({x}, {y})...")
        page.mouse.click(x, y)
        time.sleep(0.5)
        
        print(f"Typing random text: {random_text}")
        page.keyboard.type(random_text)
        time.sleep(1)
        
        print("Looking for save button...")
        save_btn = page.locator('.save.function').first
        save_btn.wait_for(state="visible", timeout=10000)
        btn_box = save_btn.bounding_box()
        
        if not btn_box:
            print("Could not find bounding box for the save button.")
            return
            
        btn_x = btn_box["x"] + btn_box["width"] / 2
        btn_y = btn_box["y"] + btn_box["height"] / 2
        
        print(f"Clicking save button at ({btn_x}, {btn_y})...")
        page.mouse.click(btn_x, btn_y)
        
        # Wait for navigation or URL change
        print("Waiting for URL to change after save...")
        try:
            page.wait_for_function("window.location.pathname.length > 2", timeout=10000)
        except Exception as e:
            print(f"URL did not change: {e}")
            
        time.sleep(2) # Give it an extra moment to settle
        
        new_url = page.url
        print(f"Copied URL after save: {new_url}")
        
        print("Opening URL in a new tab...")
        new_page = context.new_page()
        new_page.goto(new_url)
        new_page.wait_for_load_state('networkidle')
        time.sleep(1) # wait for render
        
        print("Verifying the text appears on the page...")
        # Since the text is placed inside a <pre><code> block after save, we check the innerText of the page.
        # But wait, we must use bounding box or just read text for verification. Reading is fine.
        content = new_page.content()
        body_text = new_page.locator('body').inner_text()
        
        passed = random_text in body_text or random_text in content
        
        if passed:
            print("SUCCESS: Text verification passed.")
        else:
            print("FAILURE: Text was not found on the page.")
            print(f"Page body text snippet: {body_text[:200]}")
        
        browser.close()
        
        print("\n--- SUMMARY ---")
        print("Target URL tested:", new_url)
        print("Steps completed: Navigate, click-to-type, save, copy URL, open in new tab, verify text.")
        print("Result:", "PASS" if passed else "FAIL")

if __name__ == '__main__':
    main()
