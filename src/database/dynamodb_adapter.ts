/**
 * DynamoDB Adapter for SoulCoreHub
 * 
 * This module provides a simple interface for interacting with DynamoDB.
 */

import { DynamoDB } from 'aws-sdk';
import { v4 as uuidv4 } from 'uuid';

/**
 * DynamoDB Adapter class
 */
export class DynamoDBAdapter {
  private dynamoDB: DynamoDB.DocumentClient;
  
  /**
   * Initialize the DynamoDB adapter
   */
  constructor() {
    this.dynamoDB = new DynamoDB.DocumentClient({
      region: process.env.AWS_REGION || 'us-east-1'
    });
  }
  
  /**
   * Create a DynamoDB table
   * @param tableName Table name
   * @param keySchema Key schema
   * @returns Success status
   */
  async createTable(tableName: string, keySchema: any): Promise<boolean> {
    try {
      const dynamoDB = new DynamoDB({
        region: process.env.AWS_REGION || 'us-east-1'
      });
      
      await dynamoDB.createTable({
        TableName: tableName,
        KeySchema: keySchema,
        AttributeDefinitions: keySchema.map((key: any) => ({
          AttributeName: key.AttributeName,
          AttributeType: 'S'
        })),
        ProvisionedThroughput: {
          ReadCapacityUnits: 5,
          WriteCapacityUnits: 5
        }
      }).promise();
      
      return true;
    } catch (error) {
      console.error(`Error creating table ${tableName}:`, error);
      return false;
    }
  }
  
  /**
   * Put an item in a DynamoDB table
   * @param tableName Table name
   * @param item Item to put
   * @returns Success status
   */
  async put(tableName: string, item: any): Promise<boolean> {
    try {
      await this.dynamoDB.put({
        TableName: tableName,
        Item: item
      }).promise();
      
      return true;
    } catch (error) {
      console.error(`Error putting item in ${tableName}:`, error);
      return false;
    }
  }
  
  /**
   * Get an item from a DynamoDB table
   * @param tableName Table name
   * @param key Key to get
   * @returns Item or null
   */
  async get(tableName: string, key: any): Promise<any> {
    try {
      const result = await this.dynamoDB.get({
        TableName: tableName,
        Key: key
      }).promise();
      
      return result.Item;
    } catch (error) {
      console.error(`Error getting item from ${tableName}:`, error);
      return null;
    }
  }
  
  /**
   * Query a DynamoDB table
   * @param tableName Table name
   * @param keyConditionExpression Key condition expression
   * @param expressionAttributeValues Expression attribute values
   * @returns Items or empty array
   */
  async query(tableName: string, keyConditionExpression: string, expressionAttributeValues: any): Promise<any[]> {
    try {
      const result = await this.dynamoDB.query({
        TableName: tableName,
        KeyConditionExpression: keyConditionExpression,
        ExpressionAttributeValues: expressionAttributeValues
      }).promise();
      
      return result.Items || [];
    } catch (error) {
      console.error(`Error querying ${tableName}:`, error);
      return [];
    }
  }
  
  /**
   * Update an item in a DynamoDB table
   * @param tableName Table name
   * @param key Key to update
   * @param updateExpression Update expression
   * @param expressionAttributeValues Expression attribute values
   * @returns Success status
   */
  async update(tableName: string, key: any, updateExpression: string, expressionAttributeValues: any): Promise<boolean> {
    try {
      await this.dynamoDB.update({
        TableName: tableName,
        Key: key,
        UpdateExpression: updateExpression,
        ExpressionAttributeValues: expressionAttributeValues
      }).promise();
      
      return true;
    } catch (error) {
      console.error(`Error updating item in ${tableName}:`, error);
      return false;
    }
  }
  
  /**
   * Delete an item from a DynamoDB table
   * @param tableName Table name
   * @param key Key to delete
   * @returns Success status
   */
  async delete(tableName: string, key: any): Promise<boolean> {
    try {
      await this.dynamoDB.delete({
        TableName: tableName,
        Key: key
      }).promise();
      
      return true;
    } catch (error) {
      console.error(`Error deleting item from ${tableName}:`, error);
      return false;
    }
  }
  
  /**
   * Scan a DynamoDB table
   * @param tableName Table name
   * @param filterExpression Filter expression
   * @param expressionAttributeValues Expression attribute values
   * @returns Items or empty array
   */
  async scan(tableName: string, filterExpression?: string, expressionAttributeValues?: any): Promise<any[]> {
    try {
      const params: DynamoDB.DocumentClient.ScanInput = {
        TableName: tableName
      };
      
      if (filterExpression) {
        params.FilterExpression = filterExpression;
        params.ExpressionAttributeValues = expressionAttributeValues;
      }
      
      const result = await this.dynamoDB.scan(params).promise();
      
      return result.Items || [];
    } catch (error) {
      console.error(`Error scanning ${tableName}:`, error);
      return [];
    }
  }
  
  /**
   * Generate a unique ID
   * @returns Unique ID
   */
  generateId(): string {
    return uuidv4();
  }
}

// Create singleton instance
export const db = new DynamoDBAdapter();
