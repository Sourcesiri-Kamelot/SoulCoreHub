/**
 * API Integration for AI Society
 * 
 * This module exports the API routes and WebSocket handler for the AI Society.
 */

import societyApi from './society_api';
import { setupSocietyWebsocket } from './society_websocket';

export {
  societyApi,
  setupSocietyWebsocket
};
