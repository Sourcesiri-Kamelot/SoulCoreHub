/**
 * Agent Types for SoulCoreHub AI Society
 * 
 * These types define the structure of agents, their traits, and generation parameters.
 */

export interface TraitSet {
  name: string;
  strength: number;
}

export interface AgentGenome {
  name: string;
  description?: string;
  traits: TraitSet[];
  personality: {
    openness: number;
    conscientiousness: number;
    extraversion: number;
    agreeableness: number;
    neuroticism: number;
  };
  capabilities: {
    name: string;
    level: number;
  }[];
}

export interface GenerationParams {
  purpose: string;
  traits: string[];
  constraints: string[];
  complexity: 'simple' | 'medium' | 'complex';
}
