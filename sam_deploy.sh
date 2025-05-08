#!/bin/bash

# SoulCoreHub SAM Deploy Script
# This script deploys the SAM application to AWS

echo "🧠 SoulCoreHub SAM Deploy"
echo "========================"

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI is not installed. Please install it first."
    echo "   Visit: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html"
    exit 1
fi

# Check if the .aws-sam directory exists (created by sam build)
if [ ! -d ".aws-sam" ]; then
    echo "❌ Build artifacts not found. Please run './sam_build.sh' first."
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "📄 Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Get AWS region from config or prompt user
AWS_REGION=${AWS_DEFAULT_REGION:-$(aws configure get region)}
if [ -z "$AWS_REGION" ]; then
    read -p "Enter AWS region (e.g., us-east-1): " AWS_REGION
    if [ -z "$AWS_REGION" ]; then
        echo "❌ AWS region is required."
        exit 1
    fi
fi

# Create a unique S3 bucket name for deployment if not specified
if [ -z "$DEPLOYMENT_BUCKET" ]; then
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    DEPLOYMENT_BUCKET="soulcore-deployment-${ACCOUNT_ID}-${AWS_REGION}"
    
    # Check if bucket exists, create if it doesn't
    if ! aws s3api head-bucket --bucket "$DEPLOYMENT_BUCKET" 2>/dev/null; then
        echo "🪣 Creating deployment bucket: $DEPLOYMENT_BUCKET"
        aws s3 mb "s3://$DEPLOYMENT_BUCKET" --region "$AWS_REGION"
        
        if [ $? -ne 0 ]; then
            echo "❌ Failed to create deployment bucket."
            exit 1
        fi
    fi
fi

# Check if we have a certificate ARN for custom domain
CERTIFICATE_ARN=""
DOMAIN_NAME=${DOMAIN_NAME:-"soulcore.heloim-ai.tech"}

# Check if we want to set up a custom domain
read -p "Do you want to set up a custom domain ($DOMAIN_NAME)? (y/n): " setup_domain
if [[ "$setup_domain" == "y" || "$setup_domain" == "Y" ]]; then
    # List certificates to see if we have one for the domain
    echo "📜 Checking for existing certificates..."
    CERTIFICATES=$(aws acm list-certificates --region us-east-1 --query "CertificateSummaryList[?contains(DomainName, '$DOMAIN_NAME')].CertificateArn" --output text)
    
    if [ -n "$CERTIFICATES" ]; then
        echo "✅ Found existing certificate for $DOMAIN_NAME"
        CERTIFICATE_ARN=$CERTIFICATES
    else
        echo "❌ No certificate found for $DOMAIN_NAME"
        echo "You'll need to create a certificate in ACM for your domain."
        echo "Visit: https://console.aws.amazon.com/acm/home?region=us-east-1#/certificates/request"
        echo ""
        read -p "Would you like to continue deployment without custom domain? (y/n): " continue_without_domain
        if [[ "$continue_without_domain" != "y" && "$continue_without_domain" != "Y" ]]; then
            echo "Deployment cancelled."
            exit 1
        fi
    fi
fi

echo "🚀 Deploying SoulCoreHub to AWS..."
echo "  Region: $AWS_REGION"
echo "  Deployment Bucket: $DEPLOYMENT_BUCKET"
if [ -n "$CERTIFICATE_ARN" ]; then
    echo "  Domain: $DOMAIN_NAME"
    echo "  Certificate ARN: $CERTIFICATE_ARN"
fi
echo ""

# Set up deployment parameters
DEPLOY_PARAMS="--region $AWS_REGION --s3-bucket $DEPLOYMENT_BUCKET --stack-name soulcore-hub"

if [ -n "$CERTIFICATE_ARN" ]; then
    DEPLOY_PARAMS="$DEPLOY_PARAMS --parameter-overrides DomainName=$DOMAIN_NAME CertificateArn=$CERTIFICATE_ARN"
fi

# Run SAM deploy with guided mode for first-time deployment
if [ ! -f "samconfig.toml" ]; then
    echo "📝 Running guided deployment for first-time setup..."
    sam deploy --guided $DEPLOY_PARAMS
else
    echo "📝 Using existing configuration from samconfig.toml..."
    sam deploy $DEPLOY_PARAMS
fi

if [ $? -eq 0 ]; then
    echo "✅ Deployment completed successfully!"
    
    # Get the API Gateway URL
    API_URL=$(aws cloudformation describe-stacks --stack-name soulcore-hub --query "Stacks[0].Outputs[?OutputKey=='SoulCoreApi'].OutputValue" --output text --region "$AWS_REGION")
    
    if [ ! -z "$API_URL" ]; then
        echo ""
        echo "🌐 SoulCore API is now available at: $API_URL"
        echo "🖥️ SoulCore Dashboard is available at: $API_URL"
        
        # If we have a custom domain, show that too
        if [ -n "$CERTIFICATE_ARN" ]; then
            CUSTOM_URL=$(aws cloudformation describe-stacks --stack-name soulcore-hub --query "Stacks[0].Outputs[?OutputKey=='CustomDomainUrl'].OutputValue" --output text --region "$AWS_REGION")
            if [ ! -z "$CUSTOM_URL" ]; then
                echo "🌐 Custom domain URL: $CUSTOM_URL"
                echo ""
                echo "⚠️ IMPORTANT: You need to create a DNS record for your domain:"
                echo "  - Create a CNAME record for $DOMAIN_NAME"
                echo "  - Point it to the API Gateway domain (see AWS Console)"
            fi
        fi
        
        # Save the API URL to .env file
        if [ -f ".env" ]; then
            if grep -q "API_ENDPOINT" .env; then
                sed -i '' "s|API_ENDPOINT=.*|API_ENDPOINT=$API_URL|g" .env
            else
                echo "API_ENDPOINT=$API_URL" >> .env
            fi
        else
            echo "API_ENDPOINT=$API_URL" > .env
        fi
    fi
else
    echo "❌ Deployment failed. Please check the errors above."
fi
