"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CodeCatalystStack = void 0;
const cdk = require("aws-cdk-lib");
const iam = require("aws-cdk-lib/aws-iam");
const codebuild = require("aws-cdk-lib/aws-codebuild");
const codepipeline = require("aws-cdk-lib/aws-codepipeline");
const codepipeline_actions = require("aws-cdk-lib/aws-codepipeline-actions");
const s3 = require("aws-cdk-lib/aws-s3");
class CodeCatalystStack extends cdk.Stack {
    constructor(scope, id, props) {
        super(scope, id, props);
        // Create a role for CodeBuild
        const role = new iam.Role(this, 'CodeBuildRole', {
            assumedBy: new iam.ServicePrincipal('codebuild.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonS3FullAccess'),
                iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonDynamoDBFullAccess'),
                iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonAPIGatewayAdministrator'),
                iam.ManagedPolicy.fromAwsManagedPolicyName('AWSLambda_FullAccess'),
                iam.ManagedPolicy.fromAwsManagedPolicyName('CloudWatchLogsFullAccess'),
                iam.ManagedPolicy.fromAwsManagedPolicyName('IAMFullAccess'),
            ],
        });
        // Create an S3 bucket for artifacts
        const artifactBucket = new s3.Bucket(this, 'ArtifactBucket', {
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            autoDeleteObjects: true,
        });
        // Create a CodeBuild project
        const buildProject = new codebuild.PipelineProject(this, 'BuildProject', {
            environment: {
                buildImage: codebuild.LinuxBuildImage.AMAZON_LINUX_2_3,
                privileged: true,
            },
            buildSpec: codebuild.BuildSpec.fromObject({
                version: '0.2',
                phases: {
                    install: {
                        'runtime-versions': {
                            nodejs: '18',
                        },
                        commands: [
                            'cd cdk-app',
                            'npm install',
                        ],
                    },
                    build: {
                        commands: [
                            'npm run build',
                            'npm run test',
                        ],
                    },
                },
                artifacts: {
                    'base-directory': 'cdk-app',
                    files: [
                        '**/*',
                    ],
                },
            }),
        });
        // Create a CodeBuild project for deployment
        const deployProject = new codebuild.PipelineProject(this, 'DeployProject', {
            environment: {
                buildImage: codebuild.LinuxBuildImage.AMAZON_LINUX_2_3,
                privileged: true,
            },
            buildSpec: codebuild.BuildSpec.fromObject({
                version: '0.2',
                phases: {
                    install: {
                        'runtime-versions': {
                            nodejs: '18',
                        },
                        commands: [
                            'npm install -g aws-cdk',
                            'cd cdk-app',
                            'npm install',
                        ],
                    },
                    build: {
                        commands: [
                            'npm run build',
                            'cdk deploy --require-approval never',
                        ],
                    },
                },
            }),
        });
        // Create a CodePipeline
        const pipeline = new codepipeline.Pipeline(this, 'Pipeline', {
            artifactBucket,
            pipelineName: 'SoulCoreHubPipeline',
        });
        // Add source stage
        const sourceOutput = new codepipeline.Artifact('SourceCode');
        const sourceAction = new codepipeline_actions.GitHubSourceAction({
            actionName: 'GitHub_Source',
            owner: 'Sourcesiri-Kamelot',
            repo: 'SoulCoreHub',
            branch: 'main',
            oauthToken: cdk.SecretValue.secretsManager('github-token'),
            output: sourceOutput,
        });
        pipeline.addStage({
            stageName: 'Source',
            actions: [sourceAction],
        });
        // Add build stage
        const buildOutput = new codepipeline.Artifact('BuildOutput');
        const buildAction = new codepipeline_actions.CodeBuildAction({
            actionName: 'Build',
            project: buildProject,
            input: sourceOutput,
            outputs: [buildOutput],
        });
        pipeline.addStage({
            stageName: 'Build',
            actions: [buildAction],
        });
        // Add deploy stage
        const deployAction = new codepipeline_actions.CodeBuildAction({
            actionName: 'Deploy',
            project: deployProject,
            input: buildOutput,
        });
        pipeline.addStage({
            stageName: 'Deploy',
            actions: [deployAction],
        });
        // Create outputs
        new cdk.CfnOutput(this, 'PipelineName', {
            value: pipeline.pipelineName,
            description: 'CodePipeline Name',
        });
        new cdk.CfnOutput(this, 'ArtifactBucketName', {
            value: artifactBucket.bucketName,
            description: 'Artifact Bucket Name',
        });
    }
}
exports.CodeCatalystStack = CodeCatalystStack;
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiY29kZWNhdGFseXN0LXN0YWNrLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXMiOlsiY29kZWNhdGFseXN0LXN0YWNrLnRzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiI7OztBQUFBLG1DQUFtQztBQUVuQywyQ0FBMkM7QUFDM0MsdURBQXVEO0FBQ3ZELDZEQUE2RDtBQUM3RCw2RUFBNkU7QUFDN0UseUNBQXlDO0FBRXpDLE1BQWEsaUJBQWtCLFNBQVEsR0FBRyxDQUFDLEtBQUs7SUFDOUMsWUFBWSxLQUFnQixFQUFFLEVBQVUsRUFBRSxLQUFzQjtRQUM5RCxLQUFLLENBQUMsS0FBSyxFQUFFLEVBQUUsRUFBRSxLQUFLLENBQUMsQ0FBQztRQUV4Qiw4QkFBOEI7UUFDOUIsTUFBTSxJQUFJLEdBQUcsSUFBSSxHQUFHLENBQUMsSUFBSSxDQUFDLElBQUksRUFBRSxlQUFlLEVBQUU7WUFDL0MsU0FBUyxFQUFFLElBQUksR0FBRyxDQUFDLGdCQUFnQixDQUFDLHlCQUF5QixDQUFDO1lBQzlELGVBQWUsRUFBRTtnQkFDZixHQUFHLENBQUMsYUFBYSxDQUFDLHdCQUF3QixDQUFDLG9CQUFvQixDQUFDO2dCQUNoRSxHQUFHLENBQUMsYUFBYSxDQUFDLHdCQUF3QixDQUFDLDBCQUEwQixDQUFDO2dCQUN0RSxHQUFHLENBQUMsYUFBYSxDQUFDLHdCQUF3QixDQUFDLCtCQUErQixDQUFDO2dCQUMzRSxHQUFHLENBQUMsYUFBYSxDQUFDLHdCQUF3QixDQUFDLHNCQUFzQixDQUFDO2dCQUNsRSxHQUFHLENBQUMsYUFBYSxDQUFDLHdCQUF3QixDQUFDLDBCQUEwQixDQUFDO2dCQUN0RSxHQUFHLENBQUMsYUFBYSxDQUFDLHdCQUF3QixDQUFDLGVBQWUsQ0FBQzthQUM1RDtTQUNGLENBQUMsQ0FBQztRQUVILG9DQUFvQztRQUNwQyxNQUFNLGNBQWMsR0FBRyxJQUFJLEVBQUUsQ0FBQyxNQUFNLENBQUMsSUFBSSxFQUFFLGdCQUFnQixFQUFFO1lBQzNELGFBQWEsRUFBRSxHQUFH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LENBQUM7U0FDdkIsQ0FBQyxDQUFDO1FBRUgsUUFBUSxDQUFDLFFBQVEsQ0FBQztZQUNoQixTQUFTLEVBQUUsT0FBTztZQUNsQixPQUFPLEVBQUUsQ0FBQyxXQUFXLENBQUM7U0FDdkIsQ0FBQyxDQUFDO1FBRUgsbUJBQW1CO1FBQ25CLE1BQU0sWUFBWSxHQUFHLElBQUksb0JBQW9CLENBQUMsZUFBZSxDQUFDO1lBQzVELFVBQVUsRUFBRSxRQUFRO1lBQ3BCLE9BQU8sRUFBRSxhQUFhO1lBQ3RCLEtBQUssRUFBRSxXQUFXO1NBQ25CLENBQUMsQ0FBQztRQUVILFFBQVEsQ0FBQyxRQUFRLENBQUM7WUFDaEIsU0FBUyxFQUFFLFFBQVE7WUFDbkIsT0FBTyxFQUFFLENBQUMsWUFBWSxDQUFDO1NBQ3hCLENBQUMsQ0FBQztRQUVILGlCQUFpQjtRQUNqQixJQUFJLEdBQUcsQ0FBQyxTQUFTLENBQUMsSUFBSSxFQUFFLGNBQWMsRUFBRTtZQUN0QyxLQUFLLEVBQUUsUUFBUSxDQUFDLFlBQVk7WUFDNUIsV0FBVyxFQUFFLG1CQUFtQjtTQUNqQyxDQUFDLENBQUM7UUFFSCxJQUFJLEdBQUcsQ0FBQyxTQUFTLENBQUMsSUFBSSxFQUFFLG9CQUFvQixFQUFFO1lBQzVDLEtBQUssRUFBRSxjQUFjLENBQUMsVUFBVTtZQUNoQyxXQUFXLEVBQUUsc0JBQXNCO1NBQ3BDLENBQUMsQ0FBQztJQUNMLENBQUM7Q0FDRjtBQWpKRCw4Q0FpSkMiLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgKiBhcyBjZGsgZnJvbSAnYXdzLWNkay1saWInO1xuaW1wb3J0IHsgQ29uc3RydWN0IH0gZnJvbSAnY29uc3RydWN0cyc7XG5pbXBvcnQgKiBhcyBpYW0gZnJvbSAnYXdzLWNkay1saWIvYXdzLWlhbSc7XG5pbXBvcnQgKiBhcyBjb2RlYnVpbGQgZnJvbSAnYXdzLWNkay1saWIvYXdzLWNvZGVidWlsZCc7XG5pbXBvcnQgKiBhcyBjb2RlcGlwZWxpbmUgZnJvbSAnYXdzLWNkay1saWIvYXdzLWNvZGVwaXBlbGluZSc7XG5pbXBvcnQgKiBhcyBjb2RlcGlwZWxpbmVfYWN0aW9ucyBmcm9tICdhd3MtY2RrLWxpYi9hd3MtY29kZXBpcGVsaW5lLWFjdGlvbnMnO1xuaW1wb3J0ICogYXMgczMgZnJvbSAnYXdzLWNkay1saWIvYXdzLXMzJztcblxuZXhwb3J0IGNsYXNzIENvZGVDYXRhbHlzdFN0YWNrIGV4dGVuZHMgY2RrLlN0YWNrIHtcbiAgY29uc3RydWN0b3Ioc2NvcGU6IENvbnN0cnVjdCwgaWQ6IHN0cmluZywgcHJvcHM/OiBjZGsuU3RhY2tQcm9wcykge1xuICAgIHN1cGVyKHNjb3BlLCBpZCwgcHJvcHMpO1xuXG4gICAgLy8gQ3JlYXRlIGEgcm9sZSBmb3IgQ29kZUJ1aWxkXG4gICAgY29uc3Qgcm9sZSA9IG5ldyBpYW0uUm9sZSh0aGlzLCAnQ29kZUJ1aWxkUm9sZScsIHtcbiAgICAgIGFzc3VtZWRCeTogbmV3IGlhbS5TZXJ2aWNlUHJpbmNpcGFsKCdjb2RlYnVpbGQuYW1hem9uYXdzLmNvbScpLFxuICAgICAgbWFuYWdlZFBvbGljaWVzOiBbXG4gICAgICAgIGlhbS5NYW5hZ2VkUG9saWN5LmZyb21Bd3NNYW5hZ2VkUG9saWN5TmFtZSgnQW1hem9uUzNGdWxsQWNjZXNzJyksXG4gICAgICAgIGlhbS5NYW5hZ2VkUG9saWN5LmZyb21Bd3NNYW5hZ2VkUG9saWN5TmFtZSgnQW1hem9uRHluYW1vREJGdWxsQWNjZXNzJyksXG4gICAgICAgIGlhbS5NYW5hZ2VkUG9saWN5LmZyb21Bd3NNYW5hZ2VkUG9saWN5TmFtZSgnQW1hem9uQVBJR2F0ZXdheUFkbWluaXN0cmF0b3InKSxcbiAgICAgICAgaWFtLk1hbmFnZWRQb2xpY3kuZnJvbUF3c01hbmFnZWRQb2xpY3lOYW1lKCdBV1NMYW1iZGFfRnVsbEFjY2VzcycpLFxuICAgICAgICBpYW0uTWFuYWdlZFBvbGljeS5mcm9tQXdzTWFuYWdlZFBvbGljeU5hbWUoJ0Nsb3VkV2F0Y2hMb2dzRnVsbEFjY2VzcycpLFxuICAgICAgICBpYW0uTWFuYWdlZFBvbGljeS5mcm9tQXdzTWFuYWdlZFBvbGljeU5hbWUoJ0lBTUZ1bGxBY2Nlc3MnKSxcbiAgICAgIF0sXG4gICAgfSk7XG5cbiAgICAvLyBDcmVhdGUgYW4gUzMgYnVja2V0IGZvciBhcnRpZmFjdHNcbiAgICBjb25zdCBhcnRpZmFjdEJ1Y2tldCA9IG5ldyBzMy5CdWNrZXQodGhpcywgJ0FydGlmYWN0QnVja2V0Jywge1xuICAgICAgcmVtb3ZhbFBvbGljeTogY2RrLlJlbW92YWxQb2xpY3kuREVTVFJPWSxcbiAgICAgIGF1dG9EZWxldGVPYmplY3RzOiB0cnVlLFxuICAgIH0pO1xuXG4gICAgLy8gQ3JlYXRlIGEgQ29kZUJ1aWxkIHByb2plY3RcbiAgICBjb25zdCBidWlsZFByb2plY3QgPSBuZXcgY29kZWJ1aWxkLlBpcGVsaW5lUHJvamVjdCh0aGlzLCAnQnVpbGRQcm9qZWN0Jywge1xuICAgICAgZW52aXJvbm1lbnQ6IHtcbiAgICAgICAgYnVpbGRJbWFnZTogY29kZWJ1aWxkLkxpbnV4QnVpbGRJbWFnZS5BTUFaT05fTElOVVhfMl8zLFxuICAgICAgICBwcml2aWxlZ2VkOiB0cnVlLFxuICAgICAgfSxcbiAgICAgIGJ1aWxkU3BlYzogY29kZWJ1aWxkLkJ1aWxkU3BlYy5mcm9tT2JqZWN0KHtcbiAgICAgICAgdmVyc2lvbjogJzAuMicsXG4gICAgICAgIHBoYXNlczoge1xuICAgICAgICAgIGluc3RhbGw6IHtcbiAgICAgICAgICAgICdydW50aW1lLXZlcnNpb25zJzoge1xuICAgICAgICAgICAgICBub2RlanM6ICcxOCcsXG4gICAgICAgICAgICB9LFxuICAgICAgICAgICAgY29tbWFuZHM6IFtcbiAgICAgICAgICAgICAgJ2NkIGNkay1hcHAnLFxuICAgICAgICAgICAgICAnbnBtIGluc3RhbGwnLFxuICAgICAgICAgICAgXSxcbiAgICAgICAgICB9LFxuICAgICAgICAgIGJ1aWxkOiB7XG4gICAgICAgICAgICBjb21tYW5kczogW1xuICAgICAgICAgICAgICAnbnBtIHJ1biBidWlsZCcsXG4gICAgICAgICAgICAgICducG0gcnVuIHRlc3QnLFxuICAgICAgICAgICAgXSxcbiAgICAgICAgICB9LFxuICAgICAgICB9LFxuICAgICAgICBhcnRpZmFjdHM6IHtcbiAgICAgICAgICAnYmFzZS1kaXJlY3RvcnknOiAnY2RrLWFwcCcsXG4gICAgICAgICAgZmlsZXM6IFtcbiAgICAgICAgICAgICcqKi8qJyxcbiAgICAgICAgICBdLFxuICAgICAgICB9LFxuICAgICAgfSksXG4gICAgfSk7XG5cbiAgICAvLyBDcmVhdGUgYSBDb2RlQnVpbGQgcHJvamVjdCBmb3IgZGVwbG95bWVudFxuICAgIGNvbnN0IGRlcGxveVByb2plY3QgPSBuZXcgY29kZWJ1aWxkLlBpcGVsaW5lUHJvamVjdCh0aGlzLCAnRGVwbG95UHJvamVjdCcsIHtcbiAgICAgIGVudmlyb25tZW50OiB7XG4gICAgICAgIGJ1aWxkSW1hZ2U6IGNvZGVidWlsZC5MaW51eEJ1aWxkSW1hZ2UuQU1BWk9OX0xJTlVYXzJfMyxcbiAgICAgICAgcHJpdmlsZWdlZDogdHJ1ZSxcbiAgICAgIH0sXG4gICAgICBidWlsZFNwZWM6IGNvZGVidWlsZC5CdWlsZFNwZWMuZnJvbU9iamVjdCh7XG4gICAgICAgIHZlcnNpb246ICcwLjInLFxuICAgICAgICBwaGFzZXM6IHtcbiAgICAgICAgICBpbnN0YWxsOiB7XG4gICAgICAgICAgICAncnVudGltZS12ZXJzaW9ucyc6IHtcbiAgICAgICAgICAgICAgbm9kZWpzOiAnMTgnLFxuICAgICAgICAgICAgfSxcbiAgICAgICAgICAgIGNvbW1hbmRzOiBbXG4gICAgICAgICAgICAgICducG0gaW5zdGFsbCAtZyBhd3MtY2RrJyxcbiAgICAgICAgICAgICAgJ2NkIGNkay1hcHAnLFxuICAgICAgICAgICAgICAnbnBtIGluc3RhbGwnLFxuICAgICAgICAgICAgXSxcbiAgICAgICAgICB9LFxuICAgICAgICAgIGJ1aWxkOiB7XG4gICAgICAgICAgICBjb21tYW5kczogW1xuICAgICAgICAgICAgICAnbnBtIHJ1biBidWlsZCcsXG4gICAgICAgICAgICAgICdjZGsgZGVwbG95IC0tcmVxdWlyZS1hcHByb3ZhbCBuZXZlcicsXG4gICAgICAgICAgICBdLFxuICAgICAgICAgIH0sXG4gICAgICAgIH0sXG4gICAgICB9KSxcbiAgICB9KTtcblxuICAgIC8vIENyZWF0ZSBhIENvZGVQaXBlbGluZVxuICAgIGNvbnN0IHBpcGVsaW5lID0gbmV3IGNvZGVwaXBlbGluZS5QaXBlbGluZSh0aGlzLCAnUGlwZWxpbmUnLCB7XG4gICAgICBhcnRpZmFjdEJ1Y2tldCxcbiAgICAgIHBpcGVsaW5lTmFtZTogJ1NvdWxDb3JlSHViUGlwZWxpbmUnLFxuICAgIH0pO1xuXG4gICAgLy8gQWRkIHNvdXJjZSBzdGFnZVxuICAgIGNvbnN0IHNvdXJjZU91dHB1dCA9IG5ldyBjb2RlcGlwZWxpbmUuQXJ0aWZhY3QoJ1NvdXJjZUNvZGUnKTtcbiAgICBjb25zdCBzb3VyY2VBY3Rpb24gPSBuZXcgY29kZXBpcGVsaW5lX2FjdGlvbnMuR2l0SHViU291cmNlQWN0aW9uKHtcbiAgICAgIGFjdGlvbk5hbWU6ICdHaXRIdWJfU291cmNlJyxcbiAgICAgIG93bmVyOiAnU291cmNlc2lyaS1LYW1lbG90JyxcbiAgICAgIHJlcG86ICdTb3VsQ29yZUh1YicsXG4gICAgICBicmFuY2g6ICdtYWluJyxcbiAgICAgIG9hdXRoVG9rZW46IGNkay5TZWNyZXRWYWx1ZS5zZWNyZXRzTWFuYWdlcignZ2l0aHViLXRva2VuJyksXG4gICAgICBvdXRwdXQ6IHNvdXJjZU91dHB1dCxcbiAgICB9KTtcblxuICAgIHBpcGVsaW5lLmFkZFN0YWdlKHtcbiAgICAgIHN0YWdlTmFtZTogJ1NvdXJjZScsXG4gICAgICBhY3Rpb25zOiBbc291cmNlQWN0aW9uXSxcbiAgICB9KTtcblxuICAgIC8vIEFkZCBidWlsZCBzdGFnZVxuICAgIGNvbnN0IGJ1aWxkT3V0cHV0ID0gbmV3IGNvZGVwaXBlbGluZS5BcnRpZmFjdCgnQnVpbGRPdXRwdXQnKTtcbiAgICBjb25zdCBidWlsZEFjdGlvbiA9IG5ldyBjb2RlcGlwZWxpbmVfYWN0aW9ucy5Db2RlQnVpbGRBY3Rpb24oe1xuICAgICAgYWN0aW9uTmFtZTogJ0J1aWxkJyxcbiAgICAgIHByb2plY3Q6IGJ1aWxkUHJvamVjdCxcbiAgICAgIGlucHV0OiBzb3VyY2VPdXRwdXQsXG4gICAgICBvdXRwdXRzOiBbYnVpbGRPdXRwdXRdLFxuICAgIH0pO1xuXG4gICAgcGlwZWxpbmUuYWRkU3RhZ2Uoe1xuICAgICAgc3RhZ2VOYW1lOiAnQnVpbGQnLFxuICAgICAgYWN0aW9uczogW2J1aWxkQWN0aW9uXSxcbiAgICB9KTtcblxuICAgIC8vIEFkZCBkZXBsb3kgc3RhZ2VcbiAgICBjb25zdCBkZXBsb3lBY3Rpb24gPSBuZXcgY29kZXBpcGVsaW5lX2FjdGlvbnMuQ29kZUJ1aWxkQWN0aW9uKHtcbiAgICAgIGFjdGlvbk5hbWU6ICdEZXBsb3knLFxuICAgICAgcHJvamVjdDogZGVwbG95UHJvamVjdCxcbiAgICAgIGlucHV0OiBidWlsZE91dHB1dCxcbiAgICB9KTtcblxuICAgIHBpcGVsaW5lLmFkZFN0YWdlKHtcbiAgICAgIHN0YWdlTmFtZTogJ0RlcGxveScsXG4gICAgICBhY3Rpb25zOiBbZGVwbG95QWN0aW9uXSxcbiAgICB9KTtcblxuICAgIC8vIENyZWF0ZSBvdXRwdXRzXG4gICAgbmV3IGNkay5DZm5PdXRwdXQodGhpcywgJ1BpcGVsaW5lTmFtZScsIHtcbiAgICAgIHZhbHVlOiBwaXBlbGluZS5waXBlbGluZU5hbWUsXG4gICAgICBkZXNjcmlwdGlvbjogJ0NvZGVQaXBlbGluZSBOYW1lJyxcbiAgICB9KTtcblxuICAgIG5ldyBjZGsuQ2ZuT3V0cHV0KHRoaXMsICdBcnRpZmFjdEJ1Y2tldE5hbWUnLCB7XG4gICAgICB2YWx1ZTogYXJ0aWZhY3RCdWNrZXQuYnVja2V0TmFtZSxcbiAgICAgIGRlc2NyaXB0aW9uOiAnQXJ0aWZhY3QgQnVja2V0IE5hbWUnLFxuICAgIH0pO1xuICB9XG59XG4iXX0=