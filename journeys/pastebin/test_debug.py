import string
import random
import time
from playwright.sync_api import sync_playwright

def generate_random_text(length=20):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def run_test():
    random_text = "test_" + generate_random_text()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # log responses
        page.on("response", lambda response: print(f"Response: {response.url} {response.status}"))
        
        base_url = "http://hackedyour.info"
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        
        current_url = page.url
        print(f"Landed on: {current_url}")
        
        textarea = page.locator('textarea[placeholder*="Paste here"]')
        textarea.wait_for(state="visible")
        box = textarea.bounding_box()
        page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        page.keyboard.type(random_text)
        
        # Click save button
        save_btn = page.locator('div.save')
        save_btn.wait_for(state="visible")
        save_box = save_btn.bounding_box()
        print(f"Save button box: {save_box}")
        
        # Ensure we actually click the center
        page.mouse.click(save_box["x"] + save_box["width"] / 2, save_box["y"] + save_box["height"] / 2)
        
        for _ in range(20):
            if page.url != current_url:
                break
            time.sleep(0.5)
            
        print(f"URL: {page.url}")
        browser.close()

if __name__ == "__main__":
    run_test()