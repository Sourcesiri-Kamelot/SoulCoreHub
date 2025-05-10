import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as route53 from 'aws-cdk-lib/aws-route53';
import * as route53Targets from 'aws-cdk-lib/aws-route53-targets';
import * as acm from 'aws-cdk-lib/aws-certificatemanager';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';

export class SoulCoreHubStack extends cdk.Stack {
  public readonly api: apigateway.RestApi;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // DynamoDB Tables
    const clientsTable = new dynamodb.Table(this, 'ClientsTable', {
      partitionKey: { name: 'clientId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    const memoryTable = new dynamodb.Table(this, 'MemoryTable', {
      partitionKey: { name: 'memoryId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    const agentsTable = new dynamodb.Table(this, 'AgentsTable', {
      partitionKey: { name: 'agentId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    const appsTable = new dynamodb.Table(this, 'AppsTable', {
      partitionKey: { name: 'appId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    // Lambda Functions
    const mainframeLambda = new lambda.Function(this, 'MainframeLambda', {
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('lambda/mainframe'),
      environment: {
        CLIENTS_TABLE: clientsTable.tableName,
        MEMORY_TABLE: memoryTable.tableName,
        AGENTS_TABLE: agentsTable.tableName,
        APPS_TABLE: appsTable.tableName,
      },
      timeout: cdk.Duration.seconds(30),
      memorySize: 512,
    });

    const clientsLambda = new lambda.Function(this, 'ClientsLambda', {
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('lambda/clients'),
      environment: {
        CLIENTS_TABLE: clientsTable.tableName,
      },
      timeout: cdk.Duration.seconds(30),
      memorySize: 512,
    });

    const memoryLambda = new lambda.Function(this, 'MemoryLambda', {
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('lambda/memory'),
      environment: {
        MEMORY_TABLE: memoryTable.tableName,
      },
      timeout: cdk.Duration.seconds(30),
      memorySize: 512,
    });

    const agentsLambda = new lambda.Function(this, 'AgentsLambda', {
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('lambda/agents'),
      environment: {
        AGENTS_TABLE: agentsTable.tableName,
      },
      timeout: cdk.Duration.seconds(30),
      memorySize: 512,
    });

    const appsLambda = new lambda.Function(this, 'AppsLambda', {
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('lambda/apps'),
      environment: {
        APPS_TABLE: appsTable.tableName,
      },
      timeout: cdk.Duration.seconds(30),
      memorySize: 512,
    });

    // Grant permissions
    clientsTable.grantReadWriteData(mainframeLambda);
    memoryTable.grantReadWriteData(mainframeLambda);
    agentsTable.grantReadWriteData(mainframeLambda);
    appsTable.grantReadWriteData(mainframeLambda);

    clientsTable.grantReadWriteData(clientsLambda);
    memoryTable.grantReadWriteData(memoryLambda);
    agentsTable.grantReadWriteData(agentsLambda);
    appsTable.grantReadWriteData(appsLambda);

    // API Gateway
    this.api = new apigateway.RestApi(this, 'SoulCoreHubApi', {
      restApiName: 'SoulCoreHub API',
      description: 'API for SoulCoreHub',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: ['Content-Type', 'X-Api-Token', 'Authorization'],
      },
      deployOptions: {
        stageName: 'prod',
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
      },
    });

    // API Gateway Resources
    const statusResource = this.api.root.addResource('status');
    const clientsResource = this.api.root.addResource('clients');
    const executeResource = this.api.root.addResource('execute');
    const memoryResource = this.api.root.addResource('memory');
    const agentsResource = this.api.root.addResource('agents');
    const appsResource = this.api.root.addResource('apps');

    // Status Endpoint
    statusResource.addMethod('GET', new apigateway.LambdaIntegration(mainframeLambda));

    // Clients Endpoints
    clientsResource.addMethod('POST', new apigateway.LambdaIntegration(clientsLambda));
    
    const clientResource = clientsResource.addResource('{clientId}');
    clientResource.addMethod('GET', new apigateway.LambdaIntegration(clientsLambda));
    
    const authenticateResource = clientResource.addResource('authenticate');
    authenticateResource.addMethod('POST', new apigateway.LambdaIntegration(clientsLambda));
    
    const clientConfigResource = clientResource.addResource('config');
    clientConfigResource.addMethod('PUT', new apigateway.LambdaIntegration(clientsLambda));

    // Execute Endpoint
    executeResource.addMethod('POST', new apigateway.LambdaIntegration(mainframeLambda));

    // Memory Endpoints
    const memoryIdResource = memoryResource.addResource('{memoryId}');
    memoryIdResource.addMethod('GET', new apigateway.LambdaIntegration(memoryLambda));
    memoryIdResource.addMethod('PUT', new apigateway.LambdaIntegration(memoryLambda));
    memoryIdResource.addMethod('DELETE', new apigateway.LambdaIntegration(memoryLambda));
    
    const searchResource = memoryIdResource.addResource('search');
    searchResource.addMethod('POST', new apigateway.LambdaIntegration(memoryLambda));

    // Agents Endpoints
    const agentIdResource = agentsResource.addResource('{agentId}');
    
    const agentStatusResource = agentIdResource.addResource('status');
    agentStatusResource.addMethod('GET', new apigateway.LambdaIntegration(agentsLambda));
    
    const invokeResource = agentIdResource.addResource('invoke');
    invokeResource.addMethod('POST', new apigateway.LambdaIntegration(agentsLambda));
    
    const agentConfigResource = agentIdResource.addResource('config');
    agentConfigResource.addMethod('PUT', new apigateway.LambdaIntegration(agentsLambda));

    // Apps Endpoints
    appsResource.addMethod('GET', new apigateway.LambdaIntegration(appsLambda));
    appsResource.addMethod('POST', new apigateway.LambdaIntegration(appsLambda));
    
    const appIdResource = appsResource.addResource('{appId}');
    appIdResource.addMethod('GET', new apigateway.LambdaIntegration(appsLambda));
    appIdResource.addMethod('PUT', new apigateway.LambdaIntegration(appsLambda));
    appIdResource.addMethod('DELETE', new apigateway.LambdaIntegration(appsLambda));
    
    const functionResource = appIdResource.addResource('functions').addResource('{functionName}');
    functionResource.addMethod('POST', new apigateway.LambdaIntegration(appsLambda));

    // CloudWatch Alarms
    const apiGateway5xxErrorAlarm = new cloudwatch.Alarm(this, 'ApiGateway5xxErrorAlarm', {
      metric: this.api.metricServerError(),
      threshold: 5,
      evaluationPeriods: 1,
      alarmDescription: 'API Gateway 5xx Error Alarm',
    });

    const apiGateway4xxErrorAlarm = new cloudwatch.Alarm(this, 'ApiGateway4xxErrorAlarm', {
      metric: this.api.metricClientError(),
      threshold: 50,
      evaluationPeriods: 1,
      alarmDescription: 'API Gateway 4xx Error Alarm',
    });

    // Outputs
    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: this.api.url,
      description: 'API Gateway Endpoint',
    });
  }
}
