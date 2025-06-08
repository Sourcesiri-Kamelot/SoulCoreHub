# SoulCoreHub Credentials Summary

## ⚠️ IMPORTANT: KEEP THIS FILE SECURE ⚠️

This file contains a summary of all credentials used in the SoulCoreHub project. All sensitive credentials have been securely stored in the `.env` file, which is excluded from Git via `.gitignore`.

## AWS Credentials

- **Access Key ID**: AKIA54WIGFOCPB45JWOQ
- **Secret Access Key**: [STORED IN .ENV]
- **Account ID**: 954976316292
- **Role ARN**: arn:aws:sts::954976316292:assumed-role/AWSReservedSSO_AdministratorAccess_92205e21b0c3e98c/kamo

## Email (AWS SES) Credentials

- **SMTP Username**: ses-smtp-user.20250510-114026
- **SMTP Password**: [STORED IN .ENV]
- **SMTP Server**: email-smtp.us-east-1.amazonaws.com
- **SMTP Port**: 587
- **Default Sender**: heloimai@heloim-ai.tech
- **Email Storage Bucket**: soulcorehub-email-storage

## AWS CodeCommit Credentials

- **Username**: ses-smtp-user.20250510-114026-at-954976316292
- **Password**: [STORED IN .ENV]

## GitLab Credentials

- **PAT Name**: kiwoncode
- **PAT Value**: [STORED IN .ENV]
- **Expiration Date**: 2026/05/10

## NVIDIA NGC Credentials

- **API Key 1**: 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
- **API Key 2**: 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
- **Organization Primary**: 0701214761930058
- **Organization Secondary**: 0580661486523348
- **Team**: helo-im-ai

## AWS Marketplace Subscriptions

- **GitLab Ultimate**
  - Product ID: 930ec988-7647-45fd-b46b-54b002269967
  - Offer ID: 8pf7blr84untuyk0whj8z019j
  - Agreement ID: agmt-2q0n6c6ousp348jmfwgfpw7hl
  - Start Date: May 10, 2025 05:11 PM UTC

## How to Access Credentials

All sensitive credentials are stored in the `.env` file and can be accessed in code using:

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Access credentials
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
```

## Security Best Practices

1. **Never commit the `.env` file to Git**
2. **Rotate credentials regularly**
3. **Use IAM roles instead of access keys when possible**
4. **Limit permissions to only what is needed**
5. **Monitor for unauthorized access**

## Credential Validation

Run the credentials check utility to validate all credentials:

```bash
python src/utils/credentials_check.py
```

## Email Service Testing

Test the email service with:

```bash
python test_email_service.py
```
