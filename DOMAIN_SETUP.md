# Setting Up Custom Domains for SoulCoreHub

This guide explains how to set up custom domains for your SoulCoreHub deployment.

## Domain Strategy

For SoulCoreHub, we recommend the following domain strategy:

1. **Main Application**: `soulcore.heloim-ai.tech`
   - This will host the SoulCore dashboard and API endpoints

2. **Integration with Main Site**: `helo-im.ai`
   - Add a section to your main site that links to the SoulCore application

## Prerequisites

1. Domain ownership (helo-im.ai and heloim-ai.tech)
2. Access to DNS settings for your domains
3. AWS account with permissions to create ACM certificates

## Step 1: Create an SSL Certificate

1. **Go to AWS Certificate Manager (ACM)**:
   - Open the [AWS Certificate Manager console](https://console.aws.amazon.com/acm/home)
   - Make sure you're in the `us-east-1` region (required for API Gateway custom domains)

2. **Request a certificate**:
   - Click "Request a certificate"
   - Select "Request a public certificate"
   - Enter your domain name: `soulcore.heloim-ai.tech`
   - Click "Next"

3. **Validate the certificate**:
   - Choose "DNS validation" (recommended)
   - Click "Create record in Route 53" if your domain is managed by Route 53
   - Otherwise, add the CNAME record to your DNS provider manually
   - Wait for validation to complete (can take up to 30 minutes)

## Step 2: Deploy with Custom Domain

1. **Run the deployment script**:
   ```bash
   ./sam_deploy.sh
   ```

2. **When prompted, choose to set up a custom domain**:
   - Enter your domain name: `soulcore.heloim-ai.tech`
   - The script will look for your certificate and use it for deployment

3. **After deployment, get the API Gateway domain name**:
   - Go to the [API Gateway console](https://console.aws.amazon.com/apigateway/home)
   - Click on "Custom domain names"
   - Find your domain and note the "API Gateway domain name"

## Step 3: Configure DNS

1. **Add a CNAME record to your DNS settings**:
   - Go to your DNS provider's management console
   - Add a CNAME record:
     - Name: `soulcore` (or subdomain of your choice)
     - Value: The API Gateway domain name (e.g., `d-abcdef123.execute-api.us-east-1.amazonaws.com`)
     - TTL: 300 seconds (or as recommended by your provider)

2. **Wait for DNS propagation**:
   - DNS changes can take up to 48 hours to propagate
   - You can check propagation using tools like [dnschecker.org](https://dnschecker.org)

## Step 4: Integrate with Your Main Site

1. **Add the SoulCoreHub section to your main site**:
   - Use the integration snippet created by the `update_frontend.py` script
   - The snippet is saved as `website_integration_snippet.html`
   - Add this snippet to your main site's HTML where you want the section to appear

2. **Customize the styling**:
   - Modify the CSS in the snippet to match your main site's design
   - Update the colors, fonts, and layout as needed

## Step 5: Test the Integration

1. **Test the custom domain**:
   - Open `https://soulcore.heloim-ai.tech` in your browser
   - Verify that the SoulCore dashboard loads correctly

2. **Test the main site integration**:
   - Open your main site
   - Navigate to the section with the SoulCore integration
   - Click the links to ensure they work correctly

## Troubleshooting

If you encounter issues with your custom domain:

1. **Check certificate status**:
   - Ensure your certificate is "Issued" in ACM
   - If it's "Pending validation," complete the validation process

2. **Verify DNS settings**:
   - Confirm your CNAME record is correctly set up
   - Use `dig` or `nslookup` to check DNS resolution

3. **Check API Gateway configuration**:
   - Ensure the custom domain is properly mapped to your API
   - Verify the base path mappings are correct

4. **Clear browser cache**:
   - Sometimes browsers cache DNS resolutions
   - Try in a private/incognito window or clear your browser cache

## Additional Resources

- [AWS API Gateway Custom Domain Names](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-custom-domains.html)
- [AWS Certificate Manager User Guide](https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html)
- [DNS Propagation Checker](https://dnschecker.org)
