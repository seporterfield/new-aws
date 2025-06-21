"""
Test email integration with AWS account creator
"""
from aws_account_creator import AWSAccountCreator
from email_service import EmailServiceIntegration


def test_email_service_standalone():
    """Test email service by itself"""
    print("=== Testing Email Service Standalone ===")
    
    try:
        email_integration = EmailServiceIntegration(debug=True)
        
        # Create temporary email
        email, password = email_integration.setup_temporary_email()
        print(f"✓ Created temporary email: {email}")
        
        # Test message retrieval
        messages = email_integration.email_service.get_messages()
        print(f"✓ Current messages: {len(messages)}")
        
        # Cleanup
        email_integration.cleanup()
        print("✓ Cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Email service test failed: {e}")
        return False


def test_aws_creator_with_email():
    """Test AWS account creator with email integration"""
    print("\n=== Testing AWS Creator with Email Integration ===")
    
    try:
        # Test with temporary email enabled
        creator = AWSAccountCreator(headless=True, debug=True, use_temp_email=True)
        
        # Test configuration loading with email override
        config = creator._load_account_config("sample_account_details.json")
        print(f"✓ Configuration loaded")
        
        # Setup email service
        creator._setup_email_service()
        print(f"✓ Email service setup: {creator.temp_email}")
        
        # Reload config to get email override
        config = creator._load_account_config("sample_account_details.json")
        print(f"✓ Email override: {config['email']}")
        
        # Test driver setup
        creator._setup_driver()
        print("✓ Driver setup successful")
        
        # Test navigation
        if creator._navigate_to_signup():
            print("✓ AWS signup page accessed")
        else:
            print("✗ Failed to access AWS signup page")
        
        # Cleanup
        creator.driver.quit()
        if creator.email_service:
            creator.email_service.cleanup()
        print("✓ Cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"✗ AWS creator email integration test failed: {e}")
        return False


def test_configuration_override():
    """Test that email configuration is properly overridden"""
    print("\n=== Testing Configuration Override ===")
    
    try:
        creator = AWSAccountCreator(headless=True, debug=False, use_temp_email=True)
        
        # Setup email first
        creator._setup_email_service()
        temp_email = creator.temp_email
        
        # Load config
        config = creator._load_account_config("sample_account_details.json")
        
        # Verify email was overridden
        assert config['email'] == temp_email, f"Email not overridden: {config['email']} != {temp_email}"
        print(f"✓ Email override successful: {temp_email}")
        
        # Cleanup
        if creator.email_service:
            creator.email_service.cleanup()
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration override test failed: {e}")
        return False


def main():
    """Run all email integration tests"""
    print("Email Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_email_service_standalone,
        test_aws_creator_with_email,
        test_configuration_override
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("EMAIL INTEGRATION TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All email integration tests passed! CORE-002 ready.")
    else:
        print("✗ Some email integration tests failed.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)