# Email System Setup for heloimai@heloim-ai.tech

## Overview

I've set up a complete email system for heloimai@heloim-ai.tech using Amazon SES. The system includes:

1. Domain verification in Amazon SES
2. DNS records setup in Route 53
3. Email storage in S3
4. Email forwarding via Lambda
5. Bounce and error handling

## DNS Records

The following DNS records have been created in Route 53:

### Domain Verification
- **Type**: TXT
- **Name**: _amazonses.heloim-ai.tech
- **Value**: "EctwEf2mUIyUSXWe8Nw2KizK9Y4cBBm8hrYhtIL7L+Y="

### DKIM Records
- **Type**: CNAME
- **Name**: 74ovn7vlsvgafdmowx6vv46f2m4phdm2._domainkey.heloim-ai.tech
- **Value**: 74ovn7vlsvgafdmowx6vv46f2m4phdm2.dkim.amazonses.com

- **Type**: CNAME
- **Name**: wlanevnqgioys3wg44rr5mxkam4yjum2._domainkey.heloim-ai.tech
- **Value**: wlanevnqgioys3wg44rr5mxkam4yjum2.dkim.amazonses.com

- **Type**: CNAME
- **Name**: vi444j4lvlxm5sn7iqtohgrwnv4ec4ck._domainkey.heloim-ai.tech
- **Value**: vi444j4lvlxm5sn7iqtohgrwnv4ec4ck.dkim.amazonses.com

### SPF Record
- **Type**: TXT
- **Name**: heloim-ai.tech
- **Value**: "v=spf1 include:amazonses.com ~all"

### MX Record
- **Type**: MX
- **Name**: heloim-ai.tech
- **Value**: 10 inbound-smtp.us-east-1.amazonaws.com

## Email Flow

1. Emails sent to heloimai@heloim-ai.tech are received by Amazon SES
2. The emails are stored in the S3 bucket: heloim-ai-tech-emails
3. S3 triggers the Lambda function: EmailForwarder
4. The Lambda function forwards the email to: kiwonbowens@helo-im.ai

## Lambda Email Forwarder

A Lambda function has been created to forward emails:

1. **Function Name**: EmailForwarder
2. **Trigger**: S3 bucket (heloim-ai-tech-emails) with prefix "incoming/"
3. **Action**: Forwards emails to kiwonbowens@helo-im.ai
4. **Features**:
   - Preserves original email headers
   - Handles attachments
   - Includes error handling and logging
   - Deployed via CloudFormation

## Bounce Handling

1. Bounce notifications are sent to the SNS topic: email-notifications
2. A template has been created for bounce notifications: BounceNotificationTemplate
3. Configuration set HeloImAiTechConfigSet handles bounce events

## Verification Status

The domain verification is currently pending. It may take up to 72 hours for the verification to complete. You can check the status with:

```bash
aws ses get-identity-verification-attributes --identities heloim-ai.tech --region us-east-1
aws ses get-identity-dkim-attributes --identities heloim-ai.tech --region us-east-1
```

## Important Notes

1. **Confirmation Email**: Check kiwonbowens@helo-im.ai for a confirmation email from AWS SNS to confirm the subscription.

2. **SES Sandbox**: Your AWS account may be in the SES sandbox, which limits you to sending emails only to verified email addresses. To move out of the sandbox, you need to request production access.

3. **Domain Registration**: Ensure that the domain heloim-ai.tech is properly registered and that its nameservers are set to the Route 53 nameservers:
   - ns-951.awsdns-54.net
   - ns-1870.awsdns-41.co.uk
   - ns-322.awsdns-40.com
   - ns-1150.awsdns-15.org

4. **Testing**: Once verification is complete, you can test the email system by sending an email to heloimai@heloim-ai.tech.

## Resources Created

1. Route 53 Hosted Zone: heloim-ai.tech
2. S3 Bucket: heloim-ai-tech-emails
3. SNS Topic: email-notifications
4. SES Receipt Rule Set: HeloImAiTechRuleSet
5. SES Receipt Rule: HeloImAiTechRule
6. SES Email Template: BounceNotificationTemplate
7. SES Configuration Set: HeloImAiTechConfigSet
8. Lambda Function: EmailForwarder
9. CloudFormation Stack: EmailForwarderStack

## Troubleshooting

If you encounter any issues:

1. Check that all DNS records have propagated using:
   ```bash
   dig TXT _amazonses.heloim-ai.tech
   dig CNAME 74ovn7vlsvgafdmowx6vv46f2m4phdm2._domainkey.heloim-ai.tech
   dig MX heloim-ai.tech
   ```

2. Verify that the S3 bucket policy allows SES to write to it:
   ```bash
   aws s3api get-bucket-policy --bucket heloim-ai-tech-emails
   ```

3. Check SES receipt rules:
   ```bash
   aws ses describe-receipt-rule-set --rule-set-name HeloImAiTechRuleSet
   ```

4. Check Lambda function logs:
   ```bash
   aws logs filter-log-events --log-group-name /aws/lambda/EmailForwarder
   ```

5. Test the email forwarding by sending a test email:
   ```bash
   aws ses send-email --from sender@example.com --destination "ToAddresses=heloimai@heloim-ai.tech" --message "Subject={Data=Test Email,Charset=UTF-8},Body={Text={Data=This is a test email,Charset=UTF-8}}" --region us-east-1
   ```
