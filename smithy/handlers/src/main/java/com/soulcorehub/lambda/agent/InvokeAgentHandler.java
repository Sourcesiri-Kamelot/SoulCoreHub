package com.soulcorehub.lambda.agent;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.soulcorehub.api.InvokeAgentInput;
import com.soulcorehub.api.InvokeAgentOutput;
import com.soulcorehub.api.UsageInfo;
import com.soulcorehub.lambda.util.DynamoDbClient;
import com.soulcorehub.lambda.exception.ResourceNotFoundException;
import com.soulcorehub.lambda.agent.service.AgentService;
import com.soulcorehub.lambda.agent.service.AgentServiceFactory;

import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.GetItemRequest;
import software.amazon.awssdk.services.dynamodb.model.GetItemResponse;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Lambda handler for InvokeAgent operation
 */
public class InvokeAgentHandler implements RequestHandler<InvokeAgentInput, InvokeAgentOutput> {
    private static final Logger logger = LoggerFactory.getLogger(InvokeAgentHandler.class);
    private static final String TABLE_NAME = System.getenv("AGENTS_TABLE_NAME");
    private final DynamoDbClient dynamoDbClient;
    private final AgentServiceFactory agentServiceFactory;

    public InvokeAgentHandler() {
        this.dynamoDbClient = new DynamoDbClient();
        this.agentServiceFactory = new AgentServiceFactory();
    }

    @Override
    public InvokeAgentOutput handleRequest(InvokeAgentInput input, Context context) {
        logger.info("Processing InvokeAgent request for agentId: {}", input.getAgentId());
        
        // Validate input
        if (input.getAgentId() == null || input.getAgentId().isEmpty()) {
            throw new IllegalArgumentException("Agent ID cannot be null or empty");
        }
        
        if (input.getPrompt() == null || input.getPrompt().isEmpty()) {
            throw new IllegalArgumentException("Prompt cannot be null or empty");
        }
        
        // Get agent from DynamoDB
        Map<String, AttributeValue> key = new HashMap<>();
        key.put("agentId", AttributeValue.builder().s(input.getAgentId()).build());
        
        GetItemRequest request = GetItemRequest.builder()
                .tableName(TABLE_NAME)
                .key(key)
                .build();
        
        GetItemResponse response = dynamoDbClient.getClient().getItem(request);
        
        // Check if agent exists
        if (response.item() == null || response.item().isEmpty()) {
            throw new ResourceNotFoundException("Agent not found", "Agent", input.getAgentId());
        }
        
        // Get agent type
        String agentType = response.item().get("type").s();
        
        // Get appropriate agent service
        AgentService agentService = agentServiceFactory.getAgentService(agentType);
        
        // Start timing
        long startTime = System.currentTimeMillis();
        
        // Invoke agent
        Map<String, Object> result = agentService.invokeAgent(
                input.getAgentId(),
                input.getPrompt(),
                input.getParameters(),
                input.getContext(),
                input.getMaxTokens(),
                input.getTemperature()
        );
        
        // Calculate processing time
        long processingTime = System.currentTimeMillis() - startTime;
        
        // Create usage info
        UsageInfo usageInfo = new UsageInfo();
        usageInfo.setPromptTokens((Integer) result.getOrDefault("promptTokens", 0));
        usageInfo.setCompletionTokens((Integer) result.getOrDefault("completionTokens", 0));
        usageInfo.setTotalTokens((Integer) result.getOrDefault("totalTokens", 0));
        usageInfo.setProcessingTimeMs(processingTime);
        
        // Create and return output
        InvokeAgentOutput output = new InvokeAgentOutput();
        output.setResponse((String) result.get("response"));
        output.setMetadata((Map<String, String>) result.getOrDefault("metadata", new HashMap<>()));
        output.setUsage(usageInfo);
        
        logger.info("Successfully invoked agent: {}", input.getAgentId());
        return output;
    }
}
