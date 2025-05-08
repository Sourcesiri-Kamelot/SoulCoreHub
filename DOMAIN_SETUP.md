# SoulCoreHub Domain Setup

## Domain Information
- Primary Domain: soulcorehub.com
- Secondary Domain: soulcorehub.io
- Registration Service: AWS Route 53
- Registration Date: May 8, 2025

## DNS Configuration

### soulcorehub.com
- Hosted Zone ID: Z04784531EU732LD17K6N
- Name Servers:
  - ns-143.awsdns-17.com
  - ns-1763.awsdns-28.co.uk
  - ns-1489.awsdns-58.org
  - ns-686.awsdns-21.net

### soulcorehub.io
- Hosted Zone ID: Z04879123TJDNS1CJINTJ
- Name Servers:
  - ns-215.awsdns-26.com
  - ns-1203.awsdns-22.org
  - ns-1554.awsdns-02.co.uk
  - ns-691.awsdns-22.net

## DNS Records

### A Records
- soulcorehub.com → 76.76.21.21
- soulcorehub.io → 76.76.21.21

### CNAME Records
- www.soulcorehub.com → soulcorehub.com
- www.soulcorehub.io → soulcorehub.io

### MX Records
- soulcorehub.com:
  - 10 mx1.forwardemail.net
  - 20 mx2.forwardemail.net
- soulcorehub.io:
  - 10 mx1.forwardemail.net
  - 20 mx2.forwardemail.net

## Email Forwarding
Email forwarding is configured through ForwardEmail.net:
- admin@soulcorehub.com → kiwonbowens@helo-im.ai
- info@soulcorehub.com → kiwonbowens@helo-im.ai
- support@soulcorehub.com → kiwonbowens@helo-im.ai
- admin@soulcorehub.io → kiwonbowens@helo-im.ai
- info@soulcorehub.io → kiwonbowens@helo-im.ai
- support@soulcorehub.io → kiwonbowens@helo-im.ai

## SSL Certificates
SSL certificates are managed through Vercel for both domains:
- soulcorehub.com (and www subdomain)
- soulcorehub.io (and www subdomain)

## Web Hosting
The SoulCoreHub web interface is hosted on Vercel and configured to serve from both domains.

## Domain Management
To make changes to the domain configuration:
1. Use AWS Route 53 console: https://console.aws.amazon.com/route53/
2. Or use AWS CLI with the following format:
   ```
   aws route53 change-resource-record-sets --hosted-zone-id ZONE_ID --change-batch file://changes.json
   ```

## Troubleshooting
If DNS issues occur:
1. Check propagation status: https://www.whatsmydns.net/
2. Verify Route 53 nameserver configuration
3. Ensure Vercel project is properly linked to both domains
