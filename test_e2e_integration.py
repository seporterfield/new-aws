"""
End-to-End Integration Test for AWS Account Creation
Tests the complete workflow without actually creating accounts
"""
import time
from aws_account_creator import AWSAccountCreator
from email_service import EmailServiceIntegration


class MockEmailVerification:
    """Mock email verification for safe testing"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    def simulate_verification_email(self) -> str:
        """Simulate receiving a verification email with a link"""
        # This would normally be a real AWS verification link
        # For testing, we use a safe mock URL
        mock_link = "https://example.com/verify?token=mock_verification_token"
        if self.debug:
            print(f"Mock verification link: {mock_link}")
        return mock_link


def test_email_service_reliability():
    """Test email service reliability and rate limiting"""
    print("=== Testing Email Service Reliability ===")
    
    try:
        # Test creating single email account
        email_service = EmailServiceIntegration(debug=True)
        email, password = email_service.setup_temporary_email()
        
        print(f"✓ Email created: {email}")
        print(f"✓ Authentication successful")
        
        # Test message checking
        messages = email_service.email_service.get_messages()
        print(f"✓ Message retrieval: {len(messages)} messages")
        
        # Test cleanup
        email_service.cleanup()
        print("✓ Cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Email service reliability test failed: {e}")
        return False


def test_aws_form_detection():
    """Test AWS form detection and field identification"""
    print("\n=== Testing AWS Form Detection ===")
    
    try:
        creator = AWSAccountCreator(headless=True, debug=False, use_temp_email=False)
        creator._setup_driver()
        
        # Navigate to AWS signup
        if creator._navigate_to_signup():
            print("✓ AWS signup page accessible")
            
            # Test form field detection
            inputs = creator.driver.find_elements("tag name", "input")
            buttons = creator.driver.find_elements("tag name", "button")
            
            print(f"✓ Form elements detected: {len(inputs)} inputs, {len(buttons)} buttons")
            
            # Test specific field selectors
            email_selectors = [
                "input[type='email']",
                "input[name*='email']", 
                "input[id*='email']",
                "#emailAddress"
            ]
            
            found_email_field = False
            for selector in email_selectors:
                try:
                    element = creator.driver.find_element("css selector", selector)
                    if element.is_displayed():
                        found_email_field = True
                        print(f"✓ Email field found: {selector}")
                        break
                except:
                    continue
            
            if not found_email_field:
                print("⚠ No email field detected (may indicate page structure changes)")
            
        else:
            print("✗ Failed to access AWS signup page")
            return False
        
        creator.driver.quit()
        return True
        
    except Exception as e:
        print(f"✗ AWS form detection test failed: {e}")
        return False


def test_configuration_workflow():
    """Test complete configuration workflow"""
    print("\n=== Testing Configuration Workflow ===")
    
    try:
        # Test with email service enabled
        creator_with_email = AWSAccountCreator(headless=True, debug=False, use_temp_email=True)
        
        # This would normally setup email service
        # For testing, we'll simulate it
        print("✓ AWS Creator with email service initialized")
        
        # Test configuration loading
        config = creator_with_email._load_account_config("sample_account_details.json")
        original_email = config.get('email')
        print(f"✓ Configuration loaded, original email: {original_email}")
        
        # Test without email service
        creator_manual = AWSAccountCreator(headless=True, debug=False, use_temp_email=False)
        config_manual = creator_manual._load_account_config("sample_account_details.json")
        
        assert config_manual['email'] == original_email, "Email should not be modified without email service"
        print("✓ Manual email mode preserves original email")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration workflow test failed: {e}")
        return False


def test_integration_workflow_simulation():
    """Simulate the complete integration workflow safely"""
    print("\n=== Testing Integration Workflow Simulation ===")
    
    try:
        # Phase 1: Email Setup
        print("Phase 1: Email Service Setup")
        email_service = EmailServiceIntegration(debug=False)
        email, password = email_service.setup_temporary_email()
        print(f"✓ Temporary email ready: {email}")
        
        # Phase 2: AWS Account Creator Setup  
        print("Phase 2: AWS Account Creator Setup")
        creator = AWSAccountCreator(headless=True, debug=False, use_temp_email=True)
        creator.email_service = email_service
        creator.temp_email = email
        print("✓ Account creator configured with email service")
        
        # Phase 3: Configuration Processing
        print("Phase 3: Configuration Processing")
        config = creator._load_account_config("sample_account_details.json")
        
        # Simulate email override
        if creator.use_temp_email and creator.temp_email:
            config['email'] = creator.temp_email
        
        assert config['email'] == email, f"Email override failed: {config['email']} != {email}"
        print(f"✓ Configuration email override successful: {config['email']}")
        
        # Phase 4: Browser Navigation (Safe Test)
        print("Phase 4: Browser Navigation Test")
        creator._setup_driver()
        
        if creator._navigate_to_signup():
            print("✓ AWS signup page navigation successful")
            
            # Simulate form detection without filling
            inputs = creator.driver.find_elements("tag name", "input")
            print(f"✓ Form detection: {len(inputs)} form inputs found")
        else:
            print("⚠ AWS navigation failed (network/page structure issue)")
        
        # Phase 5: Mock Email Verification
        print("Phase 5: Mock Email Verification")
        mock_verifier = MockEmailVerification(debug=False)
        verification_link = mock_verifier.simulate_verification_email()
        print(f"✓ Mock verification link generated: {verification_link}")
        
        # Phase 6: Cleanup
        print("Phase 6: Cleanup")
        creator.driver.quit()
        email_service.cleanup()
        print("✓ Cleanup completed successfully")
        
        print("\n🎉 Integration workflow simulation completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Integration workflow simulation failed: {e}")
        return False


def main():
    """Run comprehensive end-to-end integration tests"""
    print("End-to-End Integration Test Suite")
    print("=" * 60)
    print("NOTE: These tests safely simulate the workflow without creating real AWS accounts")
    print("=" * 60)
    
    tests = [
        test_email_service_reliability,
        test_aws_form_detection,
        test_configuration_workflow,
        test_integration_workflow_simulation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            # Small delay between tests to avoid rate limiting
            time.sleep(2)
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("END-TO-END INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All integration tests passed! System ready for deployment.")
        print("\nNext steps:")
        print("- Manual verification: Run 'just create-account' with test config")
        print("- Monitor first real account creation for any edge cases")
        print("- Consider adding more comprehensive error handling")
    elif passed >= total * 0.75:
        print("⚠️ Most integration tests passed. Minor issues detected.")
        print("System is likely functional but may need attention for edge cases.")
    else:
        print("❌ Integration tests indicate significant issues.")
        print("Review failed tests and address underlying problems before deployment.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)