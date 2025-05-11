package com.soulcorehub.lambda.agent.service;

import java.util.Map;

/**
 * Interface for agent services
 */
public interface AgentService {
    /**
     * Invokes an agent with a prompt
     *
     * @param agentId     The ID of the agent to invoke
     * @param prompt      The prompt to send to the agent
     * @param parameters  Additional parameters for the agent
     * @param context     Context for the agent
     * @param maxTokens   Maximum tokens to generate
     * @param temperature Temperature for generation
     * @return A map containing the response and metadata
     */
    Map<String, Object> invokeAgent(
            String agentId,
            String prompt,
            Map<String, String> parameters,
            String context,
            Integer maxTokens,
            Float temperature
    );
}
