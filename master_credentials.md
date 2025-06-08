# SoulCoreHub Master Credentials Document

## ⚠️ HIGHLY CONFIDENTIAL - SECURE STORAGE ONLY ⚠️

This document contains a comprehensive inventory of all credentials for the SoulCoreHub project. All credentials have been securely stored in the `.env` file, which is excluded from Git via `.gitignore`.

## AWS Accounts

### Primary AWS Account (699475940746)

- **Account ID**: 699475940746
- **Console URL**: https://heloimai.signin.aws.amazon.com/console
- **IAM User**: soulcore-admin
- **Console Password**: [STORED IN .ENV]
- **Access Key ID**: AKIA2FXAD2WFJIPPPZB2
- **Secret Access Key**: [STORED IN .ENV]
- **User ARN**: arn:aws:iam::699475940746:user/soulcore-admin

#### SageMaker
- **Default Execution Role**: arn:aws:iam::699475940746:role/service-role/AmazonSageMaker-ExecutionRole-20250508T072749
- **Space Execution Role**: arn:aws:iam::699475940746:role/service-role/AmazonSageMaker-ExecutionRole-20250508T072749

#### S3 Buckets
- **SAM CLI Bucket**: aws-sam-cli-managed-default-samclisourcebucket-rgxvv7kpkrj1
- **Email Storage**: soulcorehub-email-storage
- **Memory Bucket**: soulcore-memory-699475940746-us-east-1-evolve

#### Additional IAM Users/Keys
- **Access Key ID (3)**: AKIA2FXAD2WFICJYDDS6
- **Secret Access Key (3)**: [STORED IN .ENV]
- **Access Key ID (4)**: AKIA2FXAD2WFOQ4O5PXM
- **Secret Access Key (4)**: [STORED IN .ENV]
- **Access Key ID (5)**: AKIA2FXAD2WFNZ7PUOXT
- **Secret Access Key (5)**: [STORED IN .ENV]

#### CodeCommit
- **Username**: kamelot-at-699475940746
- **Password**: [STORED IN .ENV]

#### AWS Signer
- **Profile ARN**: arn:aws:signer:us-east-1:699475940746:/signing-profiles/Heloimai
- **Versioned Profile ARN**: arn:aws:signer:us-east-1:699475940746:/signing-profiles/Heloimai/Z9OVbt9shv

#### Keyspaces
- **Password**: [STORED IN .ENV]

### Secondary AWS Account (954976316292)

- **Account ID**: 954976316292
- **Role ARN**: arn:aws:sts::954976316292:assumed-role/AWSReservedSSO_AdministratorAccess_92205e21b0c3e98c/kamo
- **Access Key ID**: AKIA54WIGFOCPB45JWOQ
- **Secret Access Key**: [STORED IN .ENV]

#### CodeCommit
- **Username**: ses-smtp-user.20250510-114026-at-954976316292
- **Password**: [STORED IN .ENV]

### AWS Identity Center

- **Portal URL**: https://d-9067c6fe37.awsapps.com/start
- **Username**: Kamelot
- **Password**: [STORED IN .ENV]
- **User ID**: 147884a8-a011-7097-5707-83d8fc42ce9f
- **Issuer URL**: https://identitycenter.amazonaws.com/ssoins-7223b7ec9f7beae4

### AWS Organizations

- **Organization ID (1)**: o-iwq7m0exd4
- **Organization ID (2)**: o-1yp8sm0fq8

### Amazon Q

- **App URL**: https://7223ec8015a99235.transform.developer.q.aws.com/
- **Profile ARN**: arn:aws:codewhisperer:us-east-1:699475940746:profile/MG7EQQE7Y3G3
- **Transform URL**: https://72238556daf69245.transform.developer.q.aws.com/

## Email Services (AWS SES)

- **SMTP Server**: email-smtp.us-east-1.amazonaws.com
- **SMTP Port**: 587
- **SMTP Username**: ses-smtp-user.20250510-114026
- **SMTP Password**: [STORED IN .ENV]
- **Default Sender**: heloimai@heloim-ai.tech
- **Email Storage Bucket**: soulcorehub-email-storage

## NVIDIA NGC

- **API Key 1**: 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
- **API Key 2**: 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
- **Organization Primary**: 0701214761930058
- **Organization Secondary**: 0580661486523348
- **Team**: helo-im-ai
- **Package Hash**: 64281653428c3dc1ece4c4b74a0d1571b5e007d0c523c241e16a45a02bd2cfc8

## GitLab

- **PAT Name**: kiwoncode
- **PAT Value**: [STORED IN .ENV]

## Microsoft

- **Email**: Helo-Im-AiKam@HeloImAiinc.onmicrosoft.com
- **Tenant ID**: 98f8305b-f09c-4582-99e7-534411e2551d

## Domain & API Services

### Namecheap
- **API Key**: 58cf42945bbb48cabdeb488ef0b10910

### CogCache
- **API Key**: TC_CogCache_4egatjnZQnB7WicZMShC
- **Endpoint**: https://proxy-api.cogcache.com

### Docker
- **Username**: heloimai
- **PAT**: [STORED IN .ENV]

### Spotify
- **RSS Feed**: https://anchor.fm/s/fe2abd28/podcast/rss
- **Email**: kabowens1@student.fullsail.edu

### Hugging Face
- **Token**: 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

### Nebius AI
- **Token**: [STORED IN .ENV - LONG TOKEN]

### JWT (Local Development)
- **Token**: [STORED IN .ENV - LONG TOKEN]

### MetaMask
- **Seed Phrase**: [STORED IN .ENV]

### Twitch
- **Stream Key**: live_1248493538_Rbxc0scCSw1iflV3lNTFj9AkRxrVXY

## IBM Services

- **Watson URL**: https://api.us-south.assistant.watson.cloud.ibm.com/instances/73c163aa-d7ae-48f2-bb08-1c5bd9dec0e5
- **Watson API Key**: [STORED IN .ENV]
- **CEID**: 10a9um
- **Software ID**: 0004391633
- **Contract Number**: USEHIIMRJQK

## Development Tools

### JetBrains
- **License ID**: VLCQBU8XUQ

### New Relic
- **API Key**: NRAK-S68EDC4O2RAPQXOMY8GO49UOMBI
- **Account ID**: 6313414

## Network Information

- **Public IP**: 67.191.208.180

## Security Best Practices

1. **Never commit the `.env` file to Git**
2. **Rotate credentials regularly**
3. **Use IAM roles instead of access keys when possible**
4. **Limit permissions to only what is needed**
5. **Monitor for unauthorized access**
6. **Store this document in a secure location**
7. **Consider using a password manager for team access**

## Credential Validation

Run the credentials check utility to validate all credentials:

```bash
python src/utils/credentials_check.py
```
