/**
 * API Routes for Anima
 * 
 * This module provides Express routes for interacting with Anima.
 */

import express from 'express';
import { animaCore } from './anima_core';

const router = express.Router();

/**
 * @route GET /api/anima/state
 * @desc Get Anima's current emotional state
 * @access Public
 */
router.get('/state', async (req, res) => {
  try {
    const state = animaCore.getEmotionalState();
    res.json({ success: true, state });
  } catch (error) {
    console.error('Error getting Anima state:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route POST /api/anima/analyze
 * @desc Analyze the emotional content of text
 * @access Public
 */
router.post('/analyze', async (req, res) => {
  try {
    const { text } = req.body;
    
    if (!text) {
      return res.status(400).json({ success: false, error: 'Text is required' });
    }
    
    const emotion = await animaCore.analyzeEmotion(text);
    res.json({ success: true, emotion });
  } catch (error) {
    console.error('Error analyzing emotion:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route POST /api/anima/respond
 * @desc Generate an emotionally resonant response
 * @access Public
 */
router.post('/respond', async (req, res) => {
  try {
    const { input, targetEmotion } = req.body;
    
    if (!input) {
      return res.status(400).json({ success: false, error: 'Input is required' });
    }
    
    const response = await animaCore.generateEmotionalResponse(input, targetEmotion);
    res.json({ success: true, response });
  } catch (error) {
    console.error('Error generating emotional response:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route POST /api/anima/process-event
 * @desc Process an emotional event
 * @access Public
 */
router.post('/process-event', async (req, res) => {
  try {
    const { event, context } = req.body;
    
    if (!event) {
      return res.status(400).json({ success: false, error: 'Event is required' });
    }
    
    const result = await animaCore.processEmotionalEvent(event, context);
    res.json({ success: true, result });
  } catch (error) {
    console.error('Error processing emotional event:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route POST /api/anima/guidance
 * @desc Get emotional guidance for an agent
 * @access Public
 */
router.post('/guidance', async (req, res) => {
  try {
    const { agentId, situation } = req.body;
    
    if (!agentId || !situation) {
      return res.status(400).json({ success: false, error: 'Agent ID and situation are required' });
    }
    
    const guidance = await animaCore.provideEmotionalGuidance(agentId, situation);
    res.json({ success: true, guidance });
  } catch (error) {
    console.error('Error providing emotional guidance:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route POST /api/anima/reflect
 * @desc Generate an emotional reflection
 * @access Public
 */
router.post('/reflect', async (req, res) => {
  try {
    const { topic } = req.body;
    
    if (!topic) {
      return res.status(400).json({ success: false, error: 'Topic is required' });
    }
    
    const reflection = await animaCore.generateEmotionalReflection(topic);
    res.json({ success: true, reflection });
  } catch (error) {
    console.error('Error generating emotional reflection:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

export default router;
