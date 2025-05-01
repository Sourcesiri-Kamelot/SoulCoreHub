#!/bin/bash
# prepare_aws_deployment.sh - Prepare SoulCoreHub for AWS deployment

echo "🚀 Preparing SoulCoreHub for AWS Deployment"
echo "=========================================="

# Set the base directory
BASE_DIR="$HOME/SoulCoreHub"
cd "$BASE_DIR" || { echo "❌ Could not change to SoulCoreHub directory"; exit 1; }

# Create logs directory if it doesn't exist
mkdir -p "$BASE_DIR/logs"
DEPLOY_LOG="$BASE_DIR/logs/aws_deploy_prep_$(date +%Y%m%d_%H%M%S).log"

# Function to log messages
log() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" | tee -a "$DEPLOY_LOG"
}

# Check AWS CLI installation
log "Checking AWS CLI installation..."
if command -v aws &> /dev/null; then
  AWS_VERSION=$(aws --version)
  log "✅ Found AWS CLI: $AWS_VERSION"
else
  log "❌ AWS CLI not found. Installing..."
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if [ -f "$BASE_DIR/AWSCLIV2.pkg" ]; then
      log "  Installing from existing package..."
      sudo installer -pkg "$BASE_DIR/AWSCLIV2.pkg" -target /
    else
      log "  Downloading and installing AWS CLI..."
      curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
      sudo installer -pkg AWSCLIV2.pkg -target /
    fi
  else
    # Linux
    log "  Downloading and installing AWS CLI..."
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
  fi
  
  # Check if installation was successful
  if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version)
    log "✅ AWS CLI installed successfully: $AWS_VERSION"
  else
    log "❌ AWS CLI installation failed. Please install manually."
    exit 1
  fi
fi

# Check AWS credentials
log "Checking AWS credentials..."
AWS_CREDS=$(aws sts get-caller-identity 2>&1)
if [[ $AWS_CREDS == *"error"* ]]; then
  log "❌ AWS credentials not configured or invalid"
  log "  Please run 'aws configure' to set up your credentials"
  exit 1
else
  log "✅ AWS credentials configured"
  log "  $AWS_CREDS"
fi

# Create deployment package
log "Creating deployment package..."
DEPLOY_DIR="$BASE_DIR/aws_deploy"
mkdir -p "$DEPLOY_DIR"

# Copy required files
log "Copying required files..."
cp -r "$BASE_DIR/mcp" "$DEPLOY_DIR/"
cp -r "$BASE_DIR/agents" "$DEPLOY_DIR/"
cp -r "$BASE_DIR/config" "$DEPLOY_DIR/"
cp "$BASE_DIR/requirements.txt" "$DEPLOY_DIR/"
cp "$BASE_DIR/requirements_voice.txt" "$DEPLOY_DIR/"
cp "$BASE_DIR/Modelfile" "$DEPLOY_DIR/"
cp "$BASE_DIR/anima_voice_recognition.py" "$DEPLOY_DIR/"
cp "$BASE_DIR/anima_ollama_bridge.py" "$DEPLOY_DIR/"
cp "$BASE_DIR/anima_sentience.py" "$DEPLOY_DIR/"
cp "$BASE_DIR/anima_voice.py" "$DEPLOY_DIR/"

# Create AWS deployment files
log "Creating AWS deployment files..."

# Create Dockerfile
cat > "$DEPLOY_DIR/Dockerfile" << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    espeak \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt requirements_voice.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements_voice.txt

# Copy application files
COPY . .

# Make scripts executable
RUN chmod +x mcp/mcp_main.py anima_voice_recognition.py

# Expose ports
EXPOSE 8765

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the MCP server
CMD ["python", "mcp/mcp_main.py", "--host", "0.0.0.0"]
EOF

# Create docker-compose.yml
cat > "$DEPLOY_DIR/docker-compose.yml" << 'EOF'
version: '3'

services:
  mcp-server:
    build: .
    ports:
      - "8765:8765"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./memory:/app/memory
    restart: unless-stopped
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}

  anima-voice:
    build: .
    depends_on:
      - mcp-server
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./memory:/app/memory
      - ./voices:/app/voices
    restart: unless-stopped
    command: python anima_voice_recognition.py
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
EOF

# Create AWS CloudFormation template
cat > "$DEPLOY_DIR/cloudformation.yaml" << 'EOF'
AWSTemplateFormatVersion: '2010-09-09'
Description: 'SoulCoreHub AWS Deployment'

Parameters:
  InstanceType:
    Description: EC2 instance type
    Type: String
    Default: t3.medium
    AllowedValues:
      - t3.small
      - t3.medium
      - t3.large
    ConstraintDescription: must be a valid EC2 instance type.

  KeyName:
    Description: Name of an existing EC2 KeyPair to enable SSH access
    Type: AWS::EC2::KeyPair::KeyName
    ConstraintDescription: must be the name of an existing EC2 KeyPair.

Resources:
  SoulCoreSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Enable SSH and web access
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 8765
          ToPort: 8765
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0

  SoulCoreInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      SecurityGroups:
        - !Ref SoulCoreSecurityGroup
      KeyName: !Ref KeyName
      ImageId: ami-0c55b159cbfafe1f0  # Amazon Linux 2 AMI (adjust for your region)
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash -xe
          yum update -y
          yum install -y docker git
          systemctl start docker
          systemctl enable docker
          curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
          chmod +x /usr/local/bin/docker-compose
          
          # Clone the repository
          mkdir -p /opt/soulcore
          cd /opt/soulcore
          
          # Set up the deployment
          # (You'll need to copy your deployment files to this instance)
          
          # Start the services
          # docker-compose up -d

  SoulCoreEIP:
    Type: AWS::EC2::EIP
    Properties:
      InstanceId: !Ref SoulCoreInstance

Outputs:
  InstanceId:
    Description: The instance ID of the SoulCore server
    Value: !Ref SoulCoreInstance
  PublicIP:
    Description: Public IP address of the SoulCore server
    Value: !Ref SoulCoreEIP
  PublicDNS:
    Description: Public DNS of the SoulCore server
    Value: !GetAtt SoulCoreInstance.PublicDnsName
EOF

# Create deployment script
cat > "$DEPLOY_DIR/deploy.sh" << 'EOF'
#!/bin/bash
# deploy.sh - Deploy SoulCoreHub to AWS

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
  echo "❌ AWS CLI not found. Please install it first."
  exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
  echo "❌ Docker not found. Please install it first."
  exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
  echo "❌ Docker Compose not found. Please install it first."
  exit 1
fi

# Set AWS region if not already set
if [ -z "$AWS_DEFAULT_REGION" ]; then
  export AWS_DEFAULT_REGION="us-west-2"
  echo "⚠️ AWS_DEFAULT_REGION not set, using default: $AWS_DEFAULT_REGION"
fi

# Create ECR repository if it doesn't exist
REPO_NAME="soulcorehub"
aws ecr describe-repositories --repository-names $REPO_NAME > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Creating ECR repository: $REPO_NAME"
  aws ecr create-repository --repository-name $REPO_NAME
fi

# Get ECR repository URI
REPO_URI=$(aws ecr describe-repositories --repository-names $REPO_NAME --query 'repositories[0].repositoryUri' --output text)

# Build and push Docker image
echo "Building Docker image..."
docker build -t $REPO_NAME .

# Log in to ECR
echo "Logging in to ECR..."
aws ecr get-login-password | docker login --username AWS --password-stdin $REPO_URI

# Tag and push image
echo "Pushing image to ECR..."
docker tag $REPO_NAME:latest $REPO_URI:latest
docker push $REPO_URI:latest

# Deploy CloudFormation stack
STACK_NAME="SoulCoreHub"
echo "Deploying CloudFormation stack: $STACK_NAME..."
aws cloudformation deploy \
  --template-file cloudformation.yaml \
  --stack-name $STACK_NAME \
  --parameter-overrides \
    KeyName=YourKeyPair \
  --capabilities CAPABILITY_IAM

# Get outputs
echo "Deployment complete. Getting outputs..."
aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs' --output table

echo "✅ Deployment successful!"
EOF

chmod +x "$DEPLOY_DIR/deploy.sh"

# Create README for deployment
cat > "$DEPLOY_DIR/README.md" << 'EOF'
# SoulCoreHub AWS Deployment

This directory contains all the necessary files to deploy SoulCoreHub to AWS.

## Prerequisites

- AWS CLI installed and configured
- Docker and Docker Compose installed
- An AWS account with appropriate permissions

## Deployment Options

### Option 1: EC2 with Docker Compose

1. Create an EC2 instance (t3.medium or larger recommended)
2. Install Docker and Docker Compose on the instance
3. Copy the contents of this directory to the instance
4. Run `docker-compose up -d` to start the services

### Option 2: Automated CloudFormation Deployment

1. Make sure AWS CLI is configured with appropriate credentials
2. Run the deployment script:
   ```
   ./deploy.sh
   ```

## Configuration

- Edit `docker-compose.yml` to adjust service configuration
- Environment variables can be set in a `.env` file

## Monitoring

- Check logs in the `logs` directory
- Monitor the services with `docker-compose logs -f`

## Troubleshooting

- If the MCP server fails to start, check the logs for errors
- Ensure all required ports are open in the security group
- Verify AWS credentials are correctly configured
EOF

log "✅ Deployment package created at: $DEPLOY_DIR"
log "  To deploy to AWS, follow the instructions in $DEPLOY_DIR/README.md"

# Final summary
log "Preparation Summary:"
log "-----------------"
log "- AWS CLI: $(aws --version)"
log "- Deployment package: $DEPLOY_DIR"
log "- Deployment log: $DEPLOY_LOG"
log ""
log "Next Steps:"
log "1. Review the deployment package"
log "2. Run the debug script to ensure everything is working properly"
log "3. Test locally with Docker before deploying to AWS"
log "4. Follow the instructions in $DEPLOY_DIR/README.md to deploy to AWS"

echo ""
echo "🚀 AWS deployment preparation completed. Check $DEPLOY_LOG for details."
