# Email Setup Instructions for heloim-ai.tech

## What I've Done So Far

1. Initiated domain verification for heloim-ai.tech with AWS SES
2. Initiated email verification for:
   - heloimai@heloim-ai.tech
   - kiwonb@heloim-ai.tech
3. Created an email rule set named "HeloImAiEmailRules"
4. Created an S3 bucket "heloimai-email-storage" for storing incoming emails
5. Created a configuration set "HeloImAiEmailConfig" for email tracking

## DNS Records to Add at domain.tech

To complete the setup, add these DNS records to your domain.tech account:

### DKIM Records (Add as CNAME records)
1. `74ovn7vlsvgafdmowx6vv46f2m4phdm2._domainkey.heloim-ai.tech` → `74ovn7vlsvgafdmowx6vv46f2m4phdm2.dkim.amazonses.com`
2. `wlanevnqgioys3wg44rr5mxkam4yjum2._domainkey.heloim-ai.tech` → `wlanevnqgioys3wg44rr5mxkam4yjum2.dkim.amazonses.com`
3. `vi444j4lvlxm5sn7iqtohgrwnv4ec4ck._domainkey.heloim-ai.tech` → `vi444j4lvlxm5sn7iqtohgrwnv4ec4ck.dkim.amazonses.com`

### TXT Record for Domain Verification
`heloim-ai.tech` → `"EctwEf2mUIyUSXWe8Nw2KizK9Y4cBBm8hrYhtIL7L+Y="`

### MX Record
`heloim-ai.tech` → `10 inbound-smtp.us-east-1.amazonaws.com`

## Next Steps (Manual Steps in AWS Console)

Since some steps require the AWS console, follow these instructions:

1. **Create SMTP Credentials**:
   - Go to AWS SES Console: https://console.aws.amazon.com/ses/
   - Click on "SMTP Settings" in the left navigation
   - Click "Create SMTP credentials"
   - Name the user "heloimai-smtp-user"
   - Save the generated SMTP username and password securely

2. **Complete Email Receiving Setup**:
   - Go to AWS SES Console: https://console.aws.amazon.com/ses/
   - Click on "Rule Sets" under "Email Receiving"
   - Select "HeloImAiEmailRules"
   - Click "Create Rule"
   - Add recipients: heloimai@heloim-ai.tech and kiwonb@heloim-ai.tech
   - Add an action: "S3" and select the "heloimai-email-storage" bucket
   - Set object key prefix: "inbox/"
   - Save the rule

3. **Set Up Email Client**:
   - Use these settings in your email client:
     - SMTP Server: email-smtp.us-east-1.amazonaws.com
     - Port: 587 (TLS) or 465 (SSL)
     - Username: [The SMTP username from step 1]
     - Password: [The SMTP password from step 1]
     - Email address: heloimai@heloim-ai.tech or kiwonb@heloim-ai.tech

4. **Access Received Emails**:
   - Option 1: Set up an email client that can access the S3 bucket
   - Option 2: Use AWS SES to forward emails to another working email address
   - Option 3: Create a simple web interface to read emails from the S3 bucket

## Important Notes

1. AWS SES starts in sandbox mode, which means:
   - You can only send emails to verified email addresses
   - You have sending quotas (usually 200 emails per 24 hours)
   - To move out of sandbox mode, you need to request production access

2. To check if your domain is verified:
   - Go to AWS SES Console
   - Click on "Domains" under "Identity Management"
   - Check the verification status of heloim-ai.tech

3. For immediate email access while waiting for verification:
   - Consider using a temporary email forwarding service
   - Or set up a simple Lambda function to forward emails from S3 to another working email address
