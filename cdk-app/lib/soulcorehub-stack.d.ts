import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
export declare class SoulCoreHubStack extends cdk.Stack {
    readonly api: apigateway.RestApi;
    constructor(scope: Construct, id: string, props?: cdk.StackProps);
}
