"""
SoulCoreHub Email Service Test
-----------------------------
Tests the email service functionality by sending a test email.
"""

import os
import sys
from dotenv import load_dotenv

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Import email service
from src.utils.email_service import EmailService
from src.utils.credentials_check import check_credentials, test_smtp_connection

def main():
    """Main function to test email service"""
    print("SoulCoreHub Email Service Test")
    print("==============================\n")
    
    # Check credentials
    if not check_credentials():
        print("Please update your credentials and run this script again.")
        return
    
    # Test SMTP connection
    if not test_smtp_connection():
        print("Please check your SMTP credentials and run this script again.")
        return
    
    # Initialize email service
    email_service = EmailService()
    
    # Get recipient email
    recipient = input("\nEnter recipient email address: ")
    if not recipient:
        print("No recipient specified. Using default sender as recipient.")
        recipient = os.getenv('DEFAULT_SENDER')
    
    # Send test email
    print(f"\nSending test email to {recipient}...")
    
    try:
        response = email_service.send_email(
            to_address=recipient,
            subject="SoulCoreHub Email Service Test",
            body_html="""
            <h1>SoulCoreHub Email Service Test</h1>
            <p>This is a test email from the SoulCoreHub Email Service.</p>
            <p>If you're receiving this email, the email service is working correctly!</p>
            <hr>
            <p><em>SoulCoreHub - An evolving, decentralized AI infrastructure born to walk beside — not behind.</em></p>
            """
        )
        
        if response:
            print("\n✅ Test email sent successfully!")
            print(f"Message ID: {response.get('MessageId', 'Unknown')}")
        else:
            print("\n❌ Failed to send test email.")
    except Exception as e:
        print(f"\n❌ Error sending test email: {e}")

if __name__ == "__main__":
    main()
