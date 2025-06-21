import asyncio
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def test_selenium_aws_registration():
    """Test AWS registration page access using Selenium"""
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("Navigating to AWS registration page...")
        driver.get("https://portal.aws.amazon.com/billing/signup")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Take screenshot
        driver.save_screenshot("selenium_aws_page.png")
        
        # Look for registration form elements
        try:
            email_field = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
            print("Found email field")
        except NoSuchElementException:
            print("No email field found")
            
        try:
            password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            print("Found password field")
        except NoSuchElementException:
            print("No password field found")
            
        # Find all input elements
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"Found {len(inputs)} input elements")
        
        for i, input_elem in enumerate(inputs):
            input_type = input_elem.get_attribute("type")
            input_name = input_elem.get_attribute("name")
            input_id = input_elem.get_attribute("id")
            placeholder = input_elem.get_attribute("placeholder")
            
            print(f"Input {i}: type={input_type}, name={input_name}, id={input_id}, placeholder={placeholder}")
            
        time.sleep(2)  # Give time to observe
        
    except Exception as e:
        print(f"Error occurred: {e}")
        driver.save_screenshot("selenium_error.png")
        
    finally:
        driver.quit()


def test_selenium_aws_with_stealth():
    """Test AWS registration with stealth techniques"""
    from selenium_stealth import stealth
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Apply stealth techniques
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
    )
    
    try:
        driver.get("https://portal.aws.amazon.com/billing/signup")
        
        # Wait longer for complex page
        time.sleep(5)
        
        print(f"Stealth - Page title: {driver.title}")
        print(f"Stealth - Current URL: {driver.current_url}")
        
        driver.save_screenshot("selenium_stealth_aws.png")
        
        # Check for CAPTCHA or bot detection
        page_source = driver.page_source.lower()
        if "captcha" in page_source or "bot" in page_source:
            print("Possible bot detection or CAPTCHA detected")
        else:
            print("No obvious bot detection")
            
    except Exception as e:
        print(f"Stealth error: {e}")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    test_selenium_aws_registration()
    # test_selenium_aws_with_stealth()  # Uncomment if selenium-stealth is installed