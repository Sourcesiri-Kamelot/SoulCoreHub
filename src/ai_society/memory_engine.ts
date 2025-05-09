/**
 * Memory Engine for SoulCoreHub AI Society
 * 
 * This module provides persistent memory capabilities for agents, including:
 * - Storing and retrieving memories
 * - Managing relationships between agents
 * - Summarizing memories for agent context
 */

import { DynamoDB } from 'aws-sdk';
import { v4 as uuidv4 } from 'uuid';

/**
 * Memory structure for agent memories
 */
export interface Memory {
  id: string;
  agentId: string;
  type: 'conversation' | 'relationship' | 'event' | 'reflection';
  content: any;
  emotionalTone?: string;
  importance: number; // 1-10
  timestamp: string;
  tags: string[];
}

/**
 * Relationship structure between agents
 */
export interface Relationship {
  targetId: string;
  sentiment: number; // -10 to 10
  trust: number; // 0 to 10
  familiarity: number; // 0 to 10
  lastInteraction: string;
  notes: string[];
}

/**
 * Memory Engine class for managing agent memories
 */
export class MemoryEngine {
  private dynamoDB: DynamoDB.DocumentClient;
  private tableName: string = 'SoulCoreHub-AgentMemory';
  private memoryCache: Map<string, Memory[]> = new Map();
  
  /**
   * Initialize the Memory Engine
   */
  constructor() {
    this.dynamoDB = new DynamoDB.DocumentClient({
      region: process.env.AWS_REGION || 'us-east-1'
    });
  }
  
  /**
   * Store a new memory for an agent
   * @param agentId ID of the agent
   * @param memory Memory to store
   * @returns ID of the stored memory
   */
  async storeMemory(agentId: string, memory: Partial<Memory>): Promise<string> {
    const memoryId = uuidv4();
    const timestamp = new Date().toISOString();
    
    const completeMemory: Memory = {
      id: memoryId,
      agentId,
      type: memory.type || 'event',
      content: memory.content,
      emotionalTone: memory.emotionalTone || 'neutral',
      importance: memory.importance || 5,
      timestamp,
      tags: memory.tags || []
    };
    
    try {
      await this.dynamoDB.put({
        TableName: this.tableName,
        Item: completeMemory
      }).promise();
      
      // Update cache
      if (this.memoryCache.has(agentId)) {
        this.memoryCache.get(agentId)?.push(completeMemory);
      }
      
      console.log(`Stored memory for agent ${agentId}: ${JSON.stringify(completeMemory)}`);
      return memoryId;
    } catch (error) {
      console.error(`Failed to store memory for agent ${agentId}`, error);
      throw error;
    }
  }
  
  /**
   * Get memories for an agent with optional filtering
   * @param agentId ID of the agent
   * @param options Filter options
   * @returns Array of memories
   */
  async getMemories(agentId: string, options: {
    limit?: number;
    type?: 'conversation' | 'relationship' | 'event' | 'reflection';
    minImportance?: number;
    tags?: string[];
    since?: string;
  } = {}): Promise<Memory[]> {
    try {
      // Try to use cache first
      if (this.memoryCache.has(agentId)) {
        const cachedMemories = this.memoryCache.get(agentId) || [];
        return this.filterMemories(cachedMemories, options);
      }
      
      // Query DynamoDB
      const params: DynamoDB.DocumentClient.QueryInput = {
        TableName: this.tableName,
        KeyConditionExpression: 'agentId = :agentId',
        ExpressionAttributeValues: {
          ':agentId': agentId
        },
        ScanIndexForward: false // newest first
      };
      
      const result = await this.dynamoDB.query(params).promise();
      const memories = result.Items as Memory[];
      
      // Update cache
      this.memoryCache.set(agentId, memories);
      
      return this.filterMemories(memories, options);
    } catch (error) {
      console.error(`Failed to get memories for agent ${agentId}`, error);
      return [];
    }
  }
  
  /**
   * Update or create a relationship between agents
   * @param agentId ID of the agent
   * @param targetId ID of the target agent
   * @param changes Changes to apply to the relationship
   */
  async updateRelationship(agentId: string, targetId: string, changes: Partial<Relationship>): Promise<void> {
    try {
      // Get existing relationship or create new one
      const relationships = await this.getMemories(agentId, { 
        type: 'relationship',
        tags: [targetId]
      });
      
      let relationship: Relationship;
      let memoryId: string;
      
      if (relationships.length > 0) {
        relationship = relationships[0].content as Relationship;
        memoryId = relationships[0].id;
        
        // Update existing relationship
        Object.assign(relationship, changes);
        relationship.lastInteraction = new Date().toISOString();
        
        // Update in DynamoDB
        await this.dynamoDB.update({
          TableName: this.tableName,
          Key: { id: memoryId, agentId },
          UpdateExpression: 'set content = :content, timestamp = :timestamp',
          ExpressionAttributeValues: {
            ':content': relationship,
            ':timestamp': new Date().toISOString()
          }
        }).promise();
      } else {
        // Create new relationship
        relationship = {
          targetId,
          sentiment: changes.sentiment || 0,
          trust: changes.trust || 0,
          familiarity: changes.familiarity || 0,
          lastInteraction: new Date().toISOString(),
          notes: changes.notes || []
        };
        
        await this.storeMemory(agentId, {
          type: 'relationship',
          content: relationship,
          importance: 7,
          tags: [targetId, 'relationship']
        });
      }
      
      console.log(`Updated relationship for agent ${agentId} with ${targetId}: ${JSON.stringify(relationship)}`);
    } catch (error) {
      console.error(`Failed to update relationship for agent ${agentId} with ${targetId}`, error);
      throw error;
    }
  }
  
  /**
   * Get a summary of an agent's memories
   * @param agentId ID of the agent
   * @returns Summary text
   */
  async summarizeMemories(agentId: string): Promise<string> {
    // Get important memories
    const memories = await this.getMemories(agentId, { minImportance: 6 });
    
    if (memories.length === 0) {
      return "No significant memories.";
    }
    
    // Group by type
    const byType = memories.reduce((acc, memory) => {
      if (!acc[memory.type]) {
        acc[memory.type] = [];
      }
      acc[memory.type].push(memory);
      return acc;
    }, {} as Record<string, Memory[]>);
    
    // Create summary
    let summary = `Memory summary for ${agentId}:\n\n`;
    
    if (byType.relationship) {
      summary += "Relationships:\n";
      byType.relationship.forEach(memory => {
        const rel = memory.content as Relationship;
        summary += `- ${rel.targetId}: Sentiment ${rel.sentiment}, Trust ${rel.trust}\n`;
      });
      summary += "\n";
    }
    
    if (byType.event) {
      summary += "Key Events:\n";
      byType.event.slice(0, 5).forEach(memory => {
        summary += `- ${memory.timestamp}: ${JSON.stringify(memory.content)}\n`;
      });
      summary += "\n";
    }
    
    if (byType.reflection) {
      summary += "Recent Reflections:\n";
      byType.reflection.slice(0, 3).forEach(memory => {
        summary += `- ${memory.content}\n`;
      });
    }
    
    return summary;
  }
  
  /**
   * Filter memories based on options
   * @param memories Memories to filter
   * @param options Filter options
   * @returns Filtered memories
   */
  private filterMemories(memories: Memory[], options: {
    limit?: number;
    type?: 'conversation' | 'relationship' | 'event' | 'reflection';
    minImportance?: number;
    tags?: string[];
    since?: string;
  }): Memory[] {
    let filtered = [...memories];
    
    if (options.type) {
      filtered = filtered.filter(m => m.type === options.type);
    }
    
    if (options.minImportance !== undefined) {
      filtered = filtered.filter(m => m.importance >= options.minImportance);
    }
    
    if (options.tags && options.tags.length > 0) {
      filtered = filtered.filter(m => 
        options.tags!.some(tag => m.tags.includes(tag))
      );
    }
    
    if (options.since) {
      filtered = filtered.filter(m => m.timestamp >= options.since);
    }
    
    if (options.limit) {
      filtered = filtered.slice(0, options.limit);
    }
    
    return filtered;
  }
}
