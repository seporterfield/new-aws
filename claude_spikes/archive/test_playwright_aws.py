import asyncio
import pytest
from playwright.async_api import async_playwright


@pytest.mark.asyncio
async def test_playwright_aws_registration():
    """Test AWS registration page access using Playwright"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("Navigating to AWS registration page...")
        await page.goto("https://portal.aws.amazon.com/billing/signup")
        
        # Wait for page to load
        await page.wait_for_load_state("networkidle")
        
        # Take screenshot for debugging
        await page.screenshot(path="aws_registration_page.png")
        
        # Check if we reached the registration page
        title = await page.title()
        print(f"Page title: {title}")
        
        # Look for common registration elements
        email_input = await page.query_selector("input[type='email']")
        if email_input:
            print("Found email input field")
        
        password_input = await page.query_selector("input[type='password']")
        if password_input:
            print("Found password input field")
            
        await browser.close()
        
        assert "aws" in title.lower() or "amazon" in title.lower()


@pytest.mark.asyncio
async def test_playwright_aws_with_form_detection():
    """Test AWS registration with form field detection"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        # Set user agent to avoid bot detection
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        
        try:
            await page.goto("https://portal.aws.amazon.com/billing/signup", wait_until="networkidle")
            
            # Wait for form elements to appear
            await page.wait_for_selector("form", timeout=10000)
            
            # Find all input fields
            inputs = await page.query_selector_all("input")
            print(f"Found {len(inputs)} input fields")
            
            for i, input_elem in enumerate(inputs):
                input_type = await input_elem.get_attribute("type")
                input_name = await input_elem.get_attribute("name")
                input_id = await input_elem.get_attribute("id")
                placeholder = await input_elem.get_attribute("placeholder")
                
                print(f"Input {i}: type={input_type}, name={input_name}, id={input_id}, placeholder={placeholder}")
            
            await page.screenshot(path="aws_form_analysis.png")
            
        except Exception as e:
            print(f"Error: {e}")
            await page.screenshot(path="aws_error.png")
            
        finally:
            await browser.close()