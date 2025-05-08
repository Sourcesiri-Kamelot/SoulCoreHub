# Setting Up GitHub Actions for SoulCoreHub

This guide explains how to set up GitHub Actions for continuous integration and deployment of SoulCoreHub.

## Prerequisites

1. A GitHub repository for your SoulCoreHub project
2. AWS credentials with appropriate permissions
3. An S3 bucket for deployment artifacts

## Steps to Set Up GitHub Actions

1. **Add GitHub Secrets**

   Go to your GitHub repository, then:
   - Click on "Settings"
   - Click on "Secrets and variables" > "Actions"
   - Add the following secrets:
     - `AWS_ACCESS_KEY_ID`: Your AWS access key ID
     - `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
     - `AWS_REGION`: Your AWS region (e.g., us-east-1)
     - `DEPLOYMENT_BUCKET`: Your S3 bucket name for deployment

2. **Create GitHub Actions Workflow File**

   The workflow file is already created as `setup_ci_cd.yml`. To use it:
   
   - Create a directory in your repository: `.github/workflows/`
   - Copy the `setup_ci_cd.yml` file to this directory:
   
   ```bash
   mkdir -p .github/workflows
   cp setup_ci_cd.yml .github/workflows/deploy.yml
   ```

3. **Commit and Push the Workflow File**

   ```bash
   git add .github/workflows/deploy.yml
   git commit -m "Add GitHub Actions workflow for CI/CD"
   git push
   ```

4. **Verify the Workflow**

   - Go to the "Actions" tab in your GitHub repository
   - You should see the workflow running (if you pushed to the main branch)
   - Check the logs to ensure everything is working correctly

## Customizing the Workflow

You can customize the workflow file to suit your needs:

- **Change the trigger branches**: Modify the `branches` section to trigger on different branches
- **Add more tests**: Add your test commands in the "Run tests" step
- **Add notifications**: Implement notification logic in the success/failure steps

## Troubleshooting

If you encounter issues with the GitHub Actions workflow:

1. **Check the workflow logs** in the GitHub Actions tab
2. **Verify your secrets** are correctly set up
3. **Ensure your AWS credentials** have the necessary permissions
4. **Check your S3 bucket** exists and is accessible

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-command-reference.html)
- [AWS Credentials for GitHub Actions](https://github.com/aws-actions/configure-aws-credentials)
