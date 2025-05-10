import json
import boto3
import email
import os
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import parseaddr

# Configuration
FORWARD_TO = "kiwonbowens@helo-im.ai"  # Email address to forward to
REGION = "us-east-1"
S3_BUCKET = "heloim-ai-tech-emails"
FROM_EMAIL = "heloimai@heloim-ai.tech"  # The email address to send from

def lambda_handler(event, context):
    """
    Lambda function to forward emails from S3 to a specified email address.
    """
    print("Email forwarding lambda triggered")
    
    # Get the S3 object
    s3_client = boto3.client('s3')
    ses_client = boto3.client('ses', region_name=REGION)
    
    # Get the S3 bucket and object key from the event
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_object_key = event['Records'][0]['s3']['object']['key']
    
    print(f"Processing email from S3 bucket: {s3_bucket}, key: {s3_object_key}")
    
    try:
        # Get the email object from S3
        email_object = s3_client.get_object(Bucket=s3_bucket, Key=s3_object_key)
        email_content = email_object['Body'].read().decode('utf-8')
        
        # Parse the email
        parsed_email = email.message_from_string(email_content)
        
        # Extract email details
        subject = parsed_email.get('Subject', '(No Subject)')
        from_address = parseaddr(parsed_email.get('From', ''))[1]
        to_address = parseaddr(parsed_email.get('To', ''))[1]
        
        print(f"Original email - From: {from_address}, To: {to_address}, Subject: {subject}")
        
        # Create a new email message
        forwarded_message = MIMEMultipart()
        forwarded_message['Subject'] = f"Fwd: {subject}"
        forwarded_message['From'] = FROM_EMAIL
        forwarded_message['To'] = FORWARD_TO
        
        # Add original headers as text
        headers_text = f"From: {from_address}\n"
        headers_text += f"To: {to_address}\n"
        headers_text += f"Subject: {subject}\n"
        headers_text += f"Date: {parsed_email.get('Date', '')}\n\n"
        
        # Add original message body
        if parsed_email.is_multipart():
            for part in parsed_email.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip multipart containers
                if content_type == "multipart/alternative" or content_type == "multipart/mixed":
                    continue
                
                # Handle text parts
                if content_type == "text/plain" or content_type == "text/html":
                    body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                    forwarded_message.attach(MIMEText(headers_text + body, part.get_content_subtype()))
                
                # Handle attachments
                elif "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachment = MIMEApplication(part.get_payload(decode=True))
                        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                        forwarded_message.attach(attachment)
        else:
            # Handle plain text emails
            body = parsed_email.get_payload(decode=True).decode('utf-8', errors='replace')
            forwarded_message.attach(MIMEText(headers_text + body, 'plain'))
        
        # Send the forwarded email
        response = ses_client.send_raw_email(
            Source=FROM_EMAIL,
            Destinations=[FORWARD_TO],
            RawMessage={'Data': forwarded_message.as_string()}
        )
        
        print(f"Email forwarded successfully. Message ID: {response['MessageId']}")
        return {
            'statusCode': 200,
            'body': json.dumps('Email forwarded successfully')
        }
        
    except Exception as e:
        print(f"Error processing email: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing email: {str(e)}')
        }
