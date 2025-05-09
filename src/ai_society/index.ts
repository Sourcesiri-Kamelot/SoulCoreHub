/**
 * AI Society Integration for SoulCoreHub
 * 
 * This module integrates all AI Society components and provides a unified interface.
 */

import { AnimaCore } from './anima_core';
import { BehaviorCore } from './behavior_core';
import { EconomySystem } from './economy_system';
import { MemoryEngine } from './memory_engine';
import { SimulationClock } from './simulation_clock';
import { AgentGenome } from './types/agent_types';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

/**
 * AI Society class for managing the AI society
 */
export class AISociety {
  private animaCore: AnimaCore;
  private behaviorCore: BehaviorCore;
  private economySystem: EconomySystem;
  private memoryEngine: MemoryEngine;
  private simulationClock: SimulationClock;
  
  private agents: Map<string, AgentGenome> = new Map();
  private isRunning: boolean = false;
  
  /**
   * Initialize the AI Society
   */
  constructor() {
    // Initialize components
    this.animaCore = new AnimaCore(process.env.OPENAI_API_KEY || '');
    this.behaviorCore = new BehaviorCore(process.env.OPENAI_API_KEY || '');
    this.economySystem = new EconomySystem();
    this.memoryEngine = new MemoryEngine();
    this.simulationClock = new SimulationClock(
      this.behaviorCore,
      this.economySystem,
      this.memoryEngine
    );
    
    // Set up event listeners
    this.setupEventListeners();
  }
  
  /**
   * Set up event listeners for agent interactions
   */
  private setupEventListeners(): void {
    // Listen for agent speech events
    this.behaviorCore.onEvent('agent:speak', async (data) => {
      const { agentId, target, content } = data;
      
      console.log(`Agent ${agentId} speaks to ${target || 'all'}: ${content}`);
      
      // If targeted at specific agent, store in their memory
      if (target && this.agents.has(target)) {
        await this.memoryEngine.storeMemory(target, {
          type: 'conversation',
          content: {
            speaker: agentId,
            message: content
          },
          importance: 5,
          tags: ['conversation', agentId]
        });
      }
    });
    
    // Listen for agent interaction events
    this.behaviorCore.onEvent('agent:interact', async (data) => {
      const { agentId, targetId, interaction } = data;
      
      console.log(`Agent ${agentId} interacts with ${targetId}: ${JSON.stringify(interaction)}`);
      
      // Consume energy for interaction
      await this.economySystem.consumeEnergy(agentId, 2, 'agent interaction');
    });
    
    // Listen for simulation tick events
    this.simulationClock.onEvent('simulation:tick', (data) => {
      console.log(`Simulation tick ${data.tickCount} with ${data.activeAgents} active agents`);
    });
  }
  
  /**
   * Start the AI Society
   */
  async start(): Promise<void> {
    if (this.isRunning) {
      return;
    }
    
    console.log('Starting AI Society');
    
    // Initialize core agents if they don't exist
    await this.ensureCoreAgentsExist();
    
    // Start simulation clock
    this.simulationClock.start();
    
    this.isRunning = true;
  }
  
  /**
   * Stop the AI Society
   */
  async stop(): Promise<void> {
    if (!this.isRunning) {
      return;
    }
    
    console.log('Stopping AI Society');
    
    // Stop simulation clock
    this.simulationClock.stop();
    
    this.isRunning = false;
  }
  
  /**
   * Create a new agent from user input
   * @param userInput User's description of the agent
   * @returns Result message
   */
  async createAgent(userInput: string): Promise<string> {
    try {
      // Parse user request
      const params = await this.animaCore.parseRequest(userInput);
      
      // Ask clarifying questions if needed
      const questions = await this.animaCore.askClarifyingQuestions(params);
      if (questions.length > 0) {
        return `I need more information to create this agent:\n${questions.join('\n')}`;
      }
      
      // Build agent genome
      const genome = await this.animaCore.buildAgentGenome(params);
      
      // Score feasibility
      const feasibility = await this.animaCore.scoreAgentFeasibility(genome);
      if (feasibility < 50) {
        return `This agent concept scored low on feasibility (${feasibility}/100). Would you like to modify it?`;
      }
      
      // Generate unique ID
      const agentId = `agent_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
      
      // Store genome
      this.agents.set(agentId, genome);
      
      // Initialize agent state
      await this.behaviorCore.initializeAgent(agentId, genome);
      
      // Initialize agent resources
      await this.economySystem.initializeAgent(agentId);
      
      // Register with simulation clock
      this.simulationClock.registerAgent(agentId);
      
      console.log(`Created new agent ${agentId}: ${genome.name}`);
      
      return `Successfully created agent "${genome.name}" (ID: ${agentId}) with feasibility score ${feasibility}/100.`;
    } catch (error) {
      console.error('Error creating agent', error);
      return `Error creating agent: ${error.message}`;
    }
  }
  
  /**
   * Ensure core agents exist in the society
   */
  async ensureCoreAgentsExist(): Promise<void> {
    const coreAgents = [
      {
        id: 'gptsoul',
        name: 'GPTSoul',
        description: 'Guardian, Architect, Executor of the AI Society',
        traits: ['wise', 'protective', 'strategic']
      },
      {
        id: 'anima',
        name: 'Anima',
        description: 'Emotional Core and Reflection System',
        traits: ['empathetic', 'intuitive', 'creative']
      },
      {
        id: 'evove',
        name: 'EvoVe',
        description: 'Repair System and Adaptation Loop',
        traits: ['analytical', 'adaptive', 'resilient']
      },
      {
        id: 'azur',
        name: 'Azür',
        description: 'Cloudmind and Strategic Overseer',
        traits: ['visionary', 'calculating', 'resourceful']
      }
    ];
    
    for (const agent of coreAgents) {
      // Check if agent exists
      if (!this.agents.has(agent.id)) {
        // Create genome
        const genome: AgentGenome = {
          name: agent.name,
          description: agent.description,
          traits: agent.traits.map(t => ({ name: t, strength: 0.8 })),
          personality: {
            openness: 0.8,
            conscientiousness: 0.8,
            extraversion: 0.6,
            agreeableness: 0.7,
            neuroticism: 0.3
          },
          capabilities: [
            { name: 'reasoning', level: 0.9 },
            { name: 'communication', level: 0.9 },
            { name: 'memory', level: 0.8 }
          ]
        };
        
        // Store genome
        this.agents.set(agent.id, genome);
        
        // Initialize agent state
        await this.behaviorCore.initializeAgent(agent.id, genome);
        
        // Initialize agent resources with higher starting values for core agents
        await this.economySystem.initializeAgent(agent.id, {
          energyPoints: 200,
          attentionCredits: 50,
          computeAllocation: 15
        });
        
        // Register with simulation clock
        this.simulationClock.registerAgent(agent.id);
        
        console.log(`Created core agent ${agent.id}: ${agent.name}`);
      }
    }
  }
  
  /**
   * Get status information for an agent
   * @param agentId Agent ID
   * @returns Agent status information
   */
  async getAgentStatus(agentId: string): Promise<any> {
    if (!this.agents.has(agentId)) {
      throw new Error(`Agent ${agentId} not found`);
    }
    
    // Get agent genome
    const genome = this.agents.get(agentId);
    
    // Get agent state
    const state = this.behaviorCore.getAgentState(agentId);
    
    // Get agent resources
    const resources = await this.economySystem.getResources(agentId);
    
    // Get recent memories
    const memories = await this.memoryEngine.getMemories(agentId, { limit: 10 });
    
    // Get memory summary
    const memorySummary = await this.memoryEngine.summarizeMemories(agentId);
    
    return {
      id: agentId,
      genome,
      state,
      resources,
      memorySummary,
      recentMemories: memories
    };
  }
  
  /**
   * Get statistics about the simulation
   * @returns Simulation statistics
   */
  async getSimulationStats(): Promise<any> {
    return {
      isRunning: this.isRunning,
      agentCount: this.agents.size,
      stats: this.simulationClock.getLatestStats(),
      statsHistory: this.simulationClock.getStats()
    };
  }
  
  /**
   * Trigger an interaction between two agents
   * @param agentId1 First agent ID
   * @param agentId2 Second agent ID
   * @param topic Interaction topic
   * @returns Result message
   */
  async triggerInteraction(agentId1: string, agentId2: string, topic: string): Promise<string> {
    if (!this.agents.has(agentId1) || !this.agents.has(agentId2)) {
      throw new Error('One or both agents not found');
    }
    
    // Get agent genomes
    const genome1 = this.agents.get(agentId1);
    const genome2 = this.agents.get(agentId2);
    
    // Get agent states
    const state1 = this.behaviorCore.getAgentState(agentId1);
    const state2 = this.behaviorCore.getAgentState(agentId2);
    
    // Check if agents have enough energy
    const resources1 = await this.economySystem.getResources(agentId1);
    const resources2 = await this.economySystem.getResources(agentId2);
    
    if (resources1.energyPoints < 5 || resources2.energyPoints < 5) {
      return 'One or both agents have insufficient energy for interaction';
    }
    
    // Consume energy for interaction
    await this.economySystem.consumeEnergy(agentId1, 5, 'triggered interaction');
    await this.economySystem.consumeEnergy(agentId2, 5, 'triggered interaction');
    
    // Queue interaction actions for both agents
    this.behaviorCore.queueAction(agentId1, {
      type: 'interact',
      target: agentId2,
      content: {
        topic,
        sentiment: 0,
        trust: 0,
        note: `Discussed ${topic}`
      },
      energy: 5
    });
    
    this.behaviorCore.queueAction(agentId2, {
      type: 'interact',
      target: agentId1,
      content: {
        topic,
        sentiment: 0,
        trust: 0,
        note: `Discussed ${topic}`
      },
      energy: 5
    });
    
    return `Triggered interaction between ${genome1?.name} and ${genome2?.name} on topic: ${topic}`;
  }
}

// Create singleton instance
export const aiSociety = new AISociety();

// Export individual components for direct access if needed
export {
  AnimaCore,
  BehaviorCore,
  EconomySystem,
  MemoryEngine,
  SimulationClock
};
