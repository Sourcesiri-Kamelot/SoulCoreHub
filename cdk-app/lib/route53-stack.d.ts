import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
interface Route53StackProps extends cdk.StackProps {
    api: apigateway.RestApi;
    domainName: string;
}
export declare class Route53Stack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: Route53StackProps);
}
export {};
