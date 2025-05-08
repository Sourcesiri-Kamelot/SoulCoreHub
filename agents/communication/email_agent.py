#!/usr/bin/env python3
"""
Email Agent - Sends, receives, and filters emails, alerting the user to important messages and filtering spam.
"""

import logging
import time
import threading
import json
import os
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime

class EmailAgent:
    def __init__(self):
        """Initialize the Email Agent"""
        self.name = "Email Agent"
        self.status = "active"
        self.running = False
        self.config_file = Path("config/email_config.json")
        self.log_file = Path("logs/email_agent.log")
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_file.parent, exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.name)
        
        # Load configuration
        self.config = self.load_config()
        
        # Thread for checking emails
        self._thread = None
        
        self.logger.info(f"{self.name} initialized")
    
    def load_config(self):
        """Load email configuration from file"""
        default_config = {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "imap_server": "imap.example.com",
            "imap_port": 993,
            "username": "user@example.com",
            "password": "password",
            "check_interval": 300,  # 5 minutes
            "spam_keywords": ["viagra", "lottery", "winner", "prince", "inheritance"],
            "important_keywords": ["urgent", "important", "deadline", "meeting"],
            "folders": {
                "inbox": "INBOX",
                "spam": "Spam",
                "important": "Important"
            }
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.logger.info("Loaded email configuration")
                    return config
            else:
                # Create default configuration
                os.makedirs(self.config_file.parent, exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                self.logger.info("Created default email configuration")
                return default_config
        except Exception as e:
            self.logger.error(f"Error loading email configuration: {e}")
            return default_config
    
    def send_email(self, to, subject, body, html=None):
        """
        Send an email
        
        Args:
            to (str): Recipient email address
            subject (str): Email subject
            body (str): Email body (plain text)
            html (str, optional): HTML version of the email body
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config['username']
            msg['To'] = to
            msg['Subject'] = subject
            
            # Attach plain text version
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML version if provided
            if html:
                msg.attach(MIMEText(html, 'html'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['username'], self.config['password'])
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Sent email to {to}: {subject}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return False
    
    def check_emails(self):
        """
        Check for new emails
        
        This method connects to the IMAP server and checks for new emails.
        It filters spam and identifies important messages.
        
        Returns:
            dict: Information about new emails
        """
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.config['imap_server'], self.config['imap_port'])
            mail.login(self.config['username'], self.config['password'])
            mail.select(self.config['folders']['inbox'])
            
            # Search for unread emails
            status, data = mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                self.logger.error("Error searching for emails")
                return {"error": "Error searching for emails"}
            
            # Process emails
            new_emails = []
            spam_emails = []
            important_emails = []
            
            for num in data[0].split():
                # Get email data
                status, data = mail.fetch(num, '(RFC822)')
                
                if status != 'OK':
                    self.logger.error(f"Error fetching email {num}")
                    continue
                
                # Parse email
                msg = email.message_from_bytes(data[0][1])
                
                # Extract information
                sender = msg['From']
                subject = msg['Subject']
                date = msg['Date']
                
                # Get body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()
                
                # Check if it's spam
                is_spam = any(keyword.lower() in body.lower() or keyword.lower() in subject.lower() 
                              for keyword in self.config['spam_keywords'])
                
                # Check if it's important
                is_important = any(keyword.lower() in body.lower() or keyword.lower() in subject.lower() 
                                  for keyword in self.config['important_keywords'])
                
                # Create email info
                email_info = {
                    "id": num.decode(),
                    "sender": sender,
                    "subject": subject,
                    "date": date,
                    "body_preview": body[:100] + "..." if len(body) > 100 else body,
                    "is_spam": is_spam,
                    "is_important": is_important
                }
                
                # Add to appropriate list
                new_emails.append(email_info)
                
                if is_spam:
                    spam_emails.append(email_info)
                    
                    # Move to spam folder
                    mail.copy(num, self.config['folders']['spam'])
                    mail.store(num, '+FLAGS', '\\Deleted')
                
                elif is_important:
                    important_emails.append(email_info)
                    
                    # Move to important folder
                    mail.copy(num, self.config['folders']['important'])
            
            # Expunge deleted messages
            mail.expunge()
            
            # Close connection
            mail.close()
            mail.logout()
            
            # Log results
            self.logger.info(f"Checked emails: {len(new_emails)} new, {len(spam_emails)} spam, {len(important_emails)} important")
            
            return {
                "new_emails": len(new_emails),
                "spam_emails": len(spam_emails),
                "important_emails": len(important_emails),
                "emails": new_emails
            }
        
        except Exception as e:
            self.logger.error(f"Error checking emails: {e}")
            return {"error": str(e)}
    
    def monitor_emails(self):
        """Monitor emails in a background thread"""
        self.logger.info("Starting email monitoring")
        self.running = True
        
        while self.running:
            try:
                # Check emails
                result = self.check_emails()
                
                # If there are important emails, log them
                if "important_emails" in result and result["important_emails"] > 0:
                    self.logger.info(f"Found {result['important_emails']} important emails")
                
                # Sleep until next check
                time.sleep(self.config['check_interval'])
            
            except Exception as e:
                self.logger.error(f"Error in email monitoring: {e}")
                time.sleep(60)  # Sleep for a minute before retrying
    
    def start(self):
        """Start the email monitoring in a background thread"""
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.monitor_emails, daemon=True)
            self._thread.start()
            self.logger.info("Email monitoring started")
            return True
        return False
    
    def stop(self):
        """Stop the email monitoring"""
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
            self.logger.info("Email monitoring stopped")
            return True
        return False
    
    def heartbeat(self):
        """Check if the agent is running properly"""
        if self._thread and self._thread.is_alive():
            self.logger.debug("Heartbeat check: OK")
            return True
        self.logger.warning("Heartbeat check: Failed - thread not running")
        return False
    
    def handle_input(self, prompt):
        """
        Handle user input
        
        Args:
            prompt (str): User input
            
        Returns:
            str: Response to the user
        """
        prompt_lower = prompt.lower()
        
        # Check emails command
        if "check" in prompt_lower and "email" in prompt_lower:
            result = self.check_emails()
            
            if "error" in result:
                return f"⚠️ Error checking emails: {result['error']}"
            
            return (
                f"📬 Email check complete:\n"
                f"• {result['new_emails']} new emails\n"
                f"• {result['spam_emails']} spam emails filtered\n"
                f"• {result['important_emails']} important emails\n\n"
                f"This is a simulation - no actual emails were checked."
            )
        
        # Send email command
        elif "send" in prompt_lower and "email" in prompt_lower:
            # Extract recipient, subject, and body
            # This is a very basic parser - in a real implementation, you'd use NLP
            parts = prompt.split(" to ")
            if len(parts) < 2:
                return "⚠️ Please specify a recipient using 'to'"
            
            recipient_parts = parts[1].split(" subject ")
            if len(recipient_parts) < 2:
                return "⚠️ Please specify a subject using 'subject'"
            
            recipient = recipient_parts[0].strip()
            
            subject_parts = recipient_parts[1].split(" body ")
            if len(subject_parts) < 2:
                return "⚠️ Please specify a body using 'body'"
            
            subject = subject_parts[0].strip()
            body = subject_parts[1].strip()
            
            # Send the email
            success = self.send_email(recipient, subject, body)
            
            if success:
                return f"✅ Email sent to {recipient}: {subject}\n\nThis is a simulation - no actual email was sent."
            else:
                return "⚠️ Error sending email"
        
        # Status command
        elif "status" in prompt_lower:
            return (
                f"📧 Email Agent Status:\n"
                f"• Running: {'Yes' if self.running else 'No'}\n"
                f"• Thread alive: {'Yes' if self._thread and self._thread.is_alive() else 'No'}\n"
                f"• Check interval: {self.config['check_interval']} seconds\n"
                f"• SMTP server: {self.config['smtp_server']}\n"
                f"• IMAP server: {self.config['imap_server']}\n\n"
                f"This is a simulation - no actual email server is connected."
            )
        
        # Help command
        elif "help" in prompt_lower:
            return (
                f"📧 Email Agent Commands:\n"
                f"• check emails - Check for new emails\n"
                f"• send email to <recipient> subject <subject> body <body> - Send an email\n"
                f"• status - Show agent status\n"
                f"• help - Show this help message\n\n"
                f"This is a simulation - no actual emails will be sent or received."
            )
        
        # Unknown command
        else:
            return (
                f"📧 Email Agent here! I can help you manage emails.\n\n"
                f"Try these commands:\n"
                f"• check emails\n"
                f"• send email to someone@example.com subject Hello body This is a test\n"
                f"• status\n"
                f"• help\n\n"
                f"This is a simulation - no actual emails will be sent or received."
            )
    
    def diagnose(self):
        """Return diagnostic information about the agent"""
        return {
            "name": self.name,
            "status": "running" if self.heartbeat() else "stopped",
            "thread_alive": self._thread.is_alive() if self._thread else False,
            "check_interval": self.config['check_interval'],
            "smtp_server": self.config['smtp_server'],
            "imap_server": self.config['imap_server']
        }

# Example usage
if __name__ == "__main__":
    agent = EmailAgent()
    agent.start()
    
    # Example commands
    print(agent.handle_input("check emails"))
    print(agent.handle_input("send email to test@example.com subject Test body This is a test email"))
    print(agent.handle_input("status"))
    
    agent.stop()
