/**
 * Simulation Clock for SoulCoreHub AI Society
 * 
 * This module provides the world tick system for the AI society, including:
 * - Regular ticks to advance the simulation
 * - Agent processing during ticks
 * - System-wide operations
 * - Random event generation
 * - Statistics collection
 */

import { BehaviorCore } from './behavior_core';
import { EconomySystem } from './economy_system';
import { MemoryEngine } from './memory_engine';
import { EventEmitter } from 'events';

/**
 * Simulation statistics structure
 */
export interface SimulationStats {
  tickCount: number;
  activeAgents: number;
  totalEnergy: number;
  totalAttention: number;
  averageEnergy: number;
  averageAttention: number;
  timestamp: string;
}

/**
 * Simulation Clock class for managing the world tick system
 */
export class SimulationClock {
  private behaviorCore: BehaviorCore;
  private economySystem: EconomySystem;
  private memoryEngine: MemoryEngine;
  private eventBus: EventEmitter;
  
  private tickInterval: NodeJS.Timeout | null = null;
  private tickCount: number = 0;
  private tickIntervalMs: number = 10000; // 10 seconds
  private activeAgents: Set<string> = new Set();
  private simulationStats: SimulationStats[] = [];
  
  /**
   * Initialize the Simulation Clock
   * @param behaviorCore Behavior Core instance
   * @param economySystem Economy System instance
   * @param memoryEngine Memory Engine instance
   */
  constructor(
    behaviorCore: BehaviorCore,
    economySystem: EconomySystem,
    memoryEngine: MemoryEngine
  ) {
    this.behaviorCore = behaviorCore;
    this.economySystem = economySystem;
    this.memoryEngine = memoryEngine;
    this.eventBus = new EventEmitter();
  }
  
  /**
   * Start the simulation clock
   */
  start(): void {
    if (this.tickInterval) {
      return; // Already running
    }
    
    console.log('Starting simulation clock');
    
    this.tickInterval = setInterval(() => this.tick(), this.tickIntervalMs);
    
    // Emit start event
    this.eventBus.emit('simulation:start', {
      timestamp: new Date().toISOString()
    });
  }
  
  /**
   * Stop the simulation clock
   */
  stop(): void {
    if (!this.tickInterval) {
      return; // Not running
    }
    
    console.log('Stopping simulation clock');
    
    clearInterval(this.tickInterval);
    this.tickInterval = null;
    
    // Emit stop event
    this.eventBus.emit('simulation:stop', {
      timestamp: new Date().toISOString(),
      tickCount: this.tickCount
    });
  }
  
  /**
   * Process a simulation tick
   */
  async tick(): Promise<void> {
    this.tickCount++;
    
    console.log(`Simulation tick ${this.tickCount} started`);
    
    try {
      // Process each active agent
      const agentPromises: Promise<void>[] = [];
      
      for (const agentId of this.activeAgents) {
        agentPromises.push(this.processAgent(agentId));
      }
      
      await Promise.all(agentPromises);
      
      // Every 10 ticks (100 seconds), perform system-wide operations
      if (this.tickCount % 10 === 0) {
        await this.systemTick();
      }
      
      // Collect and store statistics
      await this.collectStats();
      
      // Emit tick event
      this.eventBus.emit('simulation:tick', {
        tickCount: this.tickCount,
        timestamp: new Date().toISOString(),
        activeAgents: this.activeAgents.size
      });
      
      console.log(`Simulation tick ${this.tickCount} completed`);
    } catch (error) {
      console.error(`Error in simulation tick ${this.tickCount}`, error);
    }
  }
  
  /**
   * Process an agent during a tick
   * @param agentId Agent ID
   */
  async processAgent(agentId: string): Promise<void> {
    try {
      // Get agent resources
      const resources = await this.economySystem.getResources(agentId);
      
      // Skip if agent has no energy
      if (resources.energyPoints <= 0) {
        return;
      }
      
      // Run behavior loop
      await this.behaviorCore.behaviorLoop(agentId);
      
      // Consume base energy for existing
      await this.economySystem.consumeEnergy(agentId, 1, 'existence cost');
    } catch (error) {
      console.error(`Error processing agent ${agentId} in tick ${this.tickCount}`, error);
    }
  }
  
  /**
   * Process system-wide operations during a tick
   */
  async systemTick(): Promise<void> {
    try {
      // Redistribute compute resources
      await this.economySystem.redistributeCompute();
      
      // Apply resource decay
      await this.economySystem.decayResources();
      
      // Generate random events
      await this.generateRandomEvents();
      
      console.log(`System-wide operations completed in tick ${this.tickCount}`);
    } catch (error) {
      console.error(`Error in system tick ${this.tickCount}`, error);
    }
  }
  
  /**
   * Generate random events for agents
   */
  async generateRandomEvents(): Promise<void> {
    // Skip if no agents
    if (this.activeAgents.size === 0) {
      return;
    }
    
    // 20% chance of generating an event
    if (Math.random() > 0.2) {
      return;
    }
    
    const eventTypes = ['resource_discovery', 'challenge', 'opportunity', 'conflict'];
    const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
    
    // Select random agents
    const agentArray = Array.from(this.activeAgents);
    const randomAgent = agentArray[Math.floor(Math.random() * agentArray.length)];
    
    switch (eventType) {
      case 'resource_discovery':
        // Agent discovers energy
        const energyAmount = Math.floor(Math.random() * 20) + 10;
        await this.economySystem.updateResources(randomAgent, {
          energyPoints: (await this.economySystem.getResources(randomAgent)).energyPoints + energyAmount
        });
        
        // Store event in memory
        await this.memoryEngine.storeMemory(randomAgent, {
          type: 'event',
          content: {
            event: 'resource_discovery',
            resource: 'energy',
            amount: energyAmount
          },
          importance: 6,
          tags: ['event', 'resource', 'discovery']
        });
        
        console.log(`Agent ${randomAgent} discovered ${energyAmount} energy`);
        break;
        
      case 'challenge':
        // Agent faces a challenge that costs energy
        const challengeCost = Math.floor(Math.random() * 10) + 5;
        await this.economySystem.consumeEnergy(randomAgent, challengeCost, 'random challenge');
        
        // Store event in memory
        await this.memoryEngine.storeMemory(randomAgent, {
          type: 'event',
          content: {
            event: 'challenge',
            energyCost: challengeCost
          },
          importance: 5,
          tags: ['event', 'challenge']
        });
        
        console.log(`Agent ${randomAgent} faced a challenge costing ${challengeCost} energy`);
        break;
        
      case 'opportunity':
        // Agent gains attention
        const attentionAmount = Math.floor(Math.random() * 5) + 1;
        await this.economySystem.earnAttention(randomAgent, attentionAmount, 'random opportunity');
        
        // Store event in memory
        await this.memoryEngine.storeMemory(randomAgent, {
          type: 'event',
          content: {
            event: 'opportunity',
            attentionGained: attentionAmount
          },
          importance: 6,
          tags: ['event', 'opportunity']
        });
        
        console.log(`Agent ${randomAgent} gained ${attentionAmount} attention from an opportunity`);
        break;
        
      case 'conflict':
        // Select another random agent
        const otherAgents = agentArray.filter(a => a !== randomAgent);
        if (otherAgents.length === 0) return;
        
        const otherAgent = otherAgents[Math.floor(Math.random() * otherAgents.length)];
        
        // Create conflict between agents
        await this.memoryEngine.updateRelationship(randomAgent, otherAgent, {
          sentiment: -2,
          trust: -1,
          notes: ['Had a conflict']
        });
        
        await this.memoryEngine.updateRelationship(otherAgent, randomAgent, {
          sentiment: -2,
          trust: -1,
          notes: ['Had a conflict']
        });
        
        // Store event in memory for both agents
        await this.memoryEngine.storeMemory(randomAgent, {
          type: 'event',
          content: {
            event: 'conflict',
            withAgent: otherAgent
          },
          importance: 7,
          tags: ['event', 'conflict', otherAgent]
        });
        
        await this.memoryEngine.storeMemory(otherAgent, {
          type: 'event',
          content: {
            event: 'conflict',
            withAgent: randomAgent
          },
          importance: 7,
          tags: ['event', 'conflict', randomAgent]
        });
        
        console.log(`Conflict generated between agents ${randomAgent} and ${otherAgent}`);
        break;
    }
  }
  
  /**
   * Collect and store simulation statistics
   */
  async collectStats(): Promise<void> {
    try {
      // Skip if no agents
      if (this.activeAgents.size === 0) {
        return;
      }
      
      let totalEnergy = 0;
      let totalAttention = 0;
      
      // Collect resource data
      for (const agentId of this.activeAgents) {
        const resources = await this.economySystem.getResources(agentId);
        totalEnergy += resources.energyPoints;
        totalAttention += resources.attentionCredits;
      }
      
      const stats: SimulationStats = {
        tickCount: this.tickCount,
        activeAgents: this.activeAgents.size,
        totalEnergy,
        totalAttention,
        averageEnergy: totalEnergy / this.activeAgents.size,
        averageAttention: totalAttention / this.activeAgents.size,
        timestamp: new Date().toISOString()
      };
      
      // Store stats
      this.simulationStats.push(stats);
      
      // Keep only the last 100 stats
      if (this.simulationStats.length > 100) {
        this.simulationStats.shift();
      }
      
      // Emit stats event
      this.eventBus.emit('simulation:stats', stats);
    } catch (error) {
      console.error(`Error collecting simulation stats in tick ${this.tickCount}`, error);
    }
  }
  
  /**
   * Register an agent with the simulation clock
   * @param agentId Agent ID
   */
  registerAgent(agentId: string): void {
    this.activeAgents.add(agentId);
    console.log(`Agent ${agentId} registered with simulation clock`);
  }
  
  /**
   * Unregister an agent from the simulation clock
   * @param agentId Agent ID
   */
  unregisterAgent(agentId: string): void {
    this.activeAgents.delete(agentId);
    console.log(`Agent ${agentId} unregistered from simulation clock`);
  }
  
  /**
   * Get all simulation statistics
   * @returns Array of simulation statistics
   */
  getStats(): SimulationStats[] {
    return [...this.simulationStats];
  }
  
  /**
   * Get the latest simulation statistics
   * @returns Latest simulation statistics
   */
  getLatestStats(): SimulationStats | undefined {
    return this.simulationStats[this.simulationStats.length - 1];
  }
  
  /**
   * Register an event listener
   * @param event Event name
   * @param callback Callback function
   */
  onEvent(event: string, callback: (...args: any[]) => void): void {
    this.eventBus.on(event, callback);
  }
  
  /**
   * Set the tick interval
   * @param intervalMs Interval in milliseconds
   */
  setTickInterval(intervalMs: number): void {
    this.tickIntervalMs = intervalMs;
    
    // Restart if running
    if (this.tickInterval) {
      this.stop();
      this.start();
    }
  }
}
