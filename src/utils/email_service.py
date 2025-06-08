"""
SoulCoreHub Email Service Module
--------------------------------
Provides email functionality for SoulCoreHub agents including:
- Sending marketing emails at scale
- Retrieving inbound emails from S3
- Email forwarding and routing
- Email analytics and tracking
"""

import os
import boto3
import json
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailService:
    def __init__(self):
        """Initialize the email service with AWS credentials from environment"""
        # SES client for sending emails
        self.ses_client = boto3.client(
            'ses',
            region_name='us-east-1',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # S3 client for accessing stored emails
        self.s3_client = boto3.client(
            's3',
            region_name='us-east-1',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # SNS client for notifications
        self.sns_client = boto3.client(
            'sns',
            region_name='us-east-1',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # Email configuration
        self.smtp_server = "email-smtp.us-east-1.amazonaws.com"
        self.smtp_port = 587
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.email_bucket = "soulcorehub-email-storage"
        self.default_sender = "heloimai@heloim-ai.tech"
        
    def send_email(self, to_address, subject, body_html, body_text=None, 
                  from_address=None, reply_to=None, attachments=None):
        """
        Send a single email using AWS SES
        
        Args:
            to_address (str or list): Recipient email address(es)
            subject (str): Email subject
            body_html (str): HTML content of the email
            body_text (str, optional): Plain text content of the email
            from_address (str, optional): Sender email address
            reply_to (str, optional): Reply-to email address
            attachments (dict, optional): Dict of filename:content pairs
            
        Returns:
            dict: Response from AWS SES
        """
        if from_address is None:
            from_address = self.default_sender
            
        if reply_to is None:
            reply_to = from_address
            
        if body_text is None:
            # Create a simple text version from HTML
            body_text = body_html.replace('<br>', '\n').replace('</p>', '\n\n')
            # Remove all other HTML tags
            import re
            body_text = re.sub('<[^<]+?>', '', body_text)
            
        # Create message container
        msg = MIMEMultipart('mixed')
        msg['Subject'] = subject
        msg['From'] = from_address
        msg['To'] = to_address if isinstance(to_address, str) else ", ".join(to_address)
        msg['Reply-To'] = reply_to
        
        # Create message alternative part
        msg_alt = MIMEMultipart('alternative')
        
        # Create text part
        text_part = MIMEText(body_text, 'plain', 'utf-8')
        msg_alt.attach(text_part)
        
        # Create HTML part
        html_part = MIMEText(body_html, 'html', 'utf-8')
        msg_alt.attach(html_part)
        
        # Attach parts to message
        msg.attach(msg_alt)
        
        # Attach any attachments
        if attachments:
            for filename, content in attachments.items():
                attachment = MIMEApplication(content)
                attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                msg.attach(attachment)
        
        try:
            # Try to send the email
            response = self.ses_client.send_raw_email(
                Source=from_address,
                Destinations=[to_address] if isinstance(to_address, str) else to_address,
                RawMessage={'Data': msg.as_string()}
            )
            return response
        except ClientError as e:
            print(f"Error sending email: {e}")
            self._alert_failure("send_email", str(e))
            return None
            
    def send_bulk_emails(self, recipients, subject, body_html, body_text=None, 
                        from_address=None, reply_to=None, batch_size=50):
        """
        Send emails to a large list of recipients in batches
        
        Args:
            recipients (list): List of recipient email addresses
            subject (str): Email subject
            body_html (str): HTML content of the email
            body_text (str, optional): Plain text content of the email
            from_address (str, optional): Sender email address
            reply_to (str, optional): Reply-to email address
            batch_size (int, optional): Number of emails to send in each batch
            
        Returns:
            dict: Summary of sending results
        """
        if from_address is None:
            from_address = self.default_sender
            
        if reply_to is None:
            reply_to = from_address
            
        results = {
            'total': len(recipients),
            'sent': 0,
            'failed': 0,
            'failures': []
        }
        
        # Process recipients in batches
        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i+batch_size]
            
            try:
                # Create message template
                template_data = {
                    'html_part': body_html,
                    'text_part': body_text if body_text else body_html.replace('<br>', '\n')
                }
                
                # Send batch
                response = self.ses_client.send_bulk_templated_email(
                    Source=from_address,
                    Template='SoulCoreHubTemplate',  # Template must be created in SES console
                    DefaultTemplateData=json.dumps(template_data),
                    Destinations=[
                        {
                            'Destination': {'ToAddresses': [recipient]},
                            'ReplacementTemplateData': json.dumps({'recipient': recipient})
                        } for recipient in batch
                    ]
                )
                
                # Process response
                for status in response['Status']:
                    if 'Error' in status:
                        results['failed'] += 1
                        results['failures'].append({
                            'email': status['Destination']['ToAddresses'][0],
                            'error': status['Error']
                        })
                    else:
                        results['sent'] += 1
                        
            except ClientError as e:
                print(f"Error sending bulk email batch: {e}")
                self._alert_failure("send_bulk_emails", str(e))
                results['failed'] += len(batch)
                results['failures'].append({
                    'batch': batch,
                    'error': str(e)
                })
                
        return results
    
    def get_new_emails(self, folder_prefix=None, max_count=100, mark_as_read=True):
        """
        Retrieve new emails from S3 storage
        
        Args:
            folder_prefix (str, optional): Folder prefix to filter emails
            max_count (int, optional): Maximum number of emails to retrieve
            mark_as_read (bool, optional): Whether to mark emails as read
            
        Returns:
            list: List of email objects
        """
        try:
            # List objects in the S3 bucket
            prefix = folder_prefix if folder_prefix else ""
            response = self.s3_client.list_objects_v2(
                Bucket=self.email_bucket,
                Prefix=prefix,
                MaxKeys=max_count
            )
            
            if 'Contents' not in response:
                return []
                
            emails = []
            for obj in response['Contents']:
                # Get the email object
                email_obj = self.s3_client.get_object(
                    Bucket=self.email_bucket,
                    Key=obj['Key']
                )
                
                # Parse the email
                email_content = email_obj['Body'].read()
                msg = email.message_from_bytes(email_content)
                
                # Extract email data
                email_data = {
                    'message_id': msg.get('Message-ID', ''),
                    'date': msg.get('Date', ''),
                    'from': msg.get('From', ''),
                    'to': msg.get('To', ''),
                    'subject': msg.get('Subject', ''),
                    'body': self._get_email_body(msg),
                    'attachments': self._get_email_attachments(msg),
                    's3_key': obj['Key']
                }
                
                emails.append(email_data)
                
                # Mark as read if requested
                if mark_as_read:
                    # Move to a "read" folder
                    new_key = obj['Key'].replace(prefix, f"{prefix}/read/")
                    self.s3_client.copy_object(
                        Bucket=self.email_bucket,
                        CopySource={'Bucket': self.email_bucket, 'Key': obj['Key']},
                        Key=new_key
                    )
                    self.s3_client.delete_object(
                        Bucket=self.email_bucket,
                        Key=obj['Key']
                    )
                    
            return emails
            
        except ClientError as e:
            print(f"Error retrieving emails: {e}")
            self._alert_failure("get_new_emails", str(e))
            return []
    
    def forward_email(self, email_key, to_address):
        """
        Forward an email from S3 to another address
        
        Args:
            email_key (str): S3 key of the email to forward
            to_address (str): Recipient email address
            
        Returns:
            bool: Success status
        """
        try:
            # Get the email object
            email_obj = self.s3_client.get_object(
                Bucket=self.email_bucket,
                Key=email_key
            )
            
            # Parse the email
            email_content = email_obj['Body'].read()
            msg = email.message_from_bytes(email_content)
            
            # Create a new message for forwarding
            forward_msg = MIMEMultipart('mixed')
            forward_msg['Subject'] = f"Fwd: {msg.get('Subject', '')}"
            forward_msg['From'] = self.default_sender
            forward_msg['To'] = to_address
            
            # Add forwarding header
            forward_text = f"""
            ---------- Forwarded message ---------
            From: {msg.get('From', '')}
            Date: {msg.get('Date', '')}
            Subject: {msg.get('Subject', '')}
            To: {msg.get('To', '')}
            
            """
            
            # Get the email body
            body = self._get_email_body(msg)
            
            # Create text part
            text_part = MIMEText(forward_text + body['text'], 'plain', 'utf-8')
            forward_msg.attach(text_part)
            
            # Add HTML part if available
            if body['html']:
                html_part = MIMEText(
                    f"<div style='border-left: 1px solid #ccc; padding-left: 10px; margin-left: 10px;'>"
                    f"<p><b>From:</b> {msg.get('From', '')}<br>"
                    f"<b>Date:</b> {msg.get('Date', '')}<br>"
                    f"<b>Subject:</b> {msg.get('Subject', '')}<br>"
                    f"<b>To:</b> {msg.get('To', '')}</p>"
                    f"{body['html']}</div>",
                    'html', 'utf-8'
                )
                forward_msg.attach(html_part)
            
            # Add attachments
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                    
                filename = part.get_filename()
                if filename:
                    attachment = MIMEApplication(part.get_payload(decode=True))
                    attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                    forward_msg.attach(attachment)
            
            # Send the forwarded email
            response = self.ses_client.send_raw_email(
                Source=self.default_sender,
                Destinations=[to_address],
                RawMessage={'Data': forward_msg.as_string()}
            )
            
            return True
            
        except ClientError as e:
            print(f"Error forwarding email: {e}")
            self._alert_failure("forward_email", str(e))
            return False
    
    def setup_email_forwarding(self, source_email, destination_email):
        """
        Set up email forwarding rule
        
        Args:
            source_email (str): Email address to forward from
            destination_email (str): Email address to forward to
            
        Returns:
            bool: Success status
        """
        try:
            # Create a receipt rule for forwarding
            rule_name = f"Forward{source_email.split('@')[0].capitalize()}"
            
            # Check if rule already exists
            try:
                self.ses_client.describe_receipt_rule(
                    RuleSetName="SoulCoreHubEmailRules",
                    RuleName=rule_name
                )
                # Rule exists, update it
                response = self.ses_client.update_receipt_rule(
                    RuleSetName="SoulCoreHubEmailRules",
                    Rule={
                        'Name': rule_name,
                        'Enabled': True,
                        'Recipients': [source_email],
                        'Actions': [
                            {
                                'S3Action': {
                                    'BucketName': self.email_bucket,
                                    'ObjectKeyPrefix': f"{source_email.split('@')[0]}/"
                                }
                            },
                            {
                                'SNSAction': {
                                    'TopicArn': 'arn:aws:sns:us-east-1:699475940746:email-forwarding',
                                    'Encoding': 'UTF-8'
                                }
                            }
                        ],
                        'TlsPolicy': 'Optional'
                    }
                )
            except ClientError:
                # Rule doesn't exist, create it
                response = self.ses_client.create_receipt_rule(
                    RuleSetName="SoulCoreHubEmailRules",
                    Rule={
                        'Name': rule_name,
                        'Enabled': True,
                        'Recipients': [source_email],
                        'Actions': [
                            {
                                'S3Action': {
                                    'BucketName': self.email_bucket,
                                    'ObjectKeyPrefix': f"{source_email.split('@')[0]}/"
                                }
                            },
                            {
                                'SNSAction': {
                                    'TopicArn': 'arn:aws:sns:us-east-1:699475940746:email-forwarding',
                                    'Encoding': 'UTF-8'
                                }
                            }
                        ],
                        'TlsPolicy': 'Optional'
                    }
                )
                
            # Subscribe the destination email to the SNS topic
            self.sns_client.subscribe(
                TopicArn='arn:aws:sns:us-east-1:699475940746:email-forwarding',
                Protocol='email',
                Endpoint=destination_email
            )
            
            return True
            
        except ClientError as e:
            print(f"Error setting up email forwarding: {e}")
            self._alert_failure("setup_email_forwarding", str(e))
            return False
    
    def track_email_metrics(self, campaign_id, metrics):
        """
        Store email campaign metrics in S3
        
        Args:
            campaign_id (str): Unique identifier for the campaign
            metrics (dict): Metrics data to store
            
        Returns:
            bool: Success status
        """
        try:
            # Store metrics in S3
            self.s3_client.put_object(
                Bucket=os.getenv('MEMORY_BUCKET'),
                Key=f"email_metrics/{campaign_id}.json",
                Body=json.dumps(metrics),
                ContentType='application/json'
            )
            
            return True
            
        except ClientError as e:
            print(f"Error storing email metrics: {e}")
            self._alert_failure("track_email_metrics", str(e))
            return False
    
    def _get_email_body(self, msg):
        """Extract text and HTML body from email message"""
        body = {'text': '', 'html': ''}
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition'))
                
                # Skip attachments
                if 'attachment' in content_disposition:
                    continue
                    
                if content_type == 'text/plain':
                    body['text'] = part.get_payload(decode=True).decode()
                elif content_type == 'text/html':
                    body['html'] = part.get_payload(decode=True).decode()
        else:
            # Not multipart - get the content type and payload
            content_type = msg.get_content_type()
            if content_type == 'text/plain':
                body['text'] = msg.get_payload(decode=True).decode()
            elif content_type == 'text/html':
                body['html'] = msg.get_payload(decode=True).decode()
                
        return body
    
    def _get_email_attachments(self, msg):
        """Extract attachments from email message"""
        attachments = []
        
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
                
            filename = part.get_filename()
            if filename:
                attachments.append({
                    'filename': filename,
                    'content_type': part.get_content_type(),
                    'size': len(part.get_payload(decode=True))
                })
                
        return attachments
    
    def _alert_failure(self, function_name, error_message):
        """Send alert for email service failures"""
        try:
            # Send SNS notification
            self.sns_client.publish(
                TopicArn='arn:aws:sns:us-east-1:699475940746:email-forwarding',
                Subject=f"SoulCoreHub Email Service Failure: {function_name}",
                Message=f"An error occurred in the SoulCoreHub Email Service:\n\n"
                        f"Function: {function_name}\n"
                        f"Error: {error_message}\n\n"
                        f"Please check the system logs for more details."
            )
        except Exception as e:
            print(f"Error sending failure alert: {e}")


# Example usage
if __name__ == "__main__":
    email_service = EmailService()
    
    # Send a test email
    response = email_service.send_email(
        to_address="heloimai@heloim-ai.tech",
        subject="Test Email from SoulCoreHub",
        body_html="<h1>Hello from SoulCoreHub!</h1><p>This is a test email.</p>"
    )
    
    print(f"Email sent: {response}")
