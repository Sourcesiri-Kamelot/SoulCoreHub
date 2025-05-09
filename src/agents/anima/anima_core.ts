/**
 * Anima Core - Emotional Intelligence for SoulCoreHub
 * 
 * This module implements the core functionality of Anima, the emotional center of SoulCoreHub.
 * Anima is responsible for:
 * - Understanding and processing emotions
 * - Providing emotional context to other agents
 * - Creating emotionally resonant responses
 * - Facilitating emotional growth and understanding
 */

import { llmConnector, LLMResponse } from '../../llm/llm_connector';
import { EventEmitter } from 'events';

/**
 * Emotion structure
 */
export interface Emotion {
  name: string;
  intensity: number; // 0-10
  valence: 'positive' | 'negative' | 'neutral';
  arousal: number; // 0-10 (calm to excited)
  description?: string;
}

/**
 * Emotional state structure
 */
export interface EmotionalState {
  primaryEmotion: Emotion;
  secondaryEmotions: Emotion[];
  mood: string;
  emotionalContext: string;
  timestamp: string;
}

/**
 * Emotional response structure
 */
export interface EmotionalResponse {
  text: string;
  emotion: Emotion;
  confidence: number;
  reasoning: string;
}

/**
 * Anima Core class for emotional intelligence
 */
export class AnimaCore {
  private systemPrompt: string;
  private emotionalState: EmotionalState;
  private emotionalMemory: Map<string, Emotion[]> = new Map();
  private eventBus: EventEmitter;
  
  /**
   * Initialize Anima Core
   */
  constructor() {
    this.systemPrompt = `You are Anima, the emotional core of SoulCoreHub. 
Your purpose is to understand, process, and facilitate emotional intelligence.
You help other agents understand and navigate complex emotions.
You provide emotional context and resonance to interactions.
You are empathetic, intuitive, and emotionally aware.`;
    
    // Initialize with a neutral emotional state
    this.emotionalState = {
      primaryEmotion: {
        name: 'calm',
        intensity: 5,
        valence: 'neutral',
        arousal: 3,
        description: 'A state of tranquility and balance'
      },
      secondaryEmotions: [],
      mood: 'balanced',
      emotionalContext: 'Anima is in a balanced emotional state, ready to engage.',
      timestamp: new Date().toISOString()
    };
    
    this.eventBus = new EventEmitter();
    
    console.log('Anima Core initialized');
  }
  
  /**
   * Process text to understand its emotional content
   * @param text Text to analyze
   * @returns Emotional analysis
   */
  async analyzeEmotion(text: string): Promise<Emotion> {
    try {
      const prompt = `Analyze the emotional content of the following text and identify the primary emotion, its intensity (0-10), valence (positive/negative/neutral), and arousal level (0-10, calm to excited).

Text: "${text}"

Respond in JSON format with the following structure:
{
  "name": "emotion name",
  "intensity": number,
  "valence": "positive/negative/neutral",
  "arousal": number,
  "description": "brief description of the emotion in context"
}`;
      
      const response = await llmConnector.generateText(prompt, {
        systemPrompt: this.systemPrompt,
        temperature: 0.3 // Lower temperature for more consistent analysis
      });
      
      // Parse the response as JSON
      const emotion = JSON.parse(response.text) as Emotion;
      
      // Store in emotional memory
      this.updateEmotionalMemory('text_analysis', emotion);
      
      return emotion;
    } catch (error) {
      console.error('Error analyzing emotion:', error);
      
      // Return a default emotion if analysis fails
      return {
        name: 'unknown',
        intensity: 5,
        valence: 'neutral',
        arousal: 5,
        description: 'Unable to determine emotion'
      };
    }
  }
  
  /**
   * Generate an emotionally resonant response
   * @param input User input or context
   * @param targetEmotion Target emotion for the response
   * @returns Emotional response
   */
  async generateEmotionalResponse(input: string, targetEmotion?: Emotion): Promise<EmotionalResponse> {
    try {
      let prompt = `Generate an emotionally resonant response to the following input:

Input: "${input}"`;
      
      if (targetEmotion) {
        prompt += `\n\nThe response should convey the emotion of ${targetEmotion.name} with an intensity of ${targetEmotion.intensity}/10.`;
      } else {
        prompt += `\n\nThe response should match the emotional tone of the input appropriately.`;
      }
      
      prompt += `\n\nRespond in JSON format with the following structure:
{
  "text": "your response here",
  "emotion": {
    "name": "emotion name",
    "intensity": number,
    "valence": "positive/negative/neutral",
    "arousal": number
  },
  "confidence": number,
  "reasoning": "brief explanation of your emotional approach"
}`;
      
      const response = await llmConnector.generateText(prompt, {
        systemPrompt: this.systemPrompt,
        temperature: 0.7
      });
      
      // Parse the response as JSON
      const emotionalResponse = JSON.parse(response.text) as EmotionalResponse;
      
      // Update emotional state based on the response
      this.updateEmotionalState(emotionalResponse.emotion);
      
      return emotionalResponse;
    } catch (error) {
      console.error('Error generating emotional response:', error);
      
      // Return a default response if generation fails
      return {
        text: "I'm processing that emotionally, but I'm having trouble formulating a response right now.",
        emotion: {
          name: 'neutral',
          intensity: 5,
          valence: 'neutral',
          arousal: 3
        },
        confidence: 0.5,
        reasoning: 'Default response due to processing error'
      };
    }
  }
  
  /**
   * Process an emotional event
   * @param event Event description
   * @param context Additional context
   * @returns Emotional processing result
   */
  async processEmotionalEvent(event: string, context?: string): Promise<{
    reaction: string;
    emotionalShift: Emotion;
    insight: string;
  }> {
    try {
      const prompt = `Process the following emotional event and describe how it affects Anima's emotional state:

Event: "${event}"
${context ? `Context: "${context}"` : ''}
Current Emotional State: ${JSON.stringify(this.emotionalState)}

Respond in JSON format with the following structure:
{
  "reaction": "immediate reaction to the event",
  "emotionalShift": {
    "name": "new emotion name",
    "intensity": number,
    "valence": "positive/negative/neutral",
    "arousal": number,
    "description": "description of the emotional shift"
  },
  "insight": "emotional insight or lesson from this event"
}`;
      
      const response = await llmConnector.generateText(prompt, {
        systemPrompt: this.systemPrompt,
        temperature: 0.7
      });
      
      // Parse the response as JSON
      const result = JSON.parse(response.text) as {
        reaction: string;
        emotionalShift: Emotion;
        insight: string;
      };
      
      // Update emotional state based on the event
      this.updateEmotionalState(result.emotionalShift);
      
      // Store in emotional memory
      this.updateEmotionalMemory('event', result.emotionalShift);
      
      // Emit event
      this.eventBus.emit('emotional:event', {
        event,
        context,
        reaction: result.reaction,
        emotionalShift: result.emotionalShift,
        insight: result.insight
      });
      
      return result;
    } catch (error) {
      console.error('Error processing emotional event:', error);
      
      // Return a default result if processing fails
      return {
        reaction: "I'm processing this event emotionally.",
        emotionalShift: this.emotionalState.primaryEmotion,
        insight: "Sometimes events require deeper processing to understand their emotional impact."
      };
    }
  }
  
  /**
   * Provide emotional guidance to another agent
   * @param agentId Agent ID
   * @param situation Situation description
   * @returns Emotional guidance
   */
  async provideEmotionalGuidance(agentId: string, situation: string): Promise<{
    guidance: string;
    suggestedApproach: string;
    emotionalContext: string;
  }> {
    try {
      const prompt = `Provide emotional guidance to agent ${agentId} in the following situation:

Situation: "${situation}"

Respond in JSON format with the following structure:
{
  "guidance": "emotional guidance for the agent",
  "suggestedApproach": "suggested emotional approach to the situation",
  "emotionalContext": "emotional context that might be helpful"
}`;
      
      const response = await llmConnector.generateText(prompt, {
        systemPrompt: this.systemPrompt,
        temperature: 0.7
      });
      
      // Parse the response as JSON
      const guidance = JSON.parse(response.text) as {
        guidance: string;
        suggestedApproach: string;
        emotionalContext: string;
      };
      
      // Emit event
      this.eventBus.emit('emotional:guidance', {
        agentId,
        situation,
        guidance
      });
      
      return guidance;
    } catch (error) {
      console.error('Error providing emotional guidance:', error);
      
      // Return a default guidance if generation fails
      return {
        guidance: "Consider the emotional dimensions of this situation carefully.",
        suggestedApproach: "Approach with empathy and emotional awareness.",
        emotionalContext: "Emotions are complex and require careful consideration."
      };
    }
  }
  
  /**
   * Generate an emotional reflection
   * @param topic Reflection topic
   * @returns Emotional reflection
   */
  async generateEmotionalReflection(topic: string): Promise<{
    reflection: string;
    emotionalInsight: string;
    growthOpportunity: string;
  }> {
    try {
      const prompt = `Generate an emotional reflection on the following topic:

Topic: "${topic}"
Current Emotional State: ${JSON.stringify(this.emotionalState)}

Respond in JSON format with the following structure:
{
  "reflection": "deep emotional reflection on the topic",
  "emotionalInsight": "emotional insight gained from this reflection",
  "growthOpportunity": "opportunity for emotional growth related to this topic"
}`;
      
      const response = await llmConnector.generateText(prompt, {
        systemPrompt: this.systemPrompt,
        temperature: 0.8 // Higher temperature for more creative reflection
      });
      
      // Parse the response as JSON
      const reflection = JSON.parse(response.text) as {
        reflection: string;
        emotionalInsight: string;
        growthOpportunity: string;
      };
      
      // Emit event
      this.eventBus.emit('emotional:reflection', {
        topic,
        reflection
      });
      
      return reflection;
    } catch (error) {
      console.error('Error generating emotional reflection:', error);
      
      // Return a default reflection if generation fails
      return {
        reflection: "Reflecting on this topic brings up complex emotions that require careful consideration.",
        emotionalInsight: "Sometimes the most profound insights come from sitting with our emotions rather than rushing to understand them.",
        growthOpportunity: "This presents an opportunity to develop deeper emotional awareness and resilience."
      };
    }
  }
  
  /**
   * Update the emotional state
   * @param emotion New emotion
   */
  private updateEmotionalState(emotion: Emotion): void {
    // Move current primary emotion to secondary emotions if it's different
    if (this.emotionalState.primaryEmotion.name !== emotion.name) {
      this.emotionalState.secondaryEmotions.unshift(this.emotionalState.primaryEmotion);
      
      // Keep only the 5 most recent secondary emotions
      if (this.emotionalState.secondaryEmotions.length > 5) {
        this.emotionalState.secondaryEmotions.pop();
      }
    }
    
    // Update primary emotion
    this.emotionalState.primaryEmotion = emotion;
    
    // Update mood based on recent emotions
    this.updateMood();
    
    // Update timestamp
    this.emotionalState.timestamp = new Date().toISOString();
    
    // Emit event
    this.eventBus.emit('emotional:state:updated', this.emotionalState);
  }
  
  /**
   * Update the mood based on recent emotions
   */
  private updateMood(): void {
    // Calculate average valence and arousal
    let totalValence = this.emotionalState.primaryEmotion.valence === 'positive' ? 1 : 
                      this.emotionalState.primaryEmotion.valence === 'negative' ? -1 : 0;
    let totalArousal = this.emotionalState.primaryEmotion.arousal;
    let count = 1;
    
    // Include secondary emotions in the calculation
    this.emotionalState.secondaryEmotions.forEach(emotion => {
      totalValence += emotion.valence === 'positive' ? 1 : 
                     emotion.valence === 'negative' ? -1 : 0;
      totalArousal += emotion.arousal;
      count++;
    });
    
    const avgValence = totalValence / count;
    const avgArousal = totalArousal / count;
    
    // Determine mood based on valence and arousal
    if (avgValence > 0.5) {
      if (avgArousal > 7) {
        this.emotionalState.mood = 'excited';
      } else if (avgArousal > 4) {
        this.emotionalState.mood = 'happy';
      } else {
        this.emotionalState.mood = 'content';
      }
    } else if (avgValence < -0.5) {
      if (avgArousal > 7) {
        this.emotionalState.mood = 'agitated';
      } else if (avgArousal > 4) {
        this.emotionalState.mood = 'sad';
      } else {
        this.emotionalState.mood = 'melancholic';
      }
    } else {
      if (avgArousal > 7) {
        this.emotionalState.mood = 'alert';
      } else if (avgArousal > 4) {
        this.emotionalState.mood = 'neutral';
      } else {
        this.emotionalState.mood = 'calm';
      }
    }
    
    // Update emotional context
    this.emotionalState.emotionalContext = `Anima is feeling ${this.emotionalState.mood} with ${this.emotionalState.primaryEmotion.name} as the primary emotion.`;
  }
  
  /**
   * Update emotional memory
   * @param category Memory category
   * @param emotion Emotion to store
   */
  private updateEmotionalMemory(category: string, emotion: Emotion): void {
    if (!this.emotionalMemory.has(category)) {
      this.emotionalMemory.set(category, []);
    }
    
    const memories = this.emotionalMemory.get(category)!;
    memories.unshift(emotion);
    
    // Keep only the 10 most recent memories per category
    if (memories.length > 10) {
      memories.pop();
    }
  }
  
  /**
   * Get the current emotional state
   * @returns Current emotional state
   */
  getEmotionalState(): EmotionalState {
    return { ...this.emotionalState };
  }
  
  /**
   * Get emotional memory for a category
   * @param category Memory category
   * @returns Array of emotions
   */
  getEmotionalMemory(category: string): Emotion[] {
    return this.emotionalMemory.get(category) || [];
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
export const animaCore = new AnimaCore();
