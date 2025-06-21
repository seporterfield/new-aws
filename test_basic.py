"""
Basic tests for AWS account creator
"""
from aws_creator import AWSAccountCreator


def test_config_loading():
    """Test configuration loading"""
    creator = AWSAccountCreator()
    
    try:
        config = creator.load_config("sample_config.json")
        assert config['email'] == "your-email@example.com"
        assert config['account_name'] == "My AWS Account"
        print("✓ Configuration loading test passed")
        return True
    except Exception as e:
        print(f"✗ Configuration loading test failed: {e}")
        return False


def test_driver_setup():
    """Test browser driver setup"""
    creator = AWSAccountCreator(headless=True)
    
    try:
        creator._setup_driver()
        assert creator.driver is not None
        assert creator.wait is not None
        
        # Test basic navigation
        creator.driver.get("https://www.google.com")
        title = creator.driver.title
        creator.driver.quit()
        
        assert "Google" in title
        print("✓ Driver setup test passed")
        return True
    except Exception as e:
        print(f"✗ Driver setup test failed: {e}")
        return False


def main():
    """Run basic tests"""
    print("Running basic tests...")
    
    tests = [test_config_loading, test_driver_setup]
    results = [test() for test in tests]
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)