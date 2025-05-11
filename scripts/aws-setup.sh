#!/bin/bash

# AWS Services Setup Script for SoulCoreHub
# This script creates all necessary AWS services for SoulCoreHub

echo "Setting up AWS services for SoulCoreHub..."

# Set AWS region
REGION="us-east-1"

# Create Cognito User Pool
echo "Creating Cognito User Pool..."
USER_POOL_ID=$(aws cognito-idp create-user-pool \
  --pool-name SoulCoreHub-UserPool \
  --auto-verified-attributes email \
  --schema Name=email,Required=true \
  --policies '{"PasswordPolicy":{"MinimumLength":8,"RequireUppercase":true,"RequireLowercase":true,"RequireNumbers":true,"RequireSymbols":false}}' \
  --region $REGION \
  --query 'UserPool.Id' \
  --output text)

echo "User Pool created with ID: $USER_POOL_ID"

# Create Cognito User Pool Client
echo "Creating Cognito User Pool Client..."
CLIENT_ID=$(aws cognito-idp create-user-pool-client \
  --user-pool-id $USER_POOL_ID \
  --client-name SoulCoreHub-App \
  --generate-secret \
  --allowed-o-auth-flows "implicit" "code" \
  --allowed-o-auth-scopes "phone" "email" "openid" "profile" \
  --allowed-o-auth-flows-user-pool-client \
  --callback-urls "http://localhost:3000/callback" \
  --logout-urls "http://localhost:3000/logout" \
  --region $REGION \
  --query 'UserPoolClient.ClientId' \
  --output text)

echo "User Pool Client created with ID: $CLIENT_ID"

# Create Cognito Identity Pool
echo "Creating Cognito Identity Pool..."
IDENTITY_POOL_ID=$(aws cognito-identity create-identity-pool \
  --identity-pool-name SoulCoreHub-IdentityPool \
  --allow-unauthenticated-identities \
  --cognito-identity-providers ProviderName=cognito-idp.$REGION.amazonaws.com/$USER_POOL_ID,ClientId=$CLIENT_ID,ServerSideTokenCheck=false \
  --region $REGION \
  --query 'IdentityPoolId' \
  --output text)

echo "Identity Pool created with ID: $IDENTITY_POOL_ID"

# Create IAM Role for CodeBuild
echo "Creating IAM Role for CodeBuild..."
aws iam create-role \
  --role-name codebuild-SoulCoreHub-service-role \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"codebuild.amazonaws.com"},"Action":"sts:AssumeRole"}]}' \
  --region $REGION

# Attach policies to the role
aws iam attach-role-policy \
  --role-name codebuild-SoulCoreHub-service-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess \
  --region $REGION

aws iam attach-role-policy \
  --role-name codebuild-SoulCoreHub-service-role \
  --policy-arn arn:aws:iam::aws:policy/AWSCodeBuildAdminAccess \
  --region $REGION

echo "IAM Role created and policies attached"

# Create CodeBuild Project
echo "Creating CodeBuild Project..."
aws codebuild create-project \
  --name SoulCoreHub-Builder \
  --description "Auto-Compiler for SoulCoreHub applications" \
  --service-role arn:aws:iam::$(aws sts get-caller-identity --query 'Account' --output text):role/codebuild-SoulCoreHub-service-role \
  --artifacts type=NO_ARTIFACTS \
  --environment type=LINUX_CONTAINER,image=aws/codebuild/amazonlinux2-x86_64-standard:3.0,computeType=BUILD_GENERAL1_SMALL \
  --source type=GITHUB,location=https://github.com/Sourcesiri-Kamelot/SoulCoreHub.git \
  --region $REGION

echo "CodeBuild Project created"

# Create CodeStar Connection
echo "Creating CodeStar Connection to GitHub..."
CONNECTION_ARN=$(aws codestar-connections create-connection \
  --provider-type GitHub \
  --connection-name SoulCoreHub-GitHub-Connection \
  --region $REGION \
  --query 'ConnectionArn' \
  --output text)

echo "CodeStar Connection created with ARN: $CONNECTION_ARN"
echo "IMPORTANT: You need to complete the connection setup in the AWS Console"

# Test Comprehend
echo "Testing AWS Comprehend..."
aws comprehend detect-sentiment \
  --text "SoulCoreHub is an amazing project with incredible potential!" \
  --language-code en \
  --region $REGION

echo "AWS Comprehend test completed"

echo "AWS services setup completed!"
echo "See aws-services-setup.md for details and next steps"
