/**
 * API Gateway for SoulCoreHub
 * 
 * This module sets up the API Gateway for SoulCoreHub, providing a unified interface
 * for accessing the system's functionality.
 */

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { animaApi } from '../agents/anima';

/**
 * Set up the API Gateway
 * @param app Express application
 */
export function setupApiGateway(app: express.Application) {
  // Security middleware
  app.use(helmet());
  app.use(cors());
  
  // Rate limiting
  const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
    standardHeaders: true,
    legacyHeaders: false,
    message: {
      success: false,
      error: 'Too many requests',
      message: 'Too many requests from this IP, please try again later'
    }
  });
  app.use('/api', limiter);
  
  // API routes
  app.use('/api/anima', animaApi);
  
  // Health check
  app.get('/api/health', (req, res) => {
    res.json({ 
      status: 'ok', 
      timestamp: new Date().toISOString() 
    });
  });
  
  console.log('API Gateway initialized');
}
