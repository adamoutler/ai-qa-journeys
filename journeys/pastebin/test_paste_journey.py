import string
import random
from playwright.sync_api import sync_playwright

def generate_random_text(length=20):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def run_test():
    random_text = "test_" + generate_random_text()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        base_url = "http://hackedyour.info"
        print(f"Navigating to {base_url}")
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        
        current_url = page.url
        
        textarea = page.locator('textarea[placeholder*="Paste here"]')
        textarea.wait_for(state="visible")
        box = textarea.bounding_box()
        
        page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        page.keyboard.type(random_text)
        
        save_btn = page.locator('div.save')
        save_btn.wait_for(state="visible")
        save_box = save_btn.bounding_box()
        
        print("Clicking save button")
        # Wait for the post to /documents to finish
        with page.expect_response("**/documents", timeout=10000) as response_info:
            page.mouse.click(save_box["x"] + save_box["width"] / 2, save_box["y"] + save_box["height"] / 2)
            
        response = response_info.value
        print(f"Document saved, status: {response.status}")
        
        # Give it a tiny bit of time to pushState
        page.wait_for_timeout(1000)
            
        new_url = page.url
        print(f"Copied URL at the top of the page: {new_url}")
        
        if new_url == current_url:
            print("Failed to save and get a new URL.")
            # If the url didn't change via pushState, maybe the JSON returned a key we can construct the url with?
            # Wait, let's just fail if the URL isn't updated since that's what the UI is supposed to do.
            return False
            
        print("Opening URL in a new tab...")
        page2 = context.new_page()
        page2.goto(new_url)
        page2.wait_for_load_state("networkidle")
        
        print(f"Verifying text '{random_text}' appears on the page...")
        try:
            page2.locator(f"text={random_text}").wait_for(state="visible", timeout=5000)
            print(f"Verification successful: text '{random_text}' appears on the new page.")
        except Exception as e:
            # Let's see if the text is inside a code block
            code_locator = page2.locator("code")
            if code_locator.count() > 0 and random_text in code_locator.first.inner_text():
                print(f"Verification successful: text '{random_text}' appears on the new page inside code block.")
            elif random_text in page2.content():
                print(f"Verification successful: text '{random_text}' found in page content.")
            else:
                print(f"Verification failed: text '{random_text}' not found.")
                return False
                
        browser.close()
        
    print("\n--- SUMMARY ---")
    print("Test passed successfully.")
    print(f"Resulting URL of the tested journey: {new_url}")

if __name__ == "__main__":
    run_test()