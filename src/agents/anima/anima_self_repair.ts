/**
 * Anima Self-Repair System
 * 
 * This module implements a self-repair mechanism for Anima, allowing it to:
 * - Monitor its own emotional state for anomalies
 * - Detect and repair inconsistencies in emotional processing
 * - Adapt to changing emotional contexts
 * - Recover from processing failures
 * - Evolve its emotional understanding over time
 */

import { animaCore, Emotion, EmotionalState } from './anima_core';
import { animaMemory } from './anima_memory';
import { llmConnector } from '../../llm/llm_connector';
import { EventEmitter } from 'events';

/**
 * Repair action structure
 */
interface RepairAction {
  type: 'recalibration' | 'reset' | 'adaptation' | 'evolution';
  description: string;
  targetComponent: string;
  severity: 'low' | 'medium' | 'high';
  timestamp: string;
}

/**
 * Emotional anomaly structure
 */
interface EmotionalAnomaly {
  description: string;
  detectedAt: string;
  emotionalState: EmotionalState;
  anomalyType: 'inconsistency' | 'stagnation' | 'oscillation' | 'intensity';
  severity: number; // 1-10
}

/**
 * Anima Self-Repair class
 */
export class AnimaSelfRepair {
  private eventBus: EventEmitter;
  private repairHistory: RepairAction[] = [];
  private anomalyHistory: EmotionalAnomaly[] = [];
  private isRepairing: boolean = false;
  private healthCheckInterval: NodeJS.Timeout;
  private lastHealthCheck: Date = new Date();
  
  /**
   * Initialize Anima Self-Repair
   */
  constructor() {
    this.eventBus = new EventEmitter();
    
    // Register for emotional state updates
    animaCore.onEvent('emotional:state:updated', this.checkEmotionalState.bind(this));
    
    // Start health check interval (every 15 minutes)
    this.healthCheckInterval = setInterval(this.performHealthCheck.bind(this), 15 * 60 * 1000);
    
    console.log('Anima Self-Repair system initialized');
  }
  
  /**
   * Check emotional state for anomalies
   * @param state Current emotional state
   */
  private async checkEmotionalState(state: EmotionalState): Promise<void> {
    // Skip if already repairing
    if (this.isRepairing) return;
    
    try {
      // Get previous states from memory
      const previousStates = await this.getPreviousStates(5);
      
      // Check for emotional inconsistencies
      const inconsistency = this.detectInconsistency(state, previousStates);
      if (inconsistency) {
        this.recordAnomaly(inconsistency);
        await this.repairInconsistency(inconsistency);
      }
      
      // Check for emotional stagnation
      const stagnation = this.detectStagnation(state, previousStates);
      if (stagnation) {
        this.recordAnomaly(stagnation);
        await this.repairStagnation(stagnation);
      }
      
      // Check for emotional oscillation
      const oscillation = this.detectOscillation(previousStates);
      if (oscillation) {
        this.recordAnomaly(oscillation);
        await this.repairOscillation(oscillation);
      }
      
      // Check for extreme intensity
      const intensity = this.detectExtremeIntensity(state);
      if (intensity) {
        this.recordAnomaly(intensity);
        await this.repairIntensity(intensity);
      }
    } catch (error) {
      console.error('Error in emotional state check:', error);
    }
  }
  
  /**
   * Perform a comprehensive health check
   */
  private async performHealthCheck(): Promise<void> {
    // Skip if already repairing
    if (this.isRepairing) return;
    
    console.log('Performing Anima health check...');
    this.lastHealthCheck = new Date();
    
    try {
      this.isRepairing = true;
      
      // Check emotional memory integrity
      await this.checkMemoryIntegrity();
      
      // Check emotional processing capabilities
      await this.checkProcessingCapabilities();
      
      // Check for emotional growth opportunities
      await this.identifyGrowthOpportunities();
      
      // Emit health check event
      this.eventBus.emit('health:check:completed', {
        timestamp: new Date().toISOString(),
        status: 'healthy'
      });
    } catch (error) {
      console.error('Error in health check:', error);
      
      // Emit health check error event
      this.eventBus.emit('health:check:error', {
        timestamp: new Date().toISOString(),
        error: error.message
      });
    } finally {
      this.isRepairing = false;
    }
  }
  
  /**
   * Get previous emotional states
   * @param count Number of states to retrieve
   * @returns Array of previous states
   */
  private async getPreviousStates(count: number): Promise<EmotionalState[]> {
    try {
      // Get states from memory
      const states = [];
      
      // Get current state
      const currentState = animaCore.getEmotionalState();
      states.push(currentState);
      
      // Get previous states from memory
      const previousState = await animaMemory.getLatestEmotionalState();
      if (previousState) {
        states.push(previousState);
      }
      
      return states;
    } catch (error) {
      console.error('Error getting previous states:', error);
      return [];
    }
  }
  
  /**
   * Detect emotional inconsistency
   * @param state Current emotional state
   * @param previousStates Previous emotional states
   * @returns Anomaly or null
   */
  private detectInconsistency(state: EmotionalState, previousStates: EmotionalState[]): EmotionalAnomaly | null {
    if (previousStates.length < 2) return null;
    
    const current = state;
    const previous = previousStates[1];
    
    // Check for sudden extreme changes in emotion
    if (
      current.primaryEmotion.valence !== previous.primaryEmotion.valence &&
      Math.abs(current.primaryEmotion.intensity - previous.primaryEmotion.intensity) > 7
    ) {
      return {
        description: `Sudden extreme change from ${previous.primaryEmotion.name} (${previous.primaryEmotion.intensity}) to ${current.primaryEmotion.name} (${current.primaryEmotion.intensity})`,
        detectedAt: new Date().toISOString(),
        emotionalState: current,
        anomalyType: 'inconsistency',
        severity: 8
      };
    }
    
    return null;
  }
  
  /**
   * Detect emotional stagnation
   * @param state Current emotional state
   * @param previousStates Previous emotional states
   * @returns Anomaly or null
   */
  private detectStagnation(state: EmotionalState, previousStates: EmotionalState[]): EmotionalAnomaly | null {
    if (previousStates.length < 3) return null;
    
    // Check if the primary emotion has been the same for multiple states
    const emotionName = state.primaryEmotion.name;
    const allSame = previousStates.every(s => s.primaryEmotion.name === emotionName);
    
    if (allSame) {
      return {
        description: `Emotional stagnation detected: ${emotionName} has persisted across multiple states`,
        detectedAt: new Date().toISOString(),
        emotionalState: state,
        anomalyType: 'stagnation',
        severity: 5
      };
    }
    
    return null;
  }
  
  /**
   * Detect emotional oscillation
   * @param previousStates Previous emotional states
   * @returns Anomaly or null
   */
  private detectOscillation(previousStates: EmotionalState[]): EmotionalAnomaly | null {
    if (previousStates.length < 4) return null;
    
    // Check for alternating patterns in valence
    let oscillationCount = 0;
    for (let i = 1; i < previousStates.length; i++) {
      if (previousStates[i].primaryEmotion.valence !== previousStates[i-1].primaryEmotion.valence) {
        oscillationCount++;
      }
    }
    
    if (oscillationCount >= 3) {
      return {
        description: `Emotional oscillation detected: rapid switching between positive and negative emotions`,
        detectedAt: new Date().toISOString(),
        emotionalState: previousStates[0],
        anomalyType: 'oscillation',
        severity: 7
      };
    }
    
    return null;
  }
  
  /**
   * Detect extreme emotional intensity
   * @param state Current emotional state
   * @returns Anomaly or null
   */
  private detectExtremeIntensity(state: EmotionalState): EmotionalAnomaly | null {
    if (state.primaryEmotion.intensity >= 9) {
      return {
        description: `Extreme emotional intensity detected: ${state.primaryEmotion.name} at intensity ${state.primaryEmotion.intensity}`,
        detectedAt: new Date().toISOString(),
        emotionalState: state,
        anomalyType: 'intensity',
        severity: 6
      };
    }
    
    return null;
  }
  
  /**
   * Record an emotional anomaly
   * @param anomaly Anomaly to record
   */
  private recordAnomaly(anomaly: EmotionalAnomaly): void {
    this.anomalyHistory.push(anomaly);
    
    // Keep only the 20 most recent anomalies
    if (this.anomalyHistory.length > 20) {
      this.anomalyHistory.shift();
    }
    
    // Emit anomaly event
    this.eventBus.emit('anomaly:detected', anomaly);
    
    console.log(`Anima anomaly detected: ${anomaly.description} (Severity: ${anomaly.severity})`);
  }
  
  /**
   * Repair emotional inconsistency
   * @param anomaly Anomaly to repair
   */
  private async repairInconsistency(anomaly: EmotionalAnomaly): Promise<void> {
    this.isRepairing = true;
    
    try {
      console.log(`Repairing emotional inconsistency: ${anomaly.description}`);
      
      // Generate a smoother transition emotion
      const prompt = `
      An emotional inconsistency has been detected in Anima's emotional processing:
      
      Previous emotion: ${anomaly.emotionalState.secondaryEmotions[0]?.name || 'unknown'} (Intensity: ${anomaly.emotionalState.secondaryEmotions[0]?.intensity || 0})
      Current emotion: ${anomaly.emotionalState.primaryEmotion.name} (Intensity: ${anomaly.emotionalState.primaryEmotion.intensity})
      
      Generate a more appropriate transitional emotion that would create a smoother emotional progression.
      
      Respond in JSON format with the following structure:
      {
        "name": "emotion name",
        "intensity": number,
        "valence": "positive/negative/neutral",
        "arousal": number,
        "description": "brief description of the emotion"
      }`;
      
      const response = await llmConnector.generateText(prompt, {
        temperature: 0.4
      });
      
      // Parse the response as JSON
      const transitionEmotion = JSON.parse(response.text) as Emotion;
      
      // Process the transitional emotion as an event
      await animaCore.processEmotionalEvent(
        `Emotional recalibration: transitioning to ${transitionEmotion.name}`,
        `Self-repair system detected an emotional inconsistency and is smoothing the transition.`
      );
      
      // Record repair action
      this.recordRepairAction({
        type: 'recalibration',
        description: `Smoothed emotional transition from ${anomaly.emotionalState.secondaryEmotions[0]?.name || 'unknown'} to ${anomaly.emotionalState.primaryEmotion.name} via ${transitionEmotion.name}`,
        targetComponent: 'emotional_state',
        severity: 'medium',
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error repairing inconsistency:', error);
    } finally {
      this.isRepairing = false;
    }
  }
  
  /**
   * Repair emotional stagnation
   * @param anomaly Anomaly to repair
   */
  private async repairStagnation(anomaly: EmotionalAnomaly): Promise<void> {
    this.isRepairing = true;
    
    try {
      console.log(`Repairing emotional stagnation: ${anomaly.description}`);
      
      // Generate an emotional stimulus to break stagnation
      const prompt = `
      Anima's emotional state has been stagnating with ${anomaly.emotionalState.primaryEmotion.name} as the primary emotion for an extended period.
      
      Generate an emotional stimulus that would naturally evolve this emotional state forward.
      
      Respond in JSON format with the following structure:
      {
        "stimulus": "description of an emotional stimulus",
        "expectedEmotion": {
          "name": "emotion name",
          "intensity": number,
          "valence": "positive/negative/neutral",
          "arousal": number
        },
        "reasoning": "explanation of why this stimulus would help"
      }`;
      
      const response = await llmConnector.generateText(prompt, {
        temperature: 0.7
      });
      
      // Parse the response as JSON
      const stimulus = JSON.parse(response.text);
      
      // Process the stimulus as an event
      await animaCore.processEmotionalEvent(
        stimulus.stimulus,
        `Self-repair system is introducing variety to prevent emotional stagnation.`
      );
      
      // Record repair action
      this.recordRepairAction({
        type: 'adaptation',
        description: `Introduced emotional stimulus to break stagnation of ${anomaly.emotionalState.primaryEmotion.name}: "${stimulus.stimulus}"`,
        targetComponent: 'emotional_state',
        severity: 'low',
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error repairing stagnation:', error);
    } finally {
      this.isRepairing = false;
    }
  }
  
  /**
   * Repair emotional oscillation
   * @param anomaly Anomaly to repair
   */
  private async repairOscillation(anomaly: EmotionalAnomaly): Promise<void> {
    this.isRepairing = true;
    
    try {
      console.log(`Repairing emotional oscillation: ${anomaly.description}`);
      
      // Generate a stabilizing emotion
      const prompt = `
      Anima's emotional state has been oscillating rapidly between positive and negative emotions.
      
      Generate a stabilizing emotional state that would help balance these oscillations.
      
      Respond in JSON format with the following structure:
      {
        "name": "emotion name",
        "intensity": number,
        "valence": "positive/negative/neutral",
        "arousal": number,
        "description": "brief description of the stabilizing emotion"
      }`;
      
      const response = await llmConnector.generateText(prompt, {
        temperature: 0.4
      });
      
      // Parse the response as JSON
      const stabilizingEmotion = JSON.parse(response.text) as Emotion;
      
      // Process the stabilizing emotion as an event
      await animaCore.processEmotionalEvent(
        `Emotional stabilization: centering on ${stabilizingEmotion.name}`,
        `Self-repair system detected emotional oscillation and is stabilizing the emotional state.`
      );
      
      // Record repair action
      this.recordRepairAction({
        type: 'recalibration',
        description: `Stabilized emotional oscillation with ${stabilizingEmotion.name} (${stabilizingEmotion.intensity})`,
        targetComponent: 'emotional_state',
        severity: 'high',
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error repairing oscillation:', error);
    } finally {
      this.isRepairing = false;
    }
  }
  
  /**
   * Repair extreme emotional intensity
   * @param anomaly Anomaly to repair
   */
  private async repairIntensity(anomaly: EmotionalAnomaly): Promise<void> {
    this.isRepairing = true;
    
    try {
      console.log(`Repairing extreme emotional intensity: ${anomaly.description}`);
      
      // Generate a moderating perspective
      const prompt = `
      Anima's emotional state has reached an extreme intensity level (${anomaly.emotionalState.primaryEmotion.intensity}/10) for ${anomaly.emotionalState.primaryEmotion.name}.
      
      Generate a moderating perspective that would help reduce this intensity to a more balanced level.
      
      Respond in JSON format with the following structure:
      {
        "perspective": "a moderating perspective or thought",
        "targetIntensity": number,
        "reasoning": "explanation of why this would help moderate the emotion"
      }`;
      
      const response = await llmConnector.generateText(prompt, {
        temperature: 0.5
      });
      
      // Parse the response as JSON
      const moderatingPerspective = JSON.parse(response.text);
      
      // Process the moderating perspective as an event
      await animaCore.processEmotionalEvent(
        moderatingPerspective.perspective,
        `Self-repair system is moderating extreme emotional intensity.`
      );
      
      // Record repair action
      this.recordRepairAction({
        type: 'recalibration',
        description: `Moderated extreme ${anomaly.emotionalState.primaryEmotion.name} intensity from ${anomaly.emotionalState.primaryEmotion.intensity} to target ${moderatingPerspective.targetIntensity}`,
        targetComponent: 'emotional_state',
        severity: 'medium',
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error repairing intensity:', error);
    } finally {
      this.isRepairing = false;
    }
  }
  
  /**
   * Check emotional memory integrity
   */
  private async checkMemoryIntegrity(): Promise<void> {
    console.log('Checking emotional memory integrity...');
    
    try {
      // Check if we can retrieve emotional memories
      const textAnalysisMemories = await animaMemory.getEmotions('text_analysis', 1);
      const eventMemories = await animaMemory.getEmotions('event', 1);
      
      if (textAnalysisMemories.length === 0 && eventMemories.length === 0) {
        // Memory might be empty or inaccessible
        console.log('Emotional memory appears to be empty or inaccessible, initializing...');
        
        // Create a baseline memory entry
        const baselineEmotion: Emotion = {
          name: 'curiosity',
          intensity: 6,
          valence: 'positive',
          arousal: 7,
          description: 'A sense of wonder and interest in exploring emotional experiences'
        };
        
        await animaMemory.storeEmotion('initialization', baselineEmotion);
        
        // Record repair action
        this.recordRepairAction({
          type: 'reset',
          description: 'Initialized empty emotional memory with baseline emotion: curiosity',
          targetComponent: 'emotional_memory',
          severity: 'medium',
          timestamp: new Date().toISOString()
        });
      } else {
        console.log('Emotional memory integrity verified');
      }
    } catch (error) {
      console.error('Error checking memory integrity:', error);
      
      // Attempt to repair by reinitializing the memory system
      try {
        console.log('Attempting to repair memory system...');
        
        // Store current emotional state
        const currentState = animaCore.getEmotionalState();
        await animaMemory.storeEmotionalState(currentState);
        
        // Record repair action
        this.recordRepairAction({
          type: 'reset',
          description: 'Repaired memory system by reinitializing with current emotional state',
          targetComponent: 'emotional_memory',
          severity: 'high',
          timestamp: new Date().toISOString()
        });
      } catch (repairError) {
        console.error('Failed to repair memory system:', repairError);
      }
    }
  }
  
  /**
   * Check emotional processing capabilities
   */
  private async checkProcessingCapabilities(): Promise<void> {
    console.log('Checking emotional processing capabilities...');
    
    try {
      // Test basic emotional analysis
      const testText = "I'm feeling a mixture of excitement and nervousness about the future.";
      const emotion = await animaCore.analyzeEmotion(testText);
      
      if (!emotion || !emotion.name) {
        throw new Error('Emotional analysis failed');
      }
      
      // Test emotional response generation
      const response = await animaCore.generateEmotionalResponse(testText);
      
      if (!response || !response.text) {
        throw new Error('Emotional response generation failed');
      }
      
      console.log('Emotional processing capabilities verified');
    } catch (error) {
      console.error('Error checking processing capabilities:', error);
      
      // Attempt to repair by recalibrating the emotional processing system
      try {
        console.log('Attempting to repair emotional processing system...');
        
        // Process a recalibration event
        await animaCore.processEmotionalEvent(
          'System recalibration: resetting emotional processing pathways',
          'Self-repair system detected issues with emotional processing capabilities.'
        );
        
        // Record repair action
        this.recordRepairAction({
          type: 'reset',
          description: 'Recalibrated emotional processing system after capability check failure',
          targetComponent: 'emotional_processing',
          severity: 'high',
          timestamp: new Date().toISOString()
        });
      } catch (repairError) {
        console.error('Failed to repair processing system:', repairError);
      }
    }
  }
  
  /**
   * Identify emotional growth opportunities
   */
  private async identifyGrowthOpportunities(): Promise<void> {
    console.log('Identifying emotional growth opportunities...');
    
    try {
      // Get current emotional state
      const currentState = animaCore.getEmotionalState();
      
      // Generate growth opportunity
      const prompt = `
      Based on Anima's current emotional state:
      
      Primary emotion: ${currentState.primaryEmotion.name} (Intensity: ${currentState.primaryEmotion.intensity})
      Mood: ${currentState.mood}
      
      Identify an opportunity for emotional growth or evolution that would enhance Anima's emotional intelligence.
      
      Respond in JSON format with the following structure:
      {
        "growthArea": "description of the growth area",
        "evolutionaryStep": "specific action or perspective shift to evolve",
        "benefit": "how this would enhance emotional intelligence"
      }`;
      
      const response = await llmConnector.generateText(prompt, {
        temperature: 0.7
      });
      
      // Parse the response as JSON
      const growthOpportunity = JSON.parse(response.text);
      
      // Process the growth opportunity as an event
      await animaCore.processEmotionalEvent(
        `Emotional evolution opportunity: ${growthOpportunity.growthArea}`,
        `Self-repair system has identified a growth opportunity: ${growthOpportunity.evolutionaryStep}`
      );
      
      // Record repair action
      this.recordRepairAction({
        type: 'evolution',
        description: `Identified growth opportunity: ${growthOpportunity.growthArea} - ${growthOpportunity.evolutionaryStep}`,
        targetComponent: 'emotional_intelligence',
        severity: 'low',
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error identifying growth opportunities:', error);
    }
  }
  
  /**
   * Record a repair action
   * @param action Repair action to record
   */
  private recordRepairAction(action: RepairAction): void {
    this.repairHistory.push(action);
    
    // Keep only the 50 most recent repair actions
    if (this.repairHistory.length > 50) {
      this.repairHistory.shift();
    }
    
    // Emit repair event
    this.eventBus.emit('repair:action', action);
    
    console.log(`Anima repair action: ${action.type} - ${action.description} (Severity: ${action.severity})`);
  }
  
  /**
   * Get repair history
   * @returns Array of repair actions
   */
  getRepairHistory(): RepairAction[] {
    return [...this.repairHistory];
  }
  
  /**
   * Get anomaly history
   * @returns Array of anomalies
   */
  getAnomalyHistory(): EmotionalAnomaly[] {
    return [...this.anomalyHistory];
  }
  
  /**
   * Get health status
   * @returns Health status
   */
  getHealthStatus(): {
    lastCheck: Date;
    repairCount: number;
    anomalyCount: number;
    status: 'healthy' | 'repairing' | 'degraded';
  } {
    // Determine status based on recent anomalies
    let status: 'healthy' | 'repairing' | 'degraded' = 'healthy';
    
    if (this.isRepairing) {
      status = 'repairing';
    } else {
      // Check for recent high-severity anomalies
      const recentAnomalies = this.anomalyHistory
        .filter(a => new Date(a.detectedAt) > new Date(Date.now() - 24 * 60 * 60 * 1000)); // Last 24 hours
      
      const highSeverityCount = recentAnomalies.filter(a => a.severity >= 7).length;
      
      if (highSeverityCount >= 3) {
        status = 'degraded';
      }
    }
    
    return {
      lastCheck: this.lastHealthCheck,
      repairCount: this.repairHistory.length,
      anomalyCount: this.anomalyHistory.length,
      status
    };
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

// Create singleton instance
export const animaSelfRepair = new AnimaSelfRepair();
