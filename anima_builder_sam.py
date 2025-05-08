#!/usr/bin/env python3
"""
Anima Builder SAM Integration
This module extends Anima's builder capabilities with AWS SAM integration
"""

import os
import sys
import json
import argparse
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/anima_builder_sam.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("anima_builder_sam")

class AnimaBuilderSAM:
    """Anima Builder SAM Integration class for managing AWS SAM deployments"""
    
    def __init__(self):
        """Initialize the AnimaBuilderSAM class"""
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.functions_dir = os.path.join(self.project_root, "functions")
        self.template_path = os.path.join(self.project_root, "template.yaml")
        
        # Ensure functions directory exists
        if not os.path.exists(self.functions_dir):
            os.makedirs(self.functions_dir)
    
    def run_command(self, command, capture_output=False):
        """Run a shell command and return the result"""
        try:
            if capture_output:
                result = subprocess.run(command, shell=True, check=True, 
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       universal_newlines=True)
                return result.stdout.strip()
            else:
                subprocess.run(command, shell=True, check=True)
                return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {command}")
            logger.error(f"Error: {str(e)}")
            if capture_output:
                logger.error(f"STDOUT: {e.stdout}")
                logger.error(f"STDERR: {e.stderr}")
            return False
    
    def init_sam_project(self):
        """Initialize a new SAM project"""
        logger.info("Initializing new SAM project")
        return self.run_command("./scripts/sam_script_runner.sh init")
    
    def build_sam_project(self):
        """Build the SAM project"""
        logger.info("Building SAM project")
        return self.run_command("./scripts/sam_script_runner.sh build")
    
    def deploy_sam_project(self):
        """Deploy the SAM project to AWS"""
        logger.info("Deploying SAM project to AWS")
        return self.run_command("./scripts/sam_script_runner.sh deploy")
    
    def run_local(self):
        """Run the SAM project locally"""
        logger.info("Running SAM project locally")
        return self.run_command("./scripts/sam_script_runner.sh local")
    
    def view_logs(self, function_name):
        """View logs for a specific Lambda function"""
        logger.info(f"Viewing logs for function: {function_name}")
        return self.run_command(f"./scripts/sam_script_runner.sh logs {function_name}")
    
    def validate_template(self):
        """Validate the SAM template"""
        logger.info("Validating SAM template")
        return self.run_command("./scripts/sam_script_runner.sh validate")
    
    def record_stripe_usage(self, user_id, units, reason=None):
        """Record Stripe usage for a user"""
        cmd = f"./scripts/sam_script_runner.sh stripe user_id={user_id} units={units}"
        if reason:
            cmd += f" reason={reason}"
        
        logger.info(f"Recording Stripe usage: {units} units for user {user_id}")
        return self.run_command(cmd)
    
    def add_stripe_billing_to_template(self):
        """Add Stripe billing function to the SAM template"""
        logger.info("Adding Stripe billing function to SAM template")
        
        try:
            # Check if template exists
            if not os.path.exists(self.template_path):
                logger.error("template.yaml not found")
                return False
            
            # Read the template
            with open(self.template_path, 'r') as f:
                template_content = f.read()
            
            # Check if StripeBillingLambda already exists
            if "StripeBillingLambda:" in template_content:
                logger.info("StripeBillingLambda already exists in template")
                return True
            
            # Find the Resources section
            resources_pos = template_content.find("Resources:")
            if resources_pos == -1:
                logger.error("Resources section not found in template")
                return False
            
            # Add StripeBillingLambda to the template
            stripe_lambda = """
  # StripeBillingLambda - handles Stripe metered billing
  StripeBillingLambda:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: functions/stripe_billing/
      Handler: app.lambda_handler
      Runtime: python3.9
      MemorySize: 128
      Timeout: 10
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref SubscriptionsTable
        - DynamoDBCrudPolicy:
            TableName: !Ref UsageTable
      Environment:
        Variables:
          STAGE: !Ref Stage
          SUBSCRIPTIONS_TABLE: !Ref SubscriptionsTable
          USAGE_TABLE: !Ref UsageTable
      Events:
        RecordUsageApi:
          Type: Api
          Properties:
            RestApiId: !Ref SoulCoreApi
            Path: /billing/record-usage
            Method: post
        VerifySubscriptionApi:
          Type: Api
          Properties:
            RestApiId: !Ref SoulCoreApi
            Path: /billing/verify-subscription
            Method: post
        GetSubscriptionApi:
          Type: Api
          Properties:
            RestApiId: !Ref SoulCoreApi
            Path: /billing/subscription
            Method: get
"""
            
            # Find a good position to insert the new Lambda function
            # Look for the last Lambda function definition
            last_lambda_pos = template_content.rfind("Lambda:")
            if last_lambda_pos == -1:
                # If no Lambda function found, insert at the end of Resources section
                insert_pos = template_content.find("Outputs:")
                if insert_pos == -1:
                    # If no Outputs section, append to the end
                    insert_pos = len(template_content)
            else:
                # Find the next section after the last Lambda
                next_section_pos = template_content.find("  ", last_lambda_pos + 7)
                if next_section_pos == -1:
                    # If no next section, insert at the end of Resources section
                    insert_pos = template_content.find("Outputs:")
                    if insert_pos == -1:
                        # If no Outputs section, append to the end
                        insert_pos = len(template_content)
                else:
                    insert_pos = next_section_pos
            
            # Insert the StripeBillingLambda
            new_template = template_content[:insert_pos] + stripe_lambda + template_content[insert_pos:]
            
            # Add to Outputs section
            outputs_pos = new_template.find("Outputs:")
            if outputs_pos != -1:
                # Find the end of Outputs section
                outputs_end_pos = new_template.find("\n\n", outputs_pos)
                if outputs_end_pos == -1:
                    outputs_end_pos = len(new_template)
                
                stripe_output = """
  StripeBillingLambda:
    Description: "Stripe Billing Lambda Function ARN"
    Value: !GetAtt StripeBillingLambda.Arn
"""
                new_template = new_template[:outputs_end_pos] + stripe_output + new_template[outputs_end_pos:]
            
            # Write the updated template
            with open(self.template_path, 'w') as f:
                f.write(new_template)
            
            logger.info("Successfully added StripeBillingLambda to template")
            return True
            
        except Exception as e:
            logger.error(f"Error adding Stripe billing to template: {str(e)}")
            return False
    
    def create_lambda_chaining(self):
        """Create Lambda → S3 → DynamoDB → EventBridge chaining"""
        logger.info("Creating Lambda chaining template")
        
        # Create a directory for the chaining example
        chaining_dir = os.path.join(self.functions_dir, "lambda_chaining")
        os.makedirs(chaining_dir, exist_ok=True)
        
        # Create app.py
        app_py = """import json
import boto3
import os
import uuid
from datetime import datetime

# Initialize clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
events = boto3.client('events')

# Get environment variables
bucket_name = os.environ.get('STORAGE_BUCKET')
table_name = os.environ.get('DATA_TABLE')
event_bus_name = os.environ.get('EVENT_BUS', 'default')

# Initialize DynamoDB table
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    """Lambda handler that demonstrates chaining with S3, DynamoDB, and EventBridge"""
    
    try:
        # Parse input
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
        
        # Generate unique ID
        item_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Add metadata
        body['id'] = item_id
        body['timestamp'] = timestamp
        body['source'] = 'lambda_chaining'
        
        # Step 1: Save to S3
        s3_key = f"data/{item_id}.json"
        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json.dumps(body),
            ContentType='application/json'
        )
        
        # Step 2: Save to DynamoDB
        table.put_item(
            Item={
                'id': item_id,
                'timestamp': timestamp,
                'data': body,
                's3_location': f"s3://{bucket_name}/{s3_key}"
            }
        )
        
        # Step 3: Send event to EventBridge
        events.put_events(
            Entries=[
                {
                    'Source': 'soulcore.lambda.chaining',
                    'DetailType': 'DataProcessed',
                    'Detail': json.dumps({
                        'id': item_id,
                        'timestamp': timestamp,
                        's3_location': f"s3://{bucket_name}/{s3_key}",
                        'status': 'completed'
                    }),
                    'EventBusName': event_bus_name
                }
            ]
        )
        
        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Processing completed successfully',
                'id': item_id,
                's3_location': f"s3://{bucket_name}/{s3_key}"
            })
        }
        
    except Exception as e:
        # Log error and return error response
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
"""
        
        # Create requirements.txt
        requirements_txt = """boto3==1.28.38
"""
        
        # Write the files
        with open(os.path.join(chaining_dir, "app.py"), 'w') as f:
            f.write(app_py)
        
        with open(os.path.join(chaining_dir, "requirements.txt"), 'w') as f:
            f.write(requirements_txt)
        
        logger.info("Created Lambda chaining example in functions/lambda_chaining")
        return True

def main():
    """Main function to parse arguments and execute commands"""
    parser = argparse.ArgumentParser(description="Anima Builder SAM Integration")
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # init command
    init_parser = subparsers.add_parser("init", help="Initialize a new SAM project")
    
    # build command
    build_parser = subparsers.add_parser("build", help="Build the SAM project")
    
    # deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy the SAM project to AWS")
    
    # local command
    local_parser = subparsers.add_parser("local", help="Run the SAM project locally")
    
    # logs command
    logs_parser = subparsers.add_parser("logs", help="View logs for a specific Lambda function")
    logs_parser.add_argument("function_name", help="Name of the Lambda function")
    
    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate the SAM template")
    
    # stripe command
    stripe_parser = subparsers.add_parser("stripe", help="Record Stripe usage for a user")
    stripe_parser.add_argument("--user_id", required=True, help="User ID")
    stripe_parser.add_argument("--units", type=int, default=1, help="Number of units to record")
    stripe_parser.add_argument("--reason", help="Reason for the usage")
    
    # add-stripe command
    add_stripe_parser = subparsers.add_parser("add-stripe", help="Add Stripe billing function to the SAM template")
    
    # create-chaining command
    create_chaining_parser = subparsers.add_parser("create-chaining", help="Create Lambda chaining example")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create AnimaBuilderSAM instance
    builder = AnimaBuilderSAM()
    
    # Execute the appropriate command
    if args.command == "init":
        builder.init_sam_project()
    elif args.command == "build":
        builder.build_sam_project()
    elif args.command == "deploy":
        builder.deploy_sam_project()
    elif args.command == "local":
        builder.run_local()
    elif args.command == "logs":
        builder.view_logs(args.function_name)
    elif args.command == "validate":
        builder.validate_template()
    elif args.command == "stripe":
        builder.record_stripe_usage(args.user_id, args.units, args.reason)
    elif args.command == "add-stripe":
        builder.add_stripe_billing_to_template()
    elif args.command == "create-chaining":
        builder.create_lambda_chaining()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
