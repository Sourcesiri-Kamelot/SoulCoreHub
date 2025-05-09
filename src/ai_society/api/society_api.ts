/**
 * API Routes for AI Society
 * 
 * This module provides Express routes for interacting with the AI Society.
 */

import express from 'express';
import { aiSociety } from '../index';

const router = express.Router();

/**
 * @route POST /api/society/start
 * @desc Start the AI Society
 * @access Public
 */
router.post('/start', async (req, res) => {
  try {
    await aiSociety.start();
    res.json({ success: true, message: 'AI Society started successfully' });
  } catch (error) {
    console.error('Error starting AI Society', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route POST /api/society/stop
 * @desc Stop the AI Society
 * @access Public
 */
router.post('/stop', async (req, res) => {
  try {
    await aiSociety.stop();
    res.json({ success: true, message: 'AI Society stopped successfully' });
  } catch (error) {
    console.error('Error stopping AI Society', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route POST /api/society/agents
 * @desc Create a new agent
 * @access Public
 */
router.post('/agents', async (req, res) => {
  try {
    const { description } = req.body;
    
    if (!description) {
      return res.status(400).json({ success: false, error: 'Agent description is required' });
    }
    
    const result = await aiSociety.createAgent(description);
    res.json({ success: true, message: result });
  } catch (error) {
    console.error('Error creating agent', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route GET /api/society/agents/:agentId
 * @desc Get agent status
 * @access Public
 */
router.get('/agents/:agentId', async (req, res) => {
  try {
    const { agentId } = req.params;
    const status = await aiSociety.getAgentStatus(agentId);
    res.json({ success: true, agent: status });
  } catch (error) {
    console.error(`Error getting agent status for ${req.params.agentId}`, error);
    res.status(404).json({ success: false, error: error.message });
  }
});

/**
 * @route GET /api/society/stats
 * @desc Get simulation stats
 * @access Public
 */
router.get('/stats', async (req, res) => {
  try {
    const stats = await aiSociety.getSimulationStats();
    res.json({ success: true, stats });
  } catch (error) {
    console.error('Error getting simulation stats', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route POST /api/society/interactions
 * @desc Trigger interaction between agents
 * @access Public
 */
router.post('/interactions', async (req, res) => {
  try {
    const { agentId1, agentId2, topic } = req.body;
    
    if (!agentId1 || !agentId2 || !topic) {
      return res.status(400).json({ 
        success: false, 
        error: 'Agent IDs and topic are required' 
      });
    }
    
    const result = await aiSociety.triggerInteraction(agentId1, agentId2, topic);
    res.json({ success: true, message: result });
  } catch (error) {
    console.error('Error triggering interaction', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

export default router;
