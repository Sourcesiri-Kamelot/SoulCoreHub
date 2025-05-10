import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as route53 from 'aws-cdk-lib/aws-route53';
import * as route53Targets from 'aws-cdk-lib/aws-route53-targets';
import * as acm from 'aws-cdk-lib/aws-certificatemanager';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

interface Route53StackProps extends cdk.StackProps {
  api: apigateway.RestApi;
  domainName: string;
}

export class Route53Stack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: Route53StackProps) {
    super(scope, id, props);

    // Create a hosted zone for the domain
    const hostedZone = new route53.HostedZone(this, 'HostedZone', {
      zoneName: props.domainName,
    });

    // Create a certificate for the domain
    const certificate = new acm.Certificate(this, 'Certificate', {
      domainName: props.domainName,
      validation: acm.CertificateValidation.fromDns(hostedZone),
    });

    // Create a domain name for the API
    const apiDomainName = new apigateway.DomainName(this, 'ApiDomainName', {
      domainName: props.domainName,
      certificate,
      endpointType: apigateway.EndpointType.REGIONAL,
    });

    // Map the API to the domain name
    new apigateway.BasePathMapping(this, 'ApiPathMapping', {
      domainName: apiDomainName,
      restApi: props.api,
      stage: props.api.deploymentStage,
    });

    // Create an A record for the domain
    new route53.ARecord(this, 'ApiARecord', {
      zone: hostedZone,
      recordName: props.domainName,
      target: route53.RecordTarget.fromAlias(
        new route53Targets.ApiGatewayDomain(apiDomainName)
      ),
    });

    // Create outputs
    new cdk.CfnOutput(this, 'DomainName', {
      value: props.domainName,
      description: 'Domain Name',
    });

    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: `https://${props.domainName}`,
      description: 'API Endpoint',
    });
  }
}
