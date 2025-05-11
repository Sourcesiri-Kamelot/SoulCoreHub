package com.soulcorehub.lambda.util;

import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.DynamoDbClientBuilder;

/**
 * Utility class for DynamoDB client
 */
public class DynamoDbClient {
    private final DynamoDbClient client;

    public DynamoDbClient() {
        // Get region from environment variable or use default
        String regionName = System.getenv("AWS_REGION");
        Region region = regionName != null ? Region.of(regionName) : Region.US_EAST_1;
        
        // Create DynamoDB client builder
        DynamoDbClientBuilder builder = DynamoDbClient.builder().region(region);
        
        // Check if running locally with DynamoDB local
        String endpointOverride = System.getenv("DYNAMODB_ENDPOINT");
        if (endpointOverride != null && !endpointOverride.isEmpty()) {
            builder.endpointOverride(java.net.URI.create(endpointOverride));
        }
        
        // Build client
        this.client = builder.build();
    }

    /**
     * Gets the DynamoDB client
     *
     * @return The DynamoDB client
     */
    public DynamoDbClient getClient() {
        return client;
    }
}
