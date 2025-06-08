# Email Setup Instructions for heloim-ai.tech

## Domain Verification

To verify your domain with AWS SES, add these DNS records to your domain:

### DKIM Records
Add these CNAME records to your DNS configuration:

1. `74ovn7vlsvgafdmowx6vv46f2m4phdm2._domainkey.heloim-ai.tech` → `74ovn7vlsvgafdmowx6vv46f2m4phdm2.dkim.amazonses.com`
2. `wlanevnqgioys3wg44rr5mxkam4yjum2._domainkey.heloim-ai.tech` → `wlanevnqgioys3wg44rr5mxkam4yjum2.dkim.amazonses.com`
3. `vi444j4lvlxm5sn7iqtohgrwnv4ec4ck._domainkey.heloim-ai.tech` → `vi444j4lvlxm5sn7iqtohgrwnv4ec4ck.dkim.amazonses.com`

### TXT Record for Domain Verification
Add this TXT record to your DNS configuration:

`heloim-ai.tech` → `"EctwEf2mUIyUSXWe8Nw2KizK9Y4cBBm8hrYhtIL7L+Y="`

### MX Record
Add an MX record to receive emails:

`heloim-ai.tech` → `10 inbound-smtp.us-east-1.amazonaws.com`

## Email Verification

Verification emails have been sent to:
- heloimai@heloim-ai.tech
- kiwonb@heloim-ai.tech

You need to click the verification links in these emails to complete the setup.

## Setting Up Email Receiving

To receive emails, you'll need to set up SES receipt rules. Here's how:

1. Create a receipt rule set
2. Create rules to forward emails to your preferred destination (S3, Lambda, or SNS)

## Email Client Setup

After verification is complete, you can use these credentials in your email client:

- SMTP Server: email-smtp.us-east-1.amazonaws.com
- Port: 587 (TLS) or 465 (SSL)
- Username: [Create SMTP credentials in AWS SES console]
- Password: [Create SMTP credentials in AWS SES console]

## Moving from info@heloim-ai.tech to kiwonb@heloim-ai.tech

After setting up kiwonb@heloim-ai.tech, create a forwarding rule from info@heloim-ai.tech to kiwonb@heloim-ai.tech.

## Next Steps

1. Add the DNS records listed above to your domain provider
2. Check your email for verification links and click them
3. Create SMTP credentials in the AWS SES console
4. Set up email receiving rules
5. Configure your email client with the new credentials
