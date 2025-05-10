#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { SoulCoreHubStack } from '../lib/soulcorehub-stack';
import { CodeCatalystStack } from '../lib/codecatalyst-stack';
import { Route53Stack } from '../lib/route53-stack';

const app = new cdk.App();

// Create the main stack
const mainStack = new SoulCoreHubStack(app, 'SoulCoreHubStack', {
  env: { 
    account: process.env.CDK_DEFAULT_ACCOUNT, 
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1' 
  },
  description: 'SoulCoreHub API and infrastructure',
});

// Create the CodeCatalyst stack
new CodeCatalystStack(app, 'SoulCoreHubCodeCatalystStack', {
  env: { 
    account: process.env.CDK_DEFAULT_ACCOUNT, 
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1' 
  },
  description: 'SoulCoreHub CodeCatalyst integration',
});

// Create the Route53 stack for the domain
// Uncomment and configure when ready to deploy to a domain
/*
new Route53Stack(app, 'SoulCoreHubRoute53Stack', {
  env: { 
    account: process.env.CDK_DEFAULT_ACCOUNT, 
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1' 
  },
  description: 'SoulCoreHub Route53 configuration',
  api: mainStack.api,
  domainName: 'soulcorehub.io',
});
*/

app.synth();
