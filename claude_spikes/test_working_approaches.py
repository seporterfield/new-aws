"""
Test the working approaches in detail to understand AWS registration form structure
"""
import asyncio
import time
from playwright.async_api import async_playwright
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


async def analyze_with_playwright():
    """Detailed analysis with Playwright"""
    print("=== PLAYWRIGHT ANALYSIS ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            await page.goto("https://portal.aws.amazon.com/billing/signup", timeout=30000)
            await page.wait_for_load_state("networkidle")
            
            print(f"Final URL: {page.url}")
            print(f"Page title: {await page.title()}")
            
            # Find all form elements
            inputs = await page.query_selector_all("input")
            selects = await page.query_selector_all("select")
            buttons = await page.query_selector_all("button")
            textareas = await page.query_selector_all("textarea")
            
            print(f"\nFound {len(inputs)} inputs, {len(selects)} selects, {len(buttons)} buttons, {len(textareas)} textareas")
            
            # Analyze each input field in detail
            print("\n--- INPUT FIELDS ---")
            for i, input_elem in enumerate(inputs):
                input_type = await input_elem.get_attribute("type") or "text"
                input_name = await input_elem.get_attribute("name") or ""
                input_id = await input_elem.get_attribute("id") or ""
                placeholder = await input_elem.get_attribute("placeholder") or ""
                is_visible = await input_elem.is_visible()
                is_enabled = await input_elem.is_enabled()
                
                print(f"Input {i}: type={input_type}, name='{input_name}', id='{input_id}', placeholder='{placeholder}', visible={is_visible}, enabled={is_enabled}")
            
            # Analyze buttons
            print("\n--- BUTTONS ---")
            for i, button in enumerate(buttons):
                text = await button.text_content()
                button_type = await button.get_attribute("type") or ""
                is_visible = await button.is_visible()
                is_enabled = await button.is_enabled()
                
                print(f"Button {i}: text='{text}', type='{button_type}', visible={is_visible}, enabled={is_enabled}")
            
            # Take screenshot
            await page.screenshot(path="playwright_detailed_analysis.png", full_page=True)
            
        finally:
            await browser.close()


def analyze_with_selenium():
    """Detailed analysis with Selenium"""
    print("\n=== SELENIUM ANALYSIS ===")
    
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        driver.get("https://portal.aws.amazon.com/billing/signup")
        
        # Wait for dynamic content
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)  # Additional wait for JavaScript
        
        print(f"Final URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Find all form elements
        inputs = driver.find_elements(By.TAG_NAME, "input")
        selects = driver.find_elements(By.TAG_NAME, "select")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        
        print(f"\nFound {len(inputs)} inputs, {len(selects)} selects, {len(buttons)} buttons, {len(textareas)} textareas")
        
        # Analyze each input field in detail
        print("\n--- INPUT FIELDS ---")
        for i, input_elem in enumerate(inputs):
            try:
                input_type = input_elem.get_attribute("type") or "text"
                input_name = input_elem.get_attribute("name") or ""
                input_id = input_elem.get_attribute("id") or ""
                placeholder = input_elem.get_attribute("placeholder") or ""
                is_displayed = input_elem.is_displayed()
                is_enabled = input_elem.is_enabled()
                
                print(f"Input {i}: type={input_type}, name='{input_name}', id='{input_id}', placeholder='{placeholder}', displayed={is_displayed}, enabled={is_enabled}")
            except Exception as e:
                print(f"Input {i}: Error analyzing - {e}")
        
        # Analyze buttons
        print("\n--- BUTTONS ---")
        for i, button in enumerate(buttons):
            try:
                text = button.text
                button_type = button.get_attribute("type") or ""
                is_displayed = button.is_displayed()
                is_enabled = button.is_enabled()
                
                print(f"Button {i}: text='{text}', type='{button_type}', displayed={is_displayed}, enabled={is_enabled}")
            except Exception as e:
                print(f"Button {i}: Error analyzing - {e}")
        
        # Take screenshot
        driver.save_screenshot("selenium_detailed_analysis.png")
        
        # Look for form containers
        forms = driver.find_elements(By.TAG_NAME, "form")
        divs_with_form_classes = driver.find_elements(By.CSS_SELECTOR, "div[class*='form'], div[class*='Form']")
        
        print(f"\n--- FORM CONTAINERS ---")
        print(f"Found {len(forms)} <form> elements")
        print(f"Found {len(divs_with_form_classes)} divs with form-related classes")
        
    finally:
        driver.quit()


async def test_form_interaction():
    """Test actually interacting with the form"""
    print("\n=== FORM INTERACTION TEST ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        try:
            await page.goto("https://portal.aws.amazon.com/billing/signup", timeout=30000)
            await page.wait_for_load_state("networkidle")
            
            # Try to find and interact with common form fields
            email_selectors = [
                "input[type='email']",
                "input[name*='email']",
                "input[id*='email']",
                "#emailAddress",
                "input[placeholder*='email']"
            ]
            
            for selector in email_selectors:
                try:
                    email_field = await page.query_selector(selector)
                    if email_field and await email_field.is_visible():
                        print(f"Found email field with selector: {selector}")
                        # Test typing (but don't actually submit)
                        await email_field.fill("test@example.com")
                        print("Successfully filled email field")
                        await email_field.clear()
                        break
                except Exception as e:
                    print(f"Email selector {selector} failed: {e}")
            
            await page.screenshot(path="form_interaction_test.png")
            
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(analyze_with_playwright())
    analyze_with_selenium()
    asyncio.run(test_form_interaction())