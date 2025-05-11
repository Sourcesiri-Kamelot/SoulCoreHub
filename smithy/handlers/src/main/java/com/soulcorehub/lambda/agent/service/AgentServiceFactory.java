package com.soulcorehub.lambda.agent.service;

import java.util.HashMap;
import java.util.Map;

/**
 * Factory for creating agent services
 */
public class AgentServiceFactory {
    private final Map<String, AgentService> serviceMap;

    public AgentServiceFactory() {
        serviceMap = new HashMap<>();
        serviceMap.put("GPTSoul", new GPTSoulAgentService());
        serviceMap.put("Anima", new AnimaAgentService());
        serviceMap.put("EvoVe", new EvoVeAgentService());
        serviceMap.put("Azur", new AzurAgentService());
        serviceMap.put("default", new DefaultAgentService());
    }

    /**
     * Gets an agent service for the specified agent type
     *
     * @param agentType The type of agent
     * @return An agent service
     */
    public AgentService getAgentService(String agentType) {
        return serviceMap.getOrDefault(agentType, serviceMap.get("default"));
    }
}
