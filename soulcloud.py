#!/usr/bin/env python3
"""
SoulCloud CLI - AWS SAM integration for SoulCoreHub

This CLI tool provides a simple interface for deploying, testing, and monitoring
SoulCoreHub components in AWS Lambda.
"""

import argparse
import os
import subprocess
import sys
import json
import time
from datetime import datetime

def run_command(command, capture_output=True):
    """Run a shell command and return the result"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, check=True, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                   universal_newlines=True)
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=True, check=True)
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error message: {e.stderr}")
        return None

def deploy_component(component_name):
    """Deploy a specific SoulCore component to AWS Lambda"""
    print(f"🚀 Deploying {component_name} to AWS Lambda...")
    
    # Check if component exists
    if not os.path.exists(f"functions/{component_name}"):
        print(f"❌ Component '{component_name}' not found in functions directory.")
        return False
    
    # Build the SAM application
    print("📦 Building SAM application...")
    run_command("./sam_build.sh", capture_output=False)
    
    # Deploy only the specified component
    print(f"☁️ Deploying {component_name} to AWS...")
    deploy_cmd = f"sam deploy --stack-name soulcore-{component_name} --parameter-overrides ComponentName={component_name}"
    run_command(deploy_cmd, capture_output=False)
    
    print(f"✅ {component_name} deployed successfully!")
    return True

def test_component(component_name):
    """Test a specific SoulCore component locally"""
    print(f"🧪 Testing {component_name} locally...")
    
    # Check if component exists
    if not os.path.exists(f"functions/{component_name}"):
        print(f"❌ Component '{component_name}' not found in functions directory.")
        return False
    
    # Check if event.json exists
    if not os.path.exists(f"functions/{component_name}/event.json"):
        print(f"❌ Event file not found for {component_name}.")
        return False
    
    # Invoke the function locally
    print(f"🔍 Invoking {component_name} with test event...")
    invoke_cmd = f"sam local invoke {component_name.capitalize()}Lambda -e functions/{component_name}/event.json"
    result = run_command(invoke_cmd, capture_output=True)
    
    if result:
        print("\n📋 Function Response:")
        try:
            # Try to parse and pretty-print JSON response
            response_body = json.loads(result)
            if 'body' in response_body:
                body_json = json.loads(response_body['body'])
                print(json.dumps(body_json, indent=2))
            else:
                print(json.dumps(response_body, indent=2))
        except:
            # If not valid JSON, print as is
            print(result)
    
    return True

def get_component_status():
    """Get the status of all deployed SoulCore components"""
    print("📊 Checking status of SoulCore components...")
    
    # List all CloudFormation stacks with the soulcore prefix
    stacks_cmd = "aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --query \"StackSummaries[?contains(StackName, 'soulcore')].StackName\" --output text"
    stacks = run_command(stacks_cmd)
    
    if not stacks:
        print("❌ No SoulCore components found in AWS.")
        return False
    
    stacks = stacks.split()
    print(f"Found {len(stacks)} deployed components:")
    
    for stack in stacks:
        # Get stack resources
        resources_cmd = f"aws cloudformation describe-stack-resources --stack-name {stack} --query \"StackResources[?ResourceType=='AWS::Lambda::Function'].PhysicalResourceId\" --output text"
        functions = run_command(resources_cmd)
        
        if functions:
            functions = functions.split()
            for function in functions:
                # Get function details
                function_cmd = f"aws lambda get-function --function-name {function} --query \"Configuration.{{Name:FunctionName, Runtime:Runtime, Memory:MemorySize, LastModified:LastModified}}\" --output json"
                function_details = run_command(function_cmd)
                
                if function_details:
                    details = json.loads(function_details)
                    print(f"  • {details['Name']}")
                    print(f"    - Runtime: {details['Runtime']}")
                    print(f"    - Memory: {details['Memory']} MB")
                    print(f"    - Last Updated: {details['LastModified']}")
                    print()
    
    return True

def get_component_logs(component_name, tail=False):
    """Get logs for a specific SoulCore component"""
    print(f"📜 Getting logs for {component_name}...")
    
    # Get the Lambda function name
    function_name = f"soulcore-{component_name}-{component_name.capitalize()}Lambda"
    
    # Check if the function exists
    check_cmd = f"aws lambda get-function --function-name {function_name} --query \"Configuration.FunctionName\" --output text"
    function_exists = run_command(check_cmd)
    
    if not function_exists:
        print(f"❌ Function '{function_name}' not found in AWS.")
        return False
    
    # Get the logs
    if tail:
        print(f"📝 Tailing logs for {component_name}... (Press Ctrl+C to stop)")
        logs_cmd = f"aws logs tail /aws/lambda/{function_name} --follow"
        run_command(logs_cmd, capture_output=False)
    else:
        logs_cmd = f"aws logs filter-log-events --log-group-name /aws/lambda/{function_name} --limit 20 --query \"events[].message\" --output text"
        logs = run_command(logs_cmd)
        
        if logs:
            print("\n📋 Recent Logs:")
            print(logs)
        else:
            print("No logs found.")
    
    return True

def main():
    """Main entry point for the SoulCloud CLI"""
    parser = argparse.ArgumentParser(description="SoulCloud CLI - AWS SAM integration for SoulCoreHub")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy a SoulCore component to AWS Lambda")
    deploy_parser.add_argument("component", help="Component to deploy (anima, gptsoul, etc.)")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test a SoulCore component locally")
    test_parser.add_argument("component", help="Component to test (anima, gptsoul, etc.)")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Get the status of all deployed SoulCore components")
    
    # Logs command
    logs_parser = subparsers.add_parser("logs", help="Get logs for a SoulCore component")
    logs_parser.add_argument("component", help="Component to get logs for (anima, gptsoul, etc.)")
    logs_parser.add_argument("--tail", action="store_true", help="Tail the logs in real-time")
    
    args = parser.parse_args()
    
    if args.command == "deploy":
        deploy_component(args.component)
    elif args.command == "test":
        test_component(args.component)
    elif args.command == "status":
        get_component_status()
    elif args.command == "logs":
        get_component_logs(args.component, args.tail)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
