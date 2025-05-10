"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Route53Stack = void 0;
const cdk = require("aws-cdk-lib");
const route53 = require("aws-cdk-lib/aws-route53");
const route53Targets = require("aws-cdk-lib/aws-route53-targets");
const acm = require("aws-cdk-lib/aws-certificatemanager");
const apigateway = require("aws-cdk-lib/aws-apigateway");
class Route53Stack extends cdk.Stack {
    constructor(scope, id, props) {
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
            target: route53.RecordTarget.fromAlias(new route53Targets.ApiGatewayDomain(apiDomainName)),
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
exports.Route53Stack = Route53Stack;
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoicm91dGU1My1zdGFjay5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzIjpbInJvdXRlNTMtc3RhY2sudHMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6Ijs7O0FBQUEsbUNBQW1DO0FBRW5DLG1EQUFtRDtBQUNuRCxrRUFBa0U7QUFDbEUsMERBQTBEO0FBQzFELHlEQUF5RDtBQU96RCxNQUFhLFlBQWEsU0FBUSxHQUFHLENBQUMsS0FBSztJQUN6QyxZQUFZLEtBQWdCLEVBQUUsRUFBVSxFQUFFLEtBQXdCO1FBQ2hFLEtBQUssQ0FBQyxLQUFLLEVBQUUsRUFBRSxFQUFFLEtBQUssQ0FBQyxDQUFDO1FBRXhCLHNDQUFzQztRQUN0QyxNQUFNLFVBQVUsR0FBRyxJQUFJLE9BQU8sQ0FBQyxVQUFVLENBQUMsSUFBSSxFQUFFLFlBQVksRUFBRTtZQUM1RCxRQUFRLEVBQUUsS0FBSyxDQUFDLFVBQVU7U0FDM0IsQ0FBQyxDQUFDO1FBRUgsc0NBQXNDO1FBQ3RDLE1BQU0sV0FBVyxHQUFHLElBQUksR0FBRyxDQUFDLFdBQVcsQ0FBQyxJQUFJLEVBQUUsYUFBYSxFQUFFO1lBQzNELFVBQVUsRUFBRSxLQUFLLENBQUMsVUFBVTtZQUM1QixVQUFVLEVBQUUsR0FBRyxDQUFDLHFCQUFxQixDQUFDLE9BQU8sQ0FBQyxVQUFVLENBQUM7U0FDMUQsQ0FBQyxDQUFDO1FBRUgsbUNBQW1DO1FBQ25DLE1BQU0sYUFBYSxHQUFHLElBQUksVUFBVSxDQUFDLFVBQVUsQ0FBQyxJQUFJLEVBQUUsZUFBZSxFQUFFO1lBQ3JFLFVBQVUsRUFBRSxLQUFLLENBQUMsVUFBVTtZQUM1QixXQUFXO1lBQ1gsWUFBWSxFQUFFLFVBQVUsQ0FBQyxZQUFZLENBQUMsUUFBUTtTQUMvQyxDQUFDLENBQUM7UUFFSCxpQ0FBaUM7UUFDakMsSUFBSSxVQUFVLENBQUMsZUFBZSxDQUFDLElBQUksRUFBRSxnQkFBZ0IsRUFBRTtZQUNyRCxVQUFVLEVBQUUsYUFBYTtZQUN6QixPQUFPLEVBQUUsS0FBSyxDQUFDLEdBQUc7WUFDbEIsS0FBSyxFQUFFLEtBQUssQ0FBQyxHQUFHLENBQUMsZUFBZTtTQUNqQyxDQUFDLENBQUM7UUFFSCxvQ0FBb0M7UUFDcEMsSUFBSSxPQUFPLENBQUMsT0FBTyxDQUFDLElBQUksRUFBRSxZQUFZLEVBQUU7WUFDdEMsSUFBSSxFQUFFLFVBQVU7WUFDaEIsVUFBVSxFQUFFLEtBQUssQ0FBQyxVQUFVO1lBQzVCLE1BQU0sRUFBRSxPQUFPLENBQUMsWUFBWSxDQUFDLFNBQVMsQ0FDcEMsSUFBSSxjQUFjLENBQUMsZ0JBQWdCLENBQUMsYUFBYSxDQUFDLENBQ25EO1NBQ0YsQ0FBQyxDQUFDO1FBRUgsaUJBQWlCO1FBQ2pCLElBQUksR0FBRyxDQUFDLFNBQVMsQ0FBQyxJQUFJLEVBQUUsWUFBWSxFQUFFO1lBQ3BDLEtBQUssRUFBRSxLQUFLLENBQUMsVUFBVTtZQUN2QixXQUFXLEVBQUUsYUFBYTtTQUMzQixDQUFDLENBQUM7UUFFSCxJQUFJLEdBQUcsQ0FBQyxTQUFTLENBQUMsSUFBSSxFQUFFLGFBQWEsRUFBRTtZQUNyQyxLQUFLLEVBQUUsV0FBVyxLQUFLLENBQUMsVUFBVSxFQUFFO1lBQ3BDLFdBQVcsRUFBRSxjQUFjO1NBQzVCLENBQUMsQ0FBQztJQUNMLENBQUM7Q0FDRjtBQWpERCxvQ0FpREMiLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgKiBhcyBjZGsgZnJvbSAnYXdzLWNkay1saWInO1xuaW1wb3J0IHsgQ29uc3RydWN0IH0gZnJvbSAnY29uc3RydWN0cyc7XG5pbXBvcnQgKiBhcyByb3V0ZTUzIGZyb20gJ2F3cy1jZGstbGliL2F3cy1yb3V0ZTUzJztcbmltcG9ydCAqIGFzIHJvdXRlNTNUYXJnZXRzIGZyb20gJ2F3cy1jZGstbGliL2F3cy1yb3V0ZTUzLXRhcmdldHMnO1xuaW1wb3J0ICogYXMgYWNtIGZyb20gJ2F3cy1jZGstbGliL2F3cy1jZXJ0aWZpY2F0ZW1hbmFnZXInO1xuaW1wb3J0ICogYXMgYXBpZ2F0ZXdheSBmcm9tICdhd3MtY2RrLWxpYi9hd3MtYXBpZ2F0ZXdheSc7XG5cbmludGVyZmFjZSBSb3V0ZTUzU3RhY2tQcm9wcyBleHRlbmRzIGNkay5TdGFja1Byb3BzIHtcbiAgYXBpOiBhcGlnYXRld2F5LlJlc3RBcGk7XG4gIGRvbWFpbk5hbWU6IHN0cmluZztcbn1cblxuZXhwb3J0IGNsYXNzIFJvdXRlNTNTdGFjayBleHRlbmRzIGNkay5TdGFjayB7XG4gIGNvbnN0cnVjdG9yKHNjb3BlOiBDb25zdHJ1Y3QsIGlkOiBzdHJpbmcsIHByb3BzOiBSb3V0ZTUzU3RhY2tQcm9wcykge1xuICAgIHN1cGVyKHNjb3BlLCBpZCwgcHJvcHMpO1xuXG4gICAgLy8gQ3JlYXRlIGEgaG9zdGVkIHpvbmUgZm9yIHRoZSBkb21haW5cbiAgICBjb25zdCBob3N0ZWRab25lID0gbmV3IHJvdXRlNTMuSG9zdGVkWm9uZSh0aGlzLCAnSG9zdGVkWm9uZScsIHtcbiAgICAgIHpvbmVOYW1lOiBwcm9wcy5kb21haW5OYW1lLFxuICAgIH0pO1xuXG4gICAgLy8gQ3JlYXRlIGEgY2VydGlmaWNhdGUgZm9yIHRoZSBkb21haW5cbiAgICBjb25zdCBjZXJ0aWZpY2F0ZSA9IG5ldyBhY20uQ2VydGlmaWNhdGUodGhpcywgJ0NlcnRpZmljYXRlJywge1xuICAgICAgZG9tYWluTmFtZTogcHJvcHMuZG9tYWluTmFtZSxcbiAgICAgIHZhbGlkYXRpb246IGFjbS5DZXJ0aWZpY2F0ZVZhbGlkYXRpb24uZnJvbURucyhob3N0ZWRab25lKSxcbiAgICB9KTtcblxuICAgIC8vIENyZWF0ZSBhIGRvbWFpbiBuYW1lIGZvciB0aGUgQVBJXG4gICAgY29uc3QgYXBpRG9tYWluTmFtZSA9IG5ldyBhcGlnYXRld2F5LkRvbWFpbk5hbWUodGhpcywgJ0FwaURvbWFpbk5hbWUnLCB7XG4gICAgICBkb21haW5OYW1lOiBwcm9wcy5kb21haW5OYW1lLFxuICAgICAgY2VydGlmaWNhdGUsXG4gICAgICBlbmRwb2ludFR5cGU6IGFwaWdhdGV3YXkuRW5kcG9pbnRUeXBlLlJFR0lPTkFMLFxuICAgIH0pO1xuXG4gICAgLy8gTWFwIHRoZSBBUEkgdG8gdGhlIGRvbWFpbiBuYW1lXG4gICAgbmV3IGFwaWdhdGV3YXkuQmFzZVBhdGhNYXBwaW5nKHRoaXMsICdBcGlQYXRoTWFwcGluZycsIHtcbiAgICAgIGRvbWFpbk5hbWU6IGFwaURvbWFpbk5hbWUsXG4gICAgICByZXN0QXBpOiBwcm9wcy5hcGksXG4gICAgICBzdGFnZTogcHJvcHMuYXBpLmRlcGxveW1lbnRTdGFnZSxcbiAgICB9KTtcblxuICAgIC8vIENyZWF0ZSBhbiBBIHJlY29yZCBmb3IgdGhlIGRvbWFpblxuICAgIG5ldyByb3V0ZTUzLkFSZWNvcmQodGhpcywgJ0FwaUFSZWNvcmQnLCB7XG4gICAgICB6b25lOiBob3N0ZWRab25lLFxuICAgICAgcmVjb3JkTmFtZTogcHJvcHMuZG9tYWluTmFtZSxcbiAgICAgIHRhcmdldDogcm91dGU1My5SZWNvcmRUYXJnZXQuZnJvbUFsaWFzKFxuICAgICAgICBuZXcgcm91dGU1M1RhcmdldHMuQXBpR2F0ZXdheURvbWFpbihhcGlEb21haW5OYW1lKVxuICAgICAgKSxcbiAgICB9KTtcblxuICAgIC8vIENyZWF0ZSBvdXRwdXRzXG4gICAgbmV3IGNkay5DZm5PdXRwdXQodGhpcywgJ0RvbWFpbk5hbWUnLCB7XG4gICAgICB2YWx1ZTogcHJvcHMuZG9tYWluTmFtZSxcbiAgICAgIGRlc2NyaXB0aW9uOiAnRG9tYWluIE5hbWUnLFxuICAgIH0pO1xuXG4gICAgbmV3IGNkay5DZm5PdXRwdXQodGhpcywgJ0FwaUVuZHBvaW50Jywge1xuICAgICAgdmFsdWU6IGBodHRwczovLyR7cHJvcHMuZG9tYWluTmFtZX1gLFxuICAgICAgZGVzY3JpcHRpb246ICdBUEkgRW5kcG9pbnQnLFxuICAgIH0pO1xuICB9XG59XG4iXX0=