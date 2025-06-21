"""
Email Service Integration
Temporary email generation and verification using mail.tm API for AWS account creation.
"""
import time
import requests
import logging
from typing import List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class EmailMessage:
    """Email message data structure"""
    id: str
    sender: str
    subject: str
    content: str
    received_at: str


class MailTMEmailService:
    """Mail.tm temporary email service integration"""
    
    def __init__(self, debug: bool = False):
        self.base_url = "https://api.mail.tm"
        self.session = requests.Session()
        self.debug = debug
        self.account_token: Optional[str] = None
        self.email_address: Optional[str] = None
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging for email service"""
        level = logging.DEBUG if self.debug else logging.INFO
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(level)
    
    def get_available_domains(self) -> List[str]:
        """Get list of available email domains from mail.tm"""
        self.logger.info("Fetching available email domains")
        
        try:
            response = self.session.get(f"{self.base_url}/domains")
            response.raise_for_status()
            
            domains_data = response.json()
            domains = [domain['domain'] for domain in domains_data['hydra:member']]
            
            self.logger.info(f"Available domains: {domains}")
            return domains
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch domains: {e}")
            raise
    
    def create_temporary_email(self, username: Optional[str] = None) -> Tuple[str, str]:
        """Create a temporary email account and return (email, password)"""
        self.logger.info("Creating temporary email account")
        
        try:
            # Get available domains
            domains = self.get_available_domains()
            if not domains:
                raise ValueError("No available email domains")
            
            # Use first available domain
            domain = domains[0]
            
            # Generate username if not provided
            if not username:
                import uuid
                username = f"aws_{str(uuid.uuid4())[:8]}"
            
            email_address = f"{username}@{domain}"
            password = f"TempPass_{int(time.time())}"
            
            # Create account
            account_data = {
                "address": email_address,
                "password": password
            }
            
            response = self.session.post(f"{self.base_url}/accounts", json=account_data)
            response.raise_for_status()
            
            self.email_address = email_address
            
            self.logger.info(f"Created temporary email: {email_address}")
            return email_address, password
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to create email account: {e}")
            raise
    
    def authenticate(self, email: str, password: str) -> str:
        """Authenticate with mail.tm and get access token"""
        self.logger.info(f"Authenticating email account: {email}")
        
        try:
            auth_data = {
                "address": email,
                "password": password
            }
            
            response = self.session.post(f"{self.base_url}/token", json=auth_data)
            response.raise_for_status()
            
            token_data = response.json()
            self.account_token = token_data['token']
            
            # Set authorization header for future requests
            self.session.headers.update({
                'Authorization': f'Bearer {self.account_token}'
            })
            
            self.logger.info("Authentication successful")
            return self.account_token
            
        except requests.RequestException as e:
            self.logger.error(f"Authentication failed: {e}")
            raise
    
    def get_messages(self, limit: int = 100) -> List[EmailMessage]:
        """Get list of received email messages"""
        if not self.account_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        self.logger.debug("Fetching email messages")
        
        try:
            params = {'page': 1}
            response = self.session.get(f"{self.base_url}/messages", params=params)
            response.raise_for_status()
            
            messages_data = response.json()
            messages = []
            
            for msg_data in messages_data.get('hydra:member', []):
                message = EmailMessage(
                    id=msg_data['id'],
                    sender=msg_data['from']['address'],
                    subject=msg_data['subject'],
                    content=self._get_message_content(msg_data['id']),
                    received_at=msg_data['createdAt']
                )
                messages.append(message)
            
            self.logger.info(f"Retrieved {len(messages)} messages")
            return messages
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to get messages: {e}")
            raise
    
    def _get_message_content(self, message_id: str) -> str:
        """Get the content of a specific message"""
        try:
            response = self.session.get(f"{self.base_url}/messages/{message_id}")
            response.raise_for_status()
            
            message_data = response.json()
            # Return text content if available, otherwise HTML
            return message_data.get('text', message_data.get('html', ''))
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to get message content: {e}")
            return ""
    
    def wait_for_email_containing(self, keywords: List[str], timeout: int = 300, poll_interval: int = 10) -> Optional[EmailMessage]:
        """Wait for an email containing specific keywords"""
        self.logger.info(f"Waiting for email containing keywords: {keywords}")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                messages = self.get_messages()
                
                for message in messages:
                    # Check if any keyword is in subject or content
                    text_to_search = f"{message.subject} {message.content}".lower()
                    
                    if any(keyword.lower() in text_to_search for keyword in keywords):
                        self.logger.info(f"Found matching email: {message.subject}")
                        return message
                
                self.logger.debug(f"No matching email found, waiting {poll_interval}s...")
                time.sleep(poll_interval)
                
            except Exception as e:
                self.logger.error(f"Error while checking for emails: {e}")
                time.sleep(poll_interval)
        
        self.logger.warning(f"Timeout waiting for email with keywords: {keywords}")
        return None
    
    def extract_verification_link(self, message: EmailMessage) -> Optional[str]:
        """Extract verification link from email content"""
        import re
        
        # Common patterns for verification links
        patterns = [
            r'https?://[^\s]+verify[^\s]*',
            r'https?://[^\s]+confirm[^\s]*',
            r'https?://[^\s]+activate[^\s]*',
            r'https?://signin\.aws\.amazon\.com[^\s]*'
        ]
        
        content = f"{message.subject} {message.content}"
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                link = matches[0].rstrip('.,;)')  # Clean up trailing punctuation
                self.logger.info(f"Found verification link: {link}")
                return link
        
        self.logger.warning("No verification link found in email")
        return None
    
    def delete_account(self) -> bool:
        """Delete the temporary email account"""
        if not self.account_token or not self.email_address:
            return True
        
        self.logger.info(f"Deleting temporary email account: {self.email_address}")
        
        try:
            # Get account ID first
            response = self.session.get(f"{self.base_url}/me")
            response.raise_for_status()
            account_data = response.json()
            account_id = account_data['id']
            
            # Delete account
            response = self.session.delete(f"{self.base_url}/accounts/{account_id}")
            response.raise_for_status()
            
            self.logger.info("Email account deleted successfully")
            return True
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to delete account: {e}")
            return False


class EmailServiceIntegration:
    """High-level email service integration for AWS account creation"""
    
    def __init__(self, debug: bool = False):
        self.email_service = MailTMEmailService(debug=debug)
        self.logger = logging.getLogger(__name__)
    
    def setup_temporary_email(self) -> Tuple[str, str]:
        """Setup temporary email for AWS registration"""
        email, password = self.email_service.create_temporary_email()
        self.email_service.authenticate(email, password)
        return email, password
    
    def wait_for_aws_verification(self, timeout: int = 600) -> Optional[str]:
        """Wait for AWS verification email and extract verification link"""
        keywords = [
            "AWS", "Amazon", "verify", "confirm", "activation", 
            "welcome", "account", "email verification"
        ]
        
        message = self.email_service.wait_for_email_containing(keywords, timeout)
        
        if message:
            return self.email_service.extract_verification_link(message)
        
        return None
    
    def cleanup(self):
        """Clean up temporary email account"""
        self.email_service.delete_account()


def main():
    """Test the email service integration"""
    print("Testing Mail.tm Email Service Integration")
    print("=" * 50)
    
    try:
        # Test basic functionality
        email_service = EmailServiceIntegration(debug=True)
        
        print("1. Creating temporary email...")
        email, password = email_service.setup_temporary_email()
        print(f"   Created: {email}")
        
        print("2. Testing message retrieval...")
        messages = email_service.email_service.get_messages()
        print(f"   Current messages: {len(messages)}")
        
        print("3. Email service ready for AWS integration")
        print(f"   Use email: {email}")
        print(f"   Use password: {password}")
        
        # Cleanup
        print("4. Cleaning up...")
        email_service.cleanup()
        print("   Cleanup complete")
        
        print("\n✓ Email service integration test successful!")
        
    except Exception as e:
        print(f"✗ Email service test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)