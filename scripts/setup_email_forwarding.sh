#!/bin/bash

# SoulCoreHub Email Forwarding Setup Script
# This script helps set up email forwarding for SoulCoreHub domains

echo "SoulCoreHub Email Forwarding Setup"
echo "=================================="
echo ""
echo "Setting up email forwarding for your SoulCoreHub domains to kiwonbowens@helo-im.ai"
echo ""

# Set the destination email
destination_email="kiwonbowens@helo-im.ai"

# Create TXT records for ForwardEmail verification
echo "Adding TXT records for ForwardEmail verification..."

# For soulcorehub.com
aws route53 change-resource-record-sets \
  --hosted-zone-id Z04784531EU732LD17K6N \
  --change-batch '{
    "Changes": [
      {
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "soulcorehub.com",
          "Type": "TXT",
          "TTL": 300,
          "ResourceRecords": [
            {
              "Value": "\"forward-email='"$destination_email"'\""
            }
          ]
        }
      }
    ]
  }'

# For soulcorehub.io
aws route53 change-resource-record-sets \
  --hosted-zone-id Z04879123TJDNS1CJINTJ \
  --change-batch '{
    "Changes": [
      {
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "soulcorehub.io",
          "Type": "TXT",
          "TTL": 300,
          "ResourceRecords": [
            {
              "Value": "\"forward-email='"$destination_email"'\""
            }
          ]
        }
      }
    ]
  }'

echo ""
echo "Email forwarding setup is complete!"
echo ""
echo "The following email addresses will now forward to $destination_email:"
echo "- admin@soulcorehub.com"
echo "- info@soulcorehub.com"
echo "- support@soulcorehub.com"
echo "- admin@soulcorehub.io"
echo "- info@soulcorehub.io"
echo "- support@soulcorehub.io"
echo ""
echo "Note: DNS changes may take up to 24-48 hours to propagate fully."
