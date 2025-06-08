/**
 * AWS Configuration for SoulCoreHub
 * 
 * This file contains the configuration for AWS services used by SoulCoreHub.
 * Update this file with your own AWS credentials and configuration.
 */

const awsConfig = {
  region: 'us-east-1',
  
  // Cognito Configuration
  cognito: {
    userPoolId: 'us-east-1_4iW9zojRV',
    userPoolWebClientId: 'mp1mucehilvra2etlit8va28r',
    identityPoolId: 'us-east-1:dbf96a34-473b-4c4f-a121-9c12a47c3a80',
  },
  
  // API Gateway Configuration (to be updated when API Gateway is set up)
  apiGateway: {
    REGION: 'us-east-1',
    URL: '',
  },
  
  // CodeBuild Configuration
  codeBuild: {
    projectName: 'SoulCoreHub-Builder',
  },
  
  // CodeStar Connection Configuration
  codeStarConnection: {
    connectionArn: 'arn:aws:codestar-connections:us-east-1:699475940746:connection/90d3ce92-a56e-4d2b-bde4-a84ac55e1bb4',
  },
};

module.exports = awsConfig;
