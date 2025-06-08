package com.soulcorehub.lambda.agent;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.soulcorehub.api.GetAgentInput;
import com.soulcorehub.api.GetAgentOutput;
import com.soulcorehub.api.Agent;
import com.soulcorehub.api.AgentStatus;
import com.soulcorehub.lambda.util.DynamoDbClient;
import com.soulcorehub.lambda.exception.ResourceNotFoundException;

import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.GetItemRequest;
import software.amazon.awssdk.services.dynamodb.model.GetItemResponse;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Lambda handler for GetAgent operation
 */
public class GetAgentHandler implements RequestHandler<GetAgentInput, GetAgentOutput> {
    private static final Logger logger = LoggerFactory.getLogger(GetAgentHandler.class);
    private static final String TABLE_NAME = System.getenv("AGENTS_TABLE_NAME");
    private final DynamoDbClient dynamoDbClient;

    public GetAgentHandler() {
        this.dynamoDbClient = new DynamoDbClient();
    }

    @Override
    public GetAgentOutput handleRequest(GetAgentInput input, Context context) {
        logger.info("Processing GetAgent request for agentId: {}", input.getAgentId());
        
        // Validate input
        if (input.getAgentId() == null || input.getAgentId().isEmpty()) {
            throw new IllegalArgumentException("Agent ID cannot be null or empty");
        }
        
        // Create request to get item from DynamoDB
        Map<String, AttributeValue> key = new HashMap<>();
        key.put("agentId", AttributeValue.builder().s(input.getAgentId()).build());
        
        GetItemRequest request = GetItemRequest.builder()
                .tableName(TABLE_NAME)
                .key(key)
                .build();
        
        // Get item from DynamoDB
        GetItemResponse response = dynamoDbClient.getClient().getItem(request);
        
        // Check if item exists
        if (response.item() == null || response.item().isEmpty()) {
            throw new ResourceNotFoundException("Agent not found", "Agent", input.getAgentId());
        }
        
        // Convert DynamoDB item to Agent
        Agent agent = mapToAgent(response.item());
        
        // Create and return output
        GetAgentOutput output = new GetAgentOutput();
        output.setAgent(agent);
        
        logger.info("Successfully retrieved agent: {}", agent.getAgentId());
        return output;
    }
    
    /**
     * Maps a DynamoDB item to an Agent
     */
    private Agent mapToAgent(Map<String, AttributeValue> item) {
        Agent agent = new Agent();
        
        agent.setAgentId(item.get("agentId").s());
        agent.setName(item.get("name").s());
        agent.setType(item.get("type").s());
        
        if (item.containsKey("description")) {
            agent.setDescription(item.get("description").s());
        }
        
        if (item.containsKey("configuration")) {
            agent.setConfiguration(item.get("configuration").s());
        }
        
        if (item.containsKey("capabilities")) {
            List<String> capabilities = item.get("capabilities").l().stream()
                    .map(AttributeValue::s)
                    .collect(Collectors.toList());
            agent.setCapabilities(capabilities);
        }
        
        agent.setStatus(AgentStatus.valueOf(item.get("status").s()));
        agent.setCreatedAt(item.get("createdAt").s());
        
        if (item.containsKey("updatedAt")) {
            agent.setUpdatedAt(item.get("updatedAt").s());
        }
        
        if (item.containsKey("tags")) {
            Map<String, String> tags = new HashMap<>();
            item.get("tags").m().forEach((key, value) -> tags.put(key, value.s()));
            agent.setTags(tags);
        }
        
        return agent;
    }
}
