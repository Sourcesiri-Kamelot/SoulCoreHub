/**
 * Anima Memory - Persistent storage for Anima's emotional memory
 * 
 * This module provides persistent storage for Anima's emotional memory using DynamoDB.
 */

import { db } from '../../database/dynamodb_adapter';
import { Emotion } from './anima_core';
import { v4 as uuidv4 } from 'uuid';

/**
 * Anima Memory class for persistent storage
 */
export class AnimaMemory {
  private tableName = 'SoulCoreHub-AnimaMemory';
  
  /**
   * Initialize Anima Memory
   */
  constructor() {
    this.initTable();
  }
  
  /**
   * Initialize the DynamoDB table
   */
  private async initTable(): Promise<void> {
    await db.createTable(this.tableName, [
      { AttributeName: 'id', KeyType: 'HASH' }
    ]);
  }
  
  /**
   * Store an emotion in memory
   * @param category Memory category
   * @param emotion Emotion to store
   * @returns ID of the stored emotion
   */
  async storeEmotion(category: string, emotion: Emotion): Promise<string> {
    const id = uuidv4();
    
    await db.put(this.tableName, {
      id,
      category,
      emotion,
      timestamp: new Date().toISOString()
    });
    
    return id;
  }
  
  /**
   * Get emotions from memory
   * @param category Memory category
   * @param limit Maximum number of emotions to retrieve
   * @returns Array of emotions
   */
  async getEmotions(category: string, limit: number = 10): Promise<Emotion[]> {
    const items = await db.scan(
      this.tableName,
      'category = :category',
      { ':category': category }
    );
    
    // Sort by timestamp (newest first) and limit
    return items
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, limit)
      .map(item => item.emotion);
  }
  
  /**
   * Store emotional state in memory
   * @param state Emotional state to store
   * @returns ID of the stored state
   */
  async storeEmotionalState(state: any): Promise<string> {
    const id = uuidv4();
    
    await db.put(this.tableName, {
      id,
      category: 'emotional_state',
      state,
      timestamp: new Date().toISOString()
    });
    
    return id;
  }
  
  /**
   * Get the latest emotional state from memory
   * @returns Latest emotional state or null
   */
  async getLatestEmotionalState(): Promise<any> {
    const items = await db.scan(
      this.tableName,
      'category = :category',
      { ':category': 'emotional_state' }
    );
    
    // Sort by timestamp (newest first) and get the first one
    const sorted = items.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    
    return sorted.length > 0 ? sorted[0].state : null;
  }
}

// Create singleton instance
export const animaMemory = new AnimaMemory();
