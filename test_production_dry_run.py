"""
Dry run test for production AWS account creator
Tests the basic functionality without actually submitting registration
"""
from aws_account_creator import AWSAccountCreator


def test_config_loading():
    """Test configuration loading and validation"""
    print("=== Testing Configuration Loading ===")
    
    creator = AWSAccountCreator(headless=True, debug=True)
    
    try:
        config = creator._load_account_config("sample_account_details.json")
        print("✓ Configuration loaded successfully")
        print(f"  Email: {config.get('email', 'NOT SET')}")
        print(f"  Account name: {config.get('account_name', 'NOT SET')}")
        print(f"  Full name: {config.get('full_name', 'NOT SET')}")
        return True
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False


def test_driver_setup():
    """Test browser driver setup"""
    print("\n=== Testing Driver Setup ===")
    
    creator = AWSAccountCreator(headless=True, debug=True)
    
    try:
        creator._setup_driver()
        print("✓ Chrome driver setup successful")
        
        # Test basic navigation
        creator.driver.get("https://www.google.com")
        title = creator.driver.title
        print(f"✓ Basic navigation works - Google title: {title}")
        
        creator.driver.quit()
        return True
    except Exception as e:
        print(f"✗ Driver setup failed: {e}")
        if creator.driver:
            creator.driver.quit()
        return False


def test_aws_page_access():
    """Test accessing AWS signup page without form submission"""
    print("\n=== Testing AWS Page Access ===")
    
    creator = AWSAccountCreator(headless=True, debug=True)
    
    try:
        creator._setup_driver()
        
        # Test navigation to AWS signup page
        success = creator._navigate_to_signup()
        
        if success:
            print("✓ AWS signup page accessed successfully")
            title = creator.driver.title
            url = creator.driver.current_url
            print(f"  Page title: {title}")
            print(f"  Final URL: {url}")
            
            # Count form elements without interacting
            inputs = creator.driver.find_elements("tag name", "input")
            buttons = creator.driver.find_elements("tag name", "button")
            print(f"  Found {len(inputs)} input fields and {len(buttons)} buttons")
            
        else:
            print("✗ Failed to access AWS signup page")
        
        creator.driver.quit()
        return success
    except Exception as e:
        print(f"✗ AWS page access failed: {e}")
        if creator.driver:
            creator.driver.quit()
        return False


def main():
    """Run all dry run tests"""
    print("Starting AWS Account Creator Production Dry Run Tests")
    print("=" * 60)
    
    tests = [
        test_config_loading,
        test_driver_setup, 
        test_aws_page_access
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("DRY RUN TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! Production system ready for integration.")
    else:
        print("✗ Some tests failed. Check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)