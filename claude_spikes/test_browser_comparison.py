"""
Comparison test runner for different browser automation approaches to AWS registration
"""
import asyncio
import time
import json
from datetime import datetime


class AWSRegistrationTester:
    def __init__(self):
        self.results = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def log_result(self, method, success, details, duration=None):
        """Log test results for comparison"""
        self.results[method] = {
            "success": success,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        print(f"\n{method}: {'SUCCESS' if success else 'FAILED'}")
        print(f"Details: {details}")
        if duration:
            print(f"Duration: {duration:.2f}s")
    
    async def test_playwright_approach(self):
        """Test Playwright approach"""
        start_time = time.time()
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto("https://portal.aws.amazon.com/billing/signup", timeout=30000)
                await page.wait_for_load_state("networkidle", timeout=10000)
                
                title = await page.title()
                inputs = await page.query_selector_all("input")
                
                await browser.close()
                
                duration = time.time() - start_time
                self.log_result("Playwright", True, 
                              f"Page loaded, title: {title}, found {len(inputs)} inputs", 
                              duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Playwright", False, str(e), duration)
    
    def test_selenium_approach(self):
        """Test Selenium approach"""
        start_time = time.time()
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=options)
            
            driver.get("https://portal.aws.amazon.com/billing/signup")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            title = driver.title
            inputs = driver.find_elements(By.TAG_NAME, "input")
            
            driver.quit()
            
            duration = time.time() - start_time
            self.log_result("Selenium", True, 
                          f"Page loaded, title: {title}, found {len(inputs)} inputs", 
                          duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Selenium", False, str(e), duration)
    
    def test_requests_approach(self):
        """Test requests + BeautifulSoup approach"""
        start_time = time.time()
        try:
            import requests
            from bs4 import BeautifulSoup
            
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            response = session.get("https://portal.aws.amazon.com/billing/signup", timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                inputs = soup.find_all('input')
                forms = soup.find_all('form')
                
                duration = time.time() - start_time
                self.log_result("Requests+BeautifulSoup", True, 
                              f"Status: {response.status_code}, found {len(inputs)} inputs, {len(forms)} forms", 
                              duration)
            else:
                duration = time.time() - start_time
                self.log_result("Requests+BeautifulSoup", False, 
                              f"HTTP {response.status_code}: {response.text[:100]}", 
                              duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Requests+BeautifulSoup", False, str(e), duration)
    
    async def test_skyvern_approach(self):
        """Test Skyvern approach"""
        start_time = time.time()
        try:
            from skyvern import Skyvern
            
            skyvern = Skyvern()
            task = await skyvern.run_task(
                url="https://portal.aws.amazon.com/billing/signup",
                prompt="Load the AWS registration page and count the number of input fields"
            )
            
            duration = time.time() - start_time
            success = task is not None and (not hasattr(task, 'status') or task.status in ['completed', 'success'])
            
            self.log_result("Skyvern", success, 
                          f"Task completed: {task}", 
                          duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Skyvern", False, str(e), duration)
    
    async def run_all_tests(self):
        """Run all approaches and compare results"""
        print("=== AWS Registration Page Access Comparison ===")
        print(f"Test started at: {datetime.now()}")
        
        # Test each approach
        print("\n1. Testing Playwright...")
        await self.test_playwright_approach()
        
        print("\n2. Testing Selenium...")
        self.test_selenium_approach()
        
        print("\n3. Testing Requests + BeautifulSoup...")
        self.test_requests_approach()
        
        print("\n4. Testing Skyvern...")
        await self.test_skyvern_approach()
        
        # Save results
        self.save_results()
        self.print_summary()
    
    def save_results(self):
        """Save test results to file"""
        filename = f"aws_test_results_{self.timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: {filename}")
    
    def print_summary(self):
        """Print comparison summary"""
        print("\n=== SUMMARY ===")
        successful = [method for method, result in self.results.items() if result['success']]
        failed = [method for method, result in self.results.items() if not result['success']]
        
        print(f"Successful approaches: {len(successful)}")
        for method in successful:
            duration = self.results[method].get('duration', 0)
            print(f"  ✓ {method} ({duration:.2f}s)")
        
        print(f"\nFailed approaches: {len(failed)}")
        for method in failed:
            print(f"  ✗ {method}")
        
        if successful:
            fastest = min(successful, key=lambda m: self.results[m].get('duration', float('inf')))
            print(f"\nFastest successful approach: {fastest} ({self.results[fastest].get('duration', 0):.2f}s)")


async def main():
    tester = AWSRegistrationTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())