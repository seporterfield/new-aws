import requests
import json
from bs4 import BeautifulSoup
import re


def test_requests_aws_registration():
    """Test AWS registration page analysis using requests + BeautifulSoup"""
    
    # Create session with realistic headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    try:
        print("Fetching AWS registration page...")
        response = session.get("https://portal.aws.amazon.com/billing/signup", timeout=10)
        
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Save raw HTML for analysis
            with open("aws_page_raw.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
            
            # Find form elements
            forms = soup.find_all('form')
            print(f"Found {len(forms)} forms")
            
            inputs = soup.find_all('input')
            print(f"Found {len(inputs)} input fields")
            
            # Analyze input fields
            for i, input_tag in enumerate(inputs):
                input_type = input_tag.get('type', 'text')
                input_name = input_tag.get('name', 'unnamed')
                input_id = input_tag.get('id', 'no-id')
                placeholder = input_tag.get('placeholder', 'no-placeholder')
                
                print(f"Input {i}: type={input_type}, name={input_name}, id={input_id}, placeholder={placeholder}")
            
            # Look for JavaScript that might handle form submission
            scripts = soup.find_all('script')
            print(f"Found {len(scripts)} script tags")
            
            # Check for React/Angular/Vue patterns
            page_text = response.text
            if 'react' in page_text.lower():
                print("Possible React application detected")
            if 'angular' in page_text.lower():
                print("Possible Angular application detected")
            if 'vue' in page_text.lower():
                print("Possible Vue application detected")
                
            # Look for API endpoints
            api_pattern = r'\/api\/[^\s"\'<>]+'
            apis = re.findall(api_pattern, page_text)
            if apis:
                print(f"Found potential API endpoints: {set(apis)}")
                
        else:
            print(f"Failed to fetch page: {response.status_code}")
            print(f"Response content: {response.text[:500]}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")


def test_requests_aws_with_cookies():
    """Test AWS registration with cookie handling"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    })
    
    try:
        # First, get the main AWS page to establish session
        print("Getting AWS main page...")
        main_response = session.get("https://aws.amazon.com", timeout=10)
        print(f"Main page cookies: {session.cookies}")
        
        # Then try the registration page
        print("Getting registration page with session...")
        reg_response = session.get("https://portal.aws.amazon.com/billing/signup", timeout=10)
        
        print(f"Registration page status: {reg_response.status_code}")
        print(f"Final cookies: {session.cookies}")
        
        if reg_response.status_code == 200:
            soup = BeautifulSoup(reg_response.content, 'html.parser')
            
            # Look for CSRF tokens or similar
            csrf_inputs = soup.find_all('input', {'name': re.compile(r'csrf|token', re.I)})
            if csrf_inputs:
                print("Found CSRF/token inputs:")
                for csrf in csrf_inputs:
                    print(f"  {csrf.get('name')}: {csrf.get('value', 'no-value')}")
            
            # Save processed content
            with open("aws_page_with_session.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
                
    except Exception as e:
        print(f"Session error: {e}")


if __name__ == "__main__":
    test_requests_aws_registration()
    print("\n" + "="*50 + "\n")
    test_requests_aws_with_cookies()