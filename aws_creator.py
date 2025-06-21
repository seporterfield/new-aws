"""
Basic AWS Account Creator
Simple browser automation for AWS registration form filling.
"""
import json
import time
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class AWSAccountCreator:
    """Basic AWS account creation using browser automation"""
    
    def __init__(self, headless: bool = False, debug: bool = False):
        self.headless = headless
        self.debug = debug
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure logging"""
        level = logging.DEBUG if self.debug else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _setup_driver(self):
        """Initialize Chrome driver with stealth configuration"""
        self.logger.info("Setting up Chrome driver")
        
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        
        # Basic stealth configuration
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def load_config(self, config_path: str) -> Dict:
        """Load account configuration from JSON file"""
        self.logger.info(f"Loading configuration from {config_path}")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Validate required fields
        required = ['email', 'password', 'account_name', 'full_name']
        missing = [field for field in required if not config.get(field)]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        return config
    
    def navigate_to_signup(self) -> bool:
        """Navigate to AWS signup page"""
        if not self.driver or not self.wait:
            return False
        
        try:
            self.driver.get("https://portal.aws.amazon.com/billing/signup")
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)  # Wait for JavaScript
            
            title = self.driver.title
            self.logger.info(f"Page loaded: {title}")
            
            return "aws" in title.lower()
            
        except TimeoutException:
            self.logger.error("Timeout loading AWS signup page")
            return False
    
    def fill_basic_fields(self, config: Dict) -> int:
        """Fill basic form fields, return number of fields filled"""
        if not self.driver:
            return 0
        
        fields_filled = 0
        
        # Email field
        email_selectors = ["input[type='email']", "input[name*='email']", "#emailAddress"]
        if self._fill_field(email_selectors, config['email'], "email"):
            fields_filled += 1
        
        # Password field  
        password_selectors = ["input[type='password']", "input[name*='password']"]
        if self._fill_field(password_selectors, config['password'], "password"):
            fields_filled += 1
        
        # Account name
        account_selectors = ["input[name*='account']", "#accountName"]
        if self._fill_field(account_selectors, config['account_name'], "account_name"):
            fields_filled += 1
        
        self.logger.info(f"Filled {fields_filled} form fields")
        return fields_filled
    
    def _fill_field(self, selectors: list, value: str, field_name: str) -> bool:
        """Try multiple selectors to find and fill a field"""
        if not self.driver or not value:
            return False
            
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed() and element.is_enabled():
                    element.clear()
                    element.send_keys(value)
                    self.logger.debug(f"Filled {field_name} with selector: {selector}")
                    return True
            except NoSuchElementException:
                continue
        
        self.logger.warning(f"Could not find field: {field_name}")
        return False
    
    def take_screenshot(self, name: str = "screenshot"):
        """Take screenshot for debugging"""
        if self.driver:
            filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot saved: {filename}")
    
    def create_account(self, config_path: str) -> Tuple[bool, str]:
        """Main method to create AWS account"""
        self.logger.info("Starting AWS account creation")
        
        try:
            config = self.load_config(config_path)
            self._setup_driver()
            
            if not self.navigate_to_signup():
                return False, "Failed to load AWS signup page"
            
            fields_filled = self.fill_basic_fields(config)
            
            if fields_filled > 0:
                if self.debug:
                    self.take_screenshot("form_filled")
                
                return True, f"Form fields filled successfully ({fields_filled} fields)"
            else:
                return False, "No form fields could be filled"
            
        except Exception as e:
            error_msg = f"Account creation failed: {e}"
            self.logger.error(error_msg)
            return False, error_msg
            
        finally:
            if self.driver:
                self.driver.quit()


def main():
    """Command line interface"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python aws_creator.py <config_file.json>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    creator = AWSAccountCreator(headless=False, debug=True)
    
    success, message = creator.create_account(config_path)
    
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")
    print(f"Message: {message}")


if __name__ == "__main__":
    main()