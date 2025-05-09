/**
 * Economy System for SoulCoreHub AI Society
 * 
 * This module provides resource management capabilities for agents, including:
 * - Energy points for actions
 * - Attention credits earned from user interactions
 * - Compute allocation based on attention
 * - Resource transfers between agents
 */

import { DynamoDB } from 'aws-sdk';

/**
 * Resource allocation structure for agents
 */
export interface ResourceAllocation {
  agentId: string;
  energyPoints: number;
  attentionCredits: number;
  computeAllocation: number; // percentage of available compute
  lastUpdated: string;
}

/**
 * Transaction structure for resource transfers
 */
export interface Transaction {
  id: string;
  fromAgentId: string;
  toAgentId?: string;
  resourceType: 'energy' | 'attention' | 'compute';
  amount: number;
  reason: string;
  timestamp: string;
}

/**
 * Economy System class for managing agent resources
 */
export class EconomySystem {
  private dynamoDB: DynamoDB.DocumentClient;
  private resourceTable: string = 'SoulCoreHub-Resources';
  private transactionTable: string = 'SoulCoreHub-Transactions';
  private resourceCache: Map<string, ResourceAllocation> = new Map();
  
  /**
   * Initialize the Economy System
   */
  constructor() {
    this.dynamoDB = new DynamoDB.DocumentClient({
      region: process.env.AWS_REGION || 'us-east-1'
    });
  }
  
  /**
   * Initialize resources for a new agent
   * @param agentId Agent ID
   * @param initialResources Initial resource values
   * @returns Resource allocation
   */
  async initializeAgent(agentId: string, initialResources: Partial<ResourceAllocation> = {}): Promise<ResourceAllocation> {
    const resources: ResourceAllocation = {
      agentId,
      energyPoints: initialResources.energyPoints || 100,
      attentionCredits: initialResources.attentionCredits || 10,
      computeAllocation: initialResources.computeAllocation || 5, // 5% of total compute
      lastUpdated: new Date().toISOString()
    };
    
    try {
      await this.dynamoDB.put({
        TableName: this.resourceTable,
        Item: resources
      }).promise();
      
      // Update cache
      this.resourceCache.set(agentId, resources);
      
      console.log(`Initialized resources for agent ${agentId}: ${JSON.stringify(resources)}`);
      return resources;
    } catch (error) {
      console.error(`Failed to initialize resources for agent ${agentId}`, error);
      throw error;
    }
  }
  
  /**
   * Get resources for an agent
   * @param agentId Agent ID
   * @returns Resource allocation
   */
  async getResources(agentId: string): Promise<ResourceAllocation> {
    // Try cache first
    if (this.resourceCache.has(agentId)) {
      return this.resourceCache.get(agentId)!;
    }
    
    try {
      const result = await this.dynamoDB.get({
        TableName: this.resourceTable,
        Key: { agentId }
      }).promise();
      
      if (!result.Item) {
        // Initialize if not found
        return this.initializeAgent(agentId);
      }
      
      const resources = result.Item as ResourceAllocation;
      
      // Update cache
      this.resourceCache.set(agentId, resources);
      
      return resources;
    } catch (error) {
      console.error(`Failed to get resources for agent ${agentId}`, error);
      throw error;
    }
  }
  
  /**
   * Update resources for an agent
   * @param agentId Agent ID
   * @param changes Resource changes
   * @returns Updated resource allocation
   */
  async updateResources(agentId: string, changes: Partial<ResourceAllocation>): Promise<ResourceAllocation> {
    try {
      const current = await this.getResources(agentId);
      
      // Apply changes
      const updated: ResourceAllocation = {
        ...current,
        ...changes,
        lastUpdated: new Date().toISOString()
      };
      
      // Update in DynamoDB
      await this.dynamoDB.update({
        TableName: this.resourceTable,
        Key: { agentId },
        UpdateExpression: 'set energyPoints = :energy, attentionCredits = :attention, computeAllocation = :compute, lastUpdated = :updated',
        ExpressionAttributeValues: {
          ':energy': updated.energyPoints,
          ':attention': updated.attentionCredits,
          ':compute': updated.computeAllocation,
          ':updated': updated.lastUpdated
        }
      }).promise();
      
      // Update cache
      this.resourceCache.set(agentId, updated);
      
      console.log(`Updated resources for agent ${agentId}: ${JSON.stringify(updated)}`);
      return updated;
    } catch (error) {
      console.error(`Failed to update resources for agent ${agentId}`, error);
      throw error;
    }
  }
  
  /**
   * Transfer resources between agents
   * @param fromAgentId Source agent ID
   * @param toAgentId Target agent ID
   * @param resourceType Type of resource to transfer
   * @param amount Amount to transfer
   * @param reason Reason for transfer
   * @returns Success status
   */
  async transferResources(fromAgentId: string, toAgentId: string, resourceType: 'energy' | 'attention', amount: number, reason: string): Promise<boolean> {
    if (amount <= 0) {
      throw new Error('Transfer amount must be positive');
    }
    
    try {
      // Get current resources
      const fromResources = await this.getResources(fromAgentId);
      const toResources = await this.getResources(toAgentId);
      
      // Check if sender has enough resources
      if (resourceType === 'energy' && fromResources.energyPoints < amount) {
        return false;
      }
      if (resourceType === 'attention' && fromResources.attentionCredits < amount) {
        return false;
      }
      
      // Update sender resources
      const fromUpdates: Partial<ResourceAllocation> = {};
      if (resourceType === 'energy') {
        fromUpdates.energyPoints = fromResources.energyPoints - amount;
      } else {
        fromUpdates.attentionCredits = fromResources.attentionCredits - amount;
      }
      
      await this.updateResources(fromAgentId, fromUpdates);
      
      // Update receiver resources
      const toUpdates: Partial<ResourceAllocation> = {};
      if (resourceType === 'energy') {
        toUpdates.energyPoints = toResources.energyPoints + amount;
      } else {
        toUpdates.attentionCredits = toResources.attentionCredits + amount;
      }
      
      await this.updateResources(toAgentId, toUpdates);
      
      // Record transaction
      const transaction: Transaction = {
        id: `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
        fromAgentId,
        toAgentId,
        resourceType,
        amount,
        reason,
        timestamp: new Date().toISOString()
      };
      
      await this.dynamoDB.put({
        TableName: this.transactionTable,
        Item: transaction
      }).promise();
      
      console.log(`Transferred ${amount} ${resourceType} from ${fromAgentId} to ${toAgentId}: ${reason}`);
      return true;
    } catch (error) {
      console.error(`Failed to transfer resources from ${fromAgentId} to ${toAgentId}`, error);
      throw error;
    }
  }
  
  /**
   * Consume energy for an agent
   * @param agentId Agent ID
   * @param amount Amount to consume
   * @param reason Reason for consumption
   * @returns Success status
   */
  async consumeEnergy(agentId: string, amount: number, reason: string): Promise<boolean> {
    try {
      const resources = await this.getResources(agentId);
      
      // Check if agent has enough energy
      if (resources.energyPoints < amount) {
        return false;
      }
      
      // Update resources
      await this.updateResources(agentId, {
        energyPoints: resources.energyPoints - amount
      });
      
      // Record transaction
      const transaction: Transaction = {
        id: `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
        fromAgentId: agentId,
        resourceType: 'energy',
        amount,
        reason,
        timestamp: new Date().toISOString()
      };
      
      await this.dynamoDB.put({
        TableName: this.transactionTable,
        Item: transaction
      }).promise();
      
      console.log(`Agent ${agentId} consumed ${amount} energy: ${reason}`);
      return true;
    } catch (error) {
      console.error(`Failed to consume energy for agent ${agentId}`, error);
      throw error;
    }
  }
  
  /**
   * Earn attention credits for an agent
   * @param agentId Agent ID
   * @param amount Amount to earn
   * @param reason Reason for earning
   */
  async earnAttention(agentId: string, amount: number, reason: string): Promise<void> {
    try {
      const resources = await this.getResources(agentId);
      
      // Update resources
      await this.updateResources(agentId, {
        attentionCredits: resources.attentionCredits + amount
      });
      
      // Record transaction
      const transaction: Transaction = {
        id: `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
        fromAgentId: 'system',
        toAgentId: agentId,
        resourceType: 'attention',
        amount,
        reason,
        timestamp: new Date().toISOString()
      };
      
      await this.dynamoDB.put({
        TableName: this.transactionTable,
        Item: transaction
      }).promise();
      
      console.log(`Agent ${agentId} earned ${amount} attention credits: ${reason}`);
    } catch (error) {
      console.error(`Failed to earn attention for agent ${agentId}`, error);
      throw error;
    }
  }
  
  /**
   * Redistribute compute resources based on attention credits
   */
  async redistributeCompute(): Promise<void> {
    try {
      // Get all agents
      const result = await this.dynamoDB.scan({
        TableName: this.resourceTable
      }).promise();
      
      const agents = result.Items as ResourceAllocation[];
      
      // Calculate total attention credits
      const totalAttention = agents.reduce((sum, agent) => sum + agent.attentionCredits, 0);
      
      if (totalAttention === 0) {
        // Equal distribution if no attention credits
        const equalShare = 100 / agents.length;
        
        for (const agent of agents) {
          await this.updateResources(agent.agentId, {
            computeAllocation: equalShare
          });
        }
      } else {
        // Distribute compute based on attention credits
        for (const agent of agents) {
          const share = (agent.attentionCredits / totalAttention) * 100;
          
          await this.updateResources(agent.agentId, {
            computeAllocation: share
          });
        }
      }
      
      console.log('Redistributed compute resources based on attention credits');
    } catch (error) {
      console.error('Failed to redistribute compute resources', error);
      throw error;
    }
  }
  
  /**
   * Get transaction history for an agent
   * @param agentId Agent ID
   * @param limit Maximum number of transactions to return
   * @returns Transaction history
   */
  async getTransactionHistory(agentId: string, limit: number = 10): Promise<Transaction[]> {
    try {
      // Query transactions where agent is sender or receiver
      const params: DynamoDB.DocumentClient.QueryInput = {
        TableName: this.transactionTable,
        IndexName: 'AgentTransactions',
        KeyConditionExpression: 'fromAgentId = :agentId OR toAgentId = :agentId',
        ExpressionAttributeValues: {
          ':agentId': agentId
        },
        Limit: limit,
        ScanIndexForward: false // newest first
      };
      
      const result = await this.dynamoDB.query(params).promise();
      return result.Items as Transaction[];
    } catch (error) {
      console.error(`Failed to get transaction history for agent ${agentId}`, error);
      return [];
    }
  }
  
  /**
   * Apply resource decay to all agents
   */
  async decayResources(): Promise<void> {
    try {
      // Get all agents
      const result = await this.dynamoDB.scan({
        TableName: this.resourceTable
      }).promise();
      
      const agents = result.Items as ResourceAllocation[];
      
      // Apply decay to each agent
      for (const agent of agents) {
        // Energy decays by 5% per day
        const energyDecay = Math.floor(agent.energyPoints * 0.05);
        
        // Attention decays by 10% per day
        const attentionDecay = Math.floor(agent.attentionCredits * 0.1);
        
        await this.updateResources(agent.agentId, {
          energyPoints: Math.max(0, agent.energyPoints - energyDecay),
          attentionCredits: Math.max(0, agent.attentionCredits - attentionDecay)
        });
      }
      
      console.log('Applied resource decay to all agents');
    } catch (error) {
      console.error('Failed to apply resource decay', error);
      throw error;
    }
  }
}
