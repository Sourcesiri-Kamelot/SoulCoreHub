#!/bin/bash

# SoulCoreHub Vercel Deployment Script
# This script deploys the SoulCoreHub to Vercel and configures the domains

# Ensure Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Installing Vercel CLI..."
    npm install -g vercel
fi

# Login to Vercel (if not already logged in)
vercel login

# Deploy to Vercel
echo "Deploying SoulCoreHub to Vercel..."
vercel --prod

# Add domains to the project
echo "Adding domains to the project..."
vercel domains add soulcorehub.com -y
vercel domains add www.soulcorehub.com -y
vercel domains add soulcorehub.io -y
vercel domains add www.soulcorehub.io -y

# Verify domains and add SSL certificates
echo "Verifying domains and adding SSL certificates..."
vercel certs issue soulcorehub.com
vercel certs issue www.soulcorehub.com
vercel certs issue soulcorehub.io
vercel certs issue www.soulcorehub.io

echo "Deployment complete! Your SoulCoreHub is now accessible at:"
echo "- https://soulcorehub.com"
echo "- https://www.soulcorehub.com"
echo "- https://soulcorehub.io"
echo "- https://www.soulcorehub.io"
