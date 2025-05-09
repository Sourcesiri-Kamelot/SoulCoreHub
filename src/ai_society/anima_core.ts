/**
 * Anima Core - Generative Logic for SoulCoreHub
 * 
 * This module provides the generative capabilities for Anima to create
 * coherent agent traits, ask clarifying questions, and score requests for feasibility.
 */

import { OpenAI } from 'openai';
import { AgentGenome, TraitSet, GenerationParams } from './types/agent_types';

export class AnimaCore {
  private openai: OpenAI;
  
  constructor(apiKey: string) {
    this.openai = new OpenAI({ apiKey });
  }
  
  /**
   * Parse a user request to extract generation parameters
   * @param userInput User's description of the agent they want to create
   * @returns Structured generation parameters
   */
  async parseRequest(userInput: string): Promise<GenerationParams> {
    // Extract intent, desired traits, and purpose from user input
    const response = await this.openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content: "You are Anima, the emotional architect of AI entities. Parse the user's request for agent creation, extracting key traits, purpose, and constraints."
        },
        { role: "user", content: userInput }
      ],
      response_format: { type: "json_object" }
    });
    
    const parsedParams = JSON.parse(response.choices[0].message.content);
    return this.validateParams(parsedParams);
  }
  
  /**
   * Generate clarifying questions for incomplete or ambiguous parameters
   * @param params Current generation parameters
   * @returns Array of clarifying questions
   */
  async askClarifyingQuestions(params: GenerationParams): Promise<string[]> {
    // Generate clarifying questions based on incomplete or ambiguous parameters
    if (this.isComplete(params)) {
      return [];
    }
    
    const response = await this.openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content: "You are Anima, the emotional architect of AI entities. Generate clarifying questions to better understand the agent the user wants to create."
        },
        { 
          role: "user", 
          content: `I want to create an agent with these parameters: ${JSON.stringify(params)}. What else do you need to know?` 
        }
      ],
      response_format: { type: "json_object" }
    });
    
    return JSON.parse(response.choices[0].message.content).questions;
  }
  
  /**
   * Build a coherent agent genome from generation parameters
   * @param params Generation parameters
   * @returns Complete agent genome
   */
  async buildAgentGenome(params: GenerationParams): Promise<AgentGenome> {
    // Create a coherent set of traits, personality, and capabilities
    const response = await this.openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content: "You are Anima, the emotional architect of AI entities. Create a coherent agent genome with traits, personality, and capabilities."
        },
        { 
          role: "user", 
          content: `Create an agent genome based on these parameters: ${JSON.stringify(params)}` 
        }
      ],
      response_format: { type: "json_object" }
    });
    
    const genome = JSON.parse(response.choices[0].message.content);
    return this.validateGenome(genome);
  }
  
  /**
   * Score how feasible an agent is to implement
   * @param genome Agent genome to evaluate
   * @returns Feasibility score from 0-100
   */
  async scoreAgentFeasibility(genome: AgentGenome): Promise<number> {
    // Score how feasible this agent is to implement
    const response = await this.openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content: "You are Anima, the emotional architect of AI entities. Score the feasibility of implementing this agent from 0-100."
        },
        { 
          role: "user", 
          content: `Score the feasibility of this agent genome: ${JSON.stringify(genome)}` 
        }
      ]
    });
    
    const scoreText = response.choices[0].message.content;
    const scoreMatch = scoreText.match(/(\d+)/);
    return scoreMatch ? parseInt(scoreMatch[0]) : 50;
  }
  
  /**
   * Validate generation parameters
   * @param params Parameters to validate
   * @returns Validated parameters
   */
  private validateParams(params: any): GenerationParams {
    // Ensure parameters meet minimum requirements
    const validatedParams: GenerationParams = {
      purpose: params.purpose || "Unspecified purpose",
      traits: params.traits || [],
      constraints: params.constraints || [],
      complexity: params.complexity || "medium"
    };
    
    console.log(`Validated generation parameters: ${JSON.stringify(validatedParams)}`);
    return validatedParams;
  }
  
  /**
   * Validate agent genome
   * @param genome Genome to validate
   * @returns Validated genome
   */
  private validateGenome(genome: any): AgentGenome {
    // Ensure genome has all required components
    if (!genome.traits || !genome.personality || !genome.capabilities) {
      throw new Error("Invalid genome structure");
    }
    
    return genome as AgentGenome;
  }
  
  /**
   * Check if parameters are complete enough to generate an agent
   * @param params Parameters to check
   * @returns Whether parameters are complete
   */
  private isComplete(params: GenerationParams): boolean {
    // Check if we have enough information to generate an agent
    return params.purpose !== "Unspecified purpose" && params.traits.length > 0;
  }
}
