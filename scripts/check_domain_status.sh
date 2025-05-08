#!/bin/bash

# SoulCoreHub Domain Status Check Script
# This script checks the status of SoulCoreHub domains and DNS records

echo "SoulCoreHub Domain Status Check"
echo "=============================="

# Check domain registration status
echo -e "\n[1] Checking domain registration status..."
aws route53domains list-domains | grep -E "soulcorehub\.(com|io)"

# Check hosted zones
echo -e "\n[2] Checking hosted zones..."
aws route53 list-hosted-zones | grep -E "soulcorehub\.(com|io)"

# Check DNS records for soulcorehub.com
echo -e "\n[3] Checking DNS records for soulcorehub.com..."
aws route53 list-resource-record-sets --hosted-zone-id Z04784531EU732LD17K6N

# Check DNS records for soulcorehub.io
echo -e "\n[4] Checking DNS records for soulcorehub.io..."
aws route53 list-resource-record-sets --hosted-zone-id Z04879123TJDNS1CJINTJ

# Check DNS propagation
echo -e "\n[5] Checking DNS propagation..."
echo "soulcorehub.com:"
dig soulcorehub.com +short
echo "www.soulcorehub.com:"
dig www.soulcorehub.com +short
echo "soulcorehub.io:"
dig soulcorehub.io +short
echo "www.soulcorehub.io:"
dig www.soulcorehub.io +short

# Check SSL certificates
echo -e "\n[6] Checking SSL certificates..."
echo "soulcorehub.com:"
echo | openssl s_client -servername soulcorehub.com -connect soulcorehub.com:443 2>/dev/null | openssl x509 -noout -dates
echo "www.soulcorehub.com:"
echo | openssl s_client -servername www.soulcorehub.com -connect www.soulcorehub.com:443 2>/dev/null | openssl x509 -noout -dates
echo "soulcorehub.io:"
echo | openssl s_client -servername soulcorehub.io -connect soulcorehub.io:443 2>/dev/null | openssl x509 -noout -dates
echo "www.soulcorehub.io:"
echo | openssl s_client -servername www.soulcorehub.io -connect www.soulcorehub.io:443 2>/dev/null | openssl x509 -noout -dates

echo -e "\n[7] Checking website availability..."
echo "soulcorehub.com:"
curl -I -s https://soulcorehub.com | head -n 1
echo "www.soulcorehub.com:"
curl -I -s https://www.soulcorehub.com | head -n 1
echo "soulcorehub.io:"
curl -I -s https://soulcorehub.io | head -n 1
echo "www.soulcorehub.io:"
curl -I -s https://www.soulcorehub.io | head -n 1

echo -e "\nDomain status check complete!"
