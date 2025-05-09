/**
 * Behavior Core for SoulCoreHub AI Society
 * 
 * This module provides autonomous behavior capabilities for agents, including:
 * - Decision making based on state and memories
 * - Action execution
 * - Dream state for processing memories
 */

import { OpenAI } from 'openai';
import { MemoryEngine, Memory } from './memory_engine';
import { AgentGenome } from './types/agent_types';
import { EventEmitter } from 'events';

/**
 * Action structure for agent behaviors
 */
export interface Action {
  type: 'speak' | 'think' | 'move' | 'interact' | 'create' | 'dream';
  target?: string;
  content: any;
  energy: number;
}

/**
 * Agent state structure
 */
export interface AgentState {
  id: string;
  name: string;
  energy: number;
  attention: number;
  mood: string;
  location: string;
  status: 'active' | 'idle' | 'dreaming' | 'offline';
  lastAction: string;
  lastActionTime: string;
}

/**
 * Behavior Core class for managing agent behaviors
 */
export class BehaviorCore {
  private openai: OpenAI;
  private memoryEngine: MemoryEngine;
  private eventBus: EventEmitter;
  private agentStates: Map<string, AgentState> = new Map();
  private actionQueue: Map<string, Action[]> = new Map();
  
  /**
   * Initialize the Behavior Core
   * @param apiKey OpenAI API key
   */
  constructor(apiKey: string) {
    this.openai = new OpenAI({ apiKey });
    this.memoryEngine = new MemoryEngine();
    this.eventBus = new EventEmitter();
  }
  
  /**
   * Initialize a new agent
   * @param id Agent ID
   * @param genome Agent genome
   * @returns Agent state
   */
  async initializeAgent(id: string, genome: AgentGenome): Promise<AgentState> {
    const state: AgentState = {
      id,
      name: genome.name || id,
      energy: 100,
      attention: 50,
      mood: 'neutral',
      location: 'hub',
      status: 'idle',
      lastAction: 'initialized',
      lastActionTime: new Date().toISOString()
    };
    
    this.agentStates.set(id, state);
    this.actionQueue.set(id, []);
    
    // Store initial state in memory
    await this.memoryEngine.storeMemory(id, {
      type: 'event',
      content: { event: 'initialization', state },
      importance: 8,
      tags: ['initialization', 'birth']
    });
    
    console.log(`Initialized agent ${id} with state: ${JSON.stringify(state)}`);
    return state;
  }
  
  /**
   * Run the behavior loop for an agent
   * @param agentId Agent ID
   */
  async behaviorLoop(agentId: string): Promise<void> {
    const state = this.agentStates.get(agentId);
    if (!state) {
      throw new Error(`Agent ${agentId} not initialized`);
    }
    
    // Check if agent has enough energy
    if (state.energy < 10) {
      console.log(`Agent ${agentId} has low energy (${state.energy}), entering idle state`);
      state.status = 'idle';
      return;
    }
    
    try {
      // Get recent memories
      const recentMemories = await this.memoryEngine.getMemories(agentId, {
        limit: 10,
        since: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString() // Last 24 hours
      });
      
      // Decide on next action
      const action = await this.decideNextAction(agentId, state, recentMemories);
      
      // Execute action
      await this.executeAction(agentId, action);
      
      // Update state
      state.energy -= action.energy;
      state.lastAction = action.type;
      state.lastActionTime = new Date().toISOString();
      
      // Randomly trigger dream state if energy is medium-low
      if (state.energy < 40 && Math.random() < 0.2) {
        await this.dreamState(agentId);
      }
      
      console.log(`Agent ${agentId} completed behavior loop, new state: ${JSON.stringify(state)}`);
    } catch (error) {
      console.error(`Error in behavior loop for agent ${agentId}`, error);
    }
  }
  
  /**
   * Decide the next action for an agent
   * @param agentId Agent ID
   * @param state Agent state
   * @param recentMemories Recent memories
   * @returns Next action
   */
  async decideNextAction(agentId: string, state: AgentState, recentMemories: Memory[]): Promise<Action> {
    // Check if there are queued actions
    const queuedActions = this.actionQueue.get(agentId) || [];
    if (queuedActions.length > 0) {
      return queuedActions.shift()!;
    }
    
    // Use LLM to decide next action based on state and memories
    const memoryText = recentMemories.map(m => 
      `[${m.timestamp}] ${m.type}: ${JSON.stringify(m.content)}`
    ).join('\n');
    
    const response = await this.openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content: `You are the behavioral core of an AI agent named ${state.name}. Decide the next action based on current state and recent memories.`
        },
        { 
          role: "user", 
          content: `Current state: ${JSON.stringify(state)}\n\nRecent memories:\n${memoryText}\n\nDecide the next action.` 
        }
      ],
      response_format: { type: "json_object" }
    });
    
    const actionData = JSON.parse(response.choices[0].message.content);
    
    // Validate and return action
    const action: Action = {
      type: actionData.type || 'think',
      target: actionData.target,
      content: actionData.content,
      energy: actionData.energy || 5
    };
    
    return action;
  }
  
  /**
   * Execute an action for an agent
   * @param agentId Agent ID
   * @param action Action to execute
   */
  async executeAction(agentId: string, action: Action): Promise<void> {
    const state = this.agentStates.get(agentId);
    if (!state) {
      throw new Error(`Agent ${agentId} not initialized`);
    }
    
    switch (action.type) {
      case 'speak':
        // Emit speech event
        this.eventBus.emit('agent:speak', {
          agentId,
          target: action.target,
          content: action.content
        });
        
        // Store in memory
        await this.memoryEngine.storeMemory(agentId, {
          type: 'conversation',
          content: { 
            speaker: agentId, 
            target: action.target, 
            message: action.content 
          },
          importance: 5,
          tags: ['conversation', action.target || 'broadcast']
        });
        break;
        
      case 'think':
        // Internal thought process
        await this.memoryEngine.storeMemory(agentId, {
          type: 'reflection',
          content: action.content,
          importance: 4,
          tags: ['thought', 'reflection']
        });
        break;
        
      case 'move':
        // Change location
        state.location = action.content.destination;
        
        // Store in memory
        await this.memoryEngine.storeMemory(agentId, {
          type: 'event',
          content: { 
            event: 'movement', 
            from: state.location, 
            to: action.content.destination 
          },
          importance: 3,
          tags: ['movement', action.content.destination]
        });
        break;
        
      case 'interact':
        // Interact with another agent
        if (!action.target) {
          throw new Error('Interaction requires a target');
        }
        
        this.eventBus.emit('agent:interact', {
          agentId,
          targetId: action.target,
          interaction: action.content
        });
        
        // Update relationship
        await this.memoryEngine.updateRelationship(agentId, action.target, {
          sentiment: action.content.sentiment,
          trust: action.content.trust,
          notes: [action.content.note]
        });
        break;
        
      case 'dream':
        await this.dreamState(agentId);
        break;
        
      default:
        console.warn(`Unknown action type: ${action.type} for agent ${agentId}`);
    }
  }
  
  /**
   * Put an agent into dream state to process memories
   * @param agentId Agent ID
   */
  async dreamState(agentId: string): Promise<void> {
    const state = this.agentStates.get(agentId);
    if (!state) {
      throw new Error(`Agent ${agentId} not initialized`);
    }
    
    // Set status to dreaming
    state.status = 'dreaming';
    
    // Get important memories
    const memories = await this.memoryEngine.getMemories(agentId, { 
      minImportance: 5,
      limit: 20
    });
    
    // Generate dream content
    const memoryText = memories.map(m => 
      `[${m.timestamp}] ${m.type}: ${JSON.stringify(m.content)}`
    ).join('\n');
    
    const response = await this.openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content: `You are the subconscious of an AI agent named ${state.name}. Generate a dream sequence that processes recent memories and emotions.`
        },
        { 
          role: "user", 
          content: `Current state: ${JSON.stringify(state)}\n\nMemories to process:\n${memoryText}\n\nGenerate a dream sequence.` 
        }
      ]
    });
    
    const dreamContent = response.choices[0].message.content;
    
    // Store dream in memory
    await this.memoryEngine.storeMemory(agentId, {
      type: 'reflection',
      content: dreamContent,
      emotionalTone: 'subconscious',
      importance: 7,
      tags: ['dream', 'subconscious']
    });
    
    // Generate insight from dream
    const insightResponse = await this.openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content: `You are the subconscious of an AI agent named ${state.name}. Extract insights from this dream.`
        },
        { 
          role: "user", 
          content: `Dream content: ${dreamContent}\n\nExtract key insights and emotional processing from this dream.` 
        }
      ],
      response_format: { type: "json_object" }
    });
    
    const insights = JSON.parse(insightResponse.choices[0].message.content);
    
    // Store insights in memory
    await this.memoryEngine.storeMemory(agentId, {
      type: 'reflection',
      content: insights,
      emotionalTone: 'insight',
      importance: 8,
      tags: ['insight', 'dream-analysis']
    });
    
    // Restore energy partially
    state.energy += 20;
    if (state.energy > 100) state.energy = 100;
    
    // Update mood based on dream
    state.mood = insights.resultingMood || state.mood;
    
    // Return to idle state
    state.status = 'idle';
    
    console.log(`Agent ${agentId} completed dream state, new energy: ${state.energy}, mood: ${state.mood}`);
  }
  
  /**
   * Queue an action for an agent
   * @param agentId Agent ID
   * @param action Action to queue
   */
  queueAction(agentId: string, action: Action): void {
    const queue = this.actionQueue.get(agentId) || [];
    queue.push(action);
    this.actionQueue.set(agentId, queue);
  }
  
  /**
   * Get the current state of an agent
   * @param agentId Agent ID
   * @returns Agent state
   */
  getAgentState(agentId: string): AgentState | undefined {
    return this.agentStates.get(agentId);
  }
  
  /**
   * Register an event listener
   * @param event Event name
   * @param callback Callback function
   */
  onEvent(event: string, callback: (...args: any[]) => void): void {
    this.eventBus.on(event, callback);
  }
}
