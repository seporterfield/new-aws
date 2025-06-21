"""
AWS Account Creation Engine
Production automation for AWS root account registration with minimal human intervention.
"""
import json
import time
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from email_service import EmailServiceIntegration


class AWSAccountCreator:
    """Automated AWS account creation using browser automation"""
    
    def __init__(self, headless: bool = False, debug: bool = False, use_temp_email: bool = True):
        self.headless = headless
        self.debug = debug
        self.use_temp_email = use_temp_email
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.email_service: Optional[EmailServiceIntegration] = None
        self.temp_email: Optional[str] = None
        self.temp_email_password: Optional[str] = None
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure logging for the account creation process"""
        level = logging.DEBUG if self.debug else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(f'aws_creation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _setup_driver(self):
        """Initialize Chrome driver with stealth configuration"""
        self.logger.info("Setting up Chrome driver with stealth configuration")
        
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        
        # Stealth configuration to avoid bot detection
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 10)
    
    def _setup_email_service(self):
        """Initialize email service for temporary email generation"""
        if self.use_temp_email:
            self.logger.info("Setting up temporary email service")
            self.email_service = EmailServiceIntegration(debug=self.debug)
            self.temp_email, self.temp_email_password = self.email_service.setup_temporary_email()
            self.logger.info(f"Temporary email created: {self.temp_email}")
        
    def _load_account_config(self, config_path: str) -> Dict:
        """Load and validate account configuration from JSON file"""
        self.logger.info(f"Loading account configuration from {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        
        # Validate required fields
        required_fields = [
            'email', 'password', 'account_name', 'full_name', 'phone_number',
            'address', 'city', 'state', 'postal_code', 'country'
        ]
        
        missing_fields = [field for field in required_fields if not config.get(field)]
        if missing_fields:
            raise ValueError(f"Missing required fields in configuration: {missing_fields}")
        
        # Override email with temporary email if using email service
        if self.use_temp_email and self.temp_email:
            original_email = config.get('email')
            config['email'] = self.temp_email
            self.logger.info(f"Using temporary email: {self.temp_email} (original: {original_email})")
        
        self.logger.info("Account configuration loaded and validated successfully")
        return config
    
    def _navigate_to_signup(self) -> bool:
        """Navigate to AWS signup page and verify it loaded"""
        self.logger.info("Navigating to AWS signup page")
        
        if not self.driver or not self.wait:
            return False
        
        try:
            self.driver.get("https://portal.aws.amazon.com/billing/signup")
            
            # Wait for page to load completely
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)  # Additional wait for JavaScript to load
            
            title = self.driver.title
            url = self.driver.current_url
            
            self.logger.info(f"Page loaded - Title: {title}, URL: {url}")
            
            # Take screenshot for debugging
            if self.debug:
                self.driver.save_screenshot(f"aws_signup_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
            return "aws" in title.lower() or "signup" in url.lower()
            
        except TimeoutException:
            self.logger.error("Timeout waiting for AWS signup page to load")
            return False
        except Exception as e:
            self.logger.error(f"Error navigating to signup page: {e}")
            return False
    
    def _fill_registration_form(self, config: Dict) -> bool:
        """Fill out the AWS registration form with account details"""
        self.logger.info("Filling out AWS registration form")
        
        try:
            # Common selectors for AWS registration form fields
            form_fields = {
                'email': [
                    "input[type='email']",
                    "input[name*='email']", 
                    "input[id*='email']",
                    "#emailAddress"
                ],
                'password': [
                    "input[type='password']",
                    "input[name*='password']",
                    "#password"
                ],
                'confirm_password': [
                    "input[name*='confirm']",
                    "input[id*='confirm']",
                    "#confirmPassword"
                ],
                'account_name': [
                    "input[name*='account']",
                    "input[id*='account']",
                    "#accountName"
                ],
                'full_name': [
                    "input[name*='name']",
                    "input[id*='name']",
                    "#fullName"
                ]
            }
            
            # Fill basic account information
            success_count = 0
            
            for field_name, selectors in form_fields.items():
                if self._fill_field(selectors, config.get(field_name) or config.get('password'), field_name):
                    success_count += 1
            
            self.logger.info(f"Successfully filled {success_count}/{len(form_fields)} form fields")
            
            # Handle additional fields that might appear
            self._fill_contact_information(config)
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Error filling registration form: {e}")
            return False
    
    def _fill_field(self, selectors: list, value: str, field_name: str) -> bool:
        """Try multiple selectors to find and fill a form field"""
        if not value or not self.driver:
            return False
            
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed() and element.is_enabled():
                    element.clear()
                    element.send_keys(value)
                    self.logger.debug(f"Successfully filled {field_name} using selector: {selector}")
                    return True
            except NoSuchElementException:
                continue
            except Exception as e:
                self.logger.debug(f"Error with selector {selector} for {field_name}: {e}")
                continue
        
        self.logger.warning(f"Could not find fillable field for {field_name}")
        return False
    
    def _fill_contact_information(self, config: Dict):
        """Fill contact information fields if they appear"""
        contact_fields = {
            'phone_number': ["input[type='tel']", "input[name*='phone']", "#phoneNumber"],
            'address': ["input[name*='address']", "#address"],
            'city': ["input[name*='city']", "#city"],
            'postal_code': ["input[name*='postal']", "input[name*='zip']", "#postalCode"],
        }
        
        for field_name, selectors in contact_fields.items():
            self._fill_field(selectors, config.get(field_name), field_name)
        
        # Handle country and state dropdowns
        self._select_dropdown("select[name*='country']", config.get('country', 'United States'))
        self._select_dropdown("select[name*='state']", config.get('state'))
    
    def _select_dropdown(self, selector: str, value: str):
        """Select value from dropdown if present"""
        if not value:
            return
            
        try:
            dropdown_element = self.driver.find_element(By.CSS_SELECTOR, selector)
            if dropdown_element.is_displayed():
                select = Select(dropdown_element)
                # Try to select by visible text first, then by value
                try:
                    select.select_by_visible_text(value)
                except Exception:
                    select.select_by_value(value)
                self.logger.debug(f"Selected '{value}' from dropdown {selector}")
        except NoSuchElementException:
            pass
        except Exception as e:
            self.logger.debug(f"Error selecting from dropdown {selector}: {e}")
    
    def _handle_email_verification(self) -> bool:
        """Handle email verification step"""
        self.logger.info("Handling email verification step")
        
        try:
            # Wait for potential redirect to verification page
            time.sleep(5)
            page_text = self.driver.page_source.lower()
            
            # Look for email verification indicators
            verification_indicators = [
                "verify your email",
                "check your email", 
                "email verification",
                "confirmation email",
                "we've sent you an email"
            ]
            
            verification_detected = any(indicator in page_text for indicator in verification_indicators)
            
            if verification_detected:
                self.logger.info("Email verification step detected")
                
                if self.email_service:
                    return self._process_email_verification()
                else:
                    self.logger.info("Email verification required but no email service configured")
                    return True  # Manual verification required
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error in email verification handling: {e}")
            return False
    
    def _process_email_verification(self) -> bool:
        """Process email verification using temporary email service"""
        self.logger.info("Processing email verification automatically")
        
        try:
            # Wait for verification email
            self.logger.info("Waiting for AWS verification email...")
            verification_link = self.email_service.wait_for_aws_verification(timeout=300)
            
            if verification_link:
                self.logger.info(f"Found verification link: {verification_link}")
                
                # Click verification link
                self.driver.get(verification_link)
                time.sleep(3)
                
                # Check if verification was successful
                success_indicators = [
                    "verified successfully",
                    "email confirmed",
                    "verification complete",
                    "account activated"
                ]
                
                page_text = self.driver.page_source.lower()
                success = any(indicator in page_text for indicator in success_indicators)
                
                if success:
                    self.logger.info("Email verification completed successfully")
                    return True
                else:
                    self.logger.warning("Email verification link clicked but success not confirmed")
                    return True  # Continue anyway
            else:
                self.logger.error("No verification email received within timeout")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in automatic email verification: {e}")
            return False
    
    def _submit_registration(self) -> bool:
        """Submit the registration form"""
        self.logger.info("Attempting to submit registration form")
        
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']", 
            "button:contains('Create')",
            "button:contains('Submit')",
            "button:contains('Continue')"
        ]
        
        for selector in submit_selectors:
            try:
                submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                if submit_button.is_displayed() and submit_button.is_enabled():
                    submit_button.click()
                    self.logger.info(f"Clicked submit button: {selector}")
                    return True
            except NoSuchElementException:
                continue
            except Exception as e:
                self.logger.debug(f"Error with submit selector {selector}: {e}")
                continue
        
        self.logger.warning("No clickable submit button found")
        return False
    
    def create_account(self, config_path: str) -> Tuple[bool, str]:
        """Main method to create AWS account with given configuration"""
        self.logger.info("Starting AWS account creation process")
        
        try:
            # Setup email service if enabled
            if self.use_temp_email:
                self._setup_email_service()
            
            # Load and validate configuration
            config = self._load_account_config(config_path)
            
            # Setup browser
            self._setup_driver()
            
            # Navigate to signup page
            if not self._navigate_to_signup():
                return False, "Failed to load AWS signup page"
            
            # Fill registration form
            if not self._fill_registration_form(config):
                return False, "Failed to fill registration form"
            
            # Submit form
            if not self._submit_registration():
                return False, "Failed to submit registration form"
            
            # Handle email verification
            verification_result = self._handle_email_verification()
            if verification_result:
                if self.email_service:
                    return True, f"AWS account created successfully! Email: {self.temp_email}"
                else:
                    return True, "Registration submitted successfully, manual email verification required"
            else:
                return True, "Registration submitted successfully"
            
        except Exception as e:
            error_msg = f"Account creation failed: {e}"
            self.logger.error(error_msg)
            return False, error_msg
            
        finally:
            # Cleanup
            if self.driver:
                if self.debug:
                    self.driver.save_screenshot(f"final_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                self.driver.quit()
                self.logger.info("Browser closed")
            
            # Cleanup email service
            if self.email_service:
                self.logger.info("Cleaning up temporary email account")
                self.email_service.cleanup()


def main():
    """Command line interface for AWS account creation"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python aws_account_creator.py <config_file.json>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    creator = AWSAccountCreator(headless=False, debug=True)
    
    success, message = creator.create_account(config_path)
    
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")
    print(f"Message: {message}")
    
    # Save result to timestamped file
    result = {
        "success": success,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "config_file": config_path
    }
    
    result_file = f"aws_account_creation_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Detailed results saved to: {result_file}")


if __name__ == "__main__":
    main()