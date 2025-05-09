/**
 * SoulCoreHub Authentication Middleware
 * 
 * This middleware handles JWT authentication for API routes
 * and provides user context to route handlers.
 */

const jwt = require('jsonwebtoken');
const { getSecrets } = require('../aws/secrets_manager');

// Cache for secrets to avoid repeated calls to AWS Secrets Manager
let secretsCache = null;
let secretsLastFetched = 0;
const SECRETS_CACHE_TTL = 3600000; // 1 hour in milliseconds

/**
 * Get JWT secret from AWS Secrets Manager or environment variable
 */
async function getJwtSecret() {
  const now = Date.now();
  
  // Use cached secrets if available and not expired
  if (secretsCache && (now - secretsLastFetched < SECRETS_CACHE_TTL)) {
    return secretsCache.JWT_SECRET;
  }
  
  try {
    // Try to get from AWS Secrets Manager
    const secrets = await getSecrets('SoulCoreSecrets');
    secretsCache = secrets;
    secretsLastFetched = now;
    return secrets.JWT_SECRET;
  } catch (error) {
    console.warn('Failed to fetch JWT secret from AWS Secrets Manager, falling back to environment variable');
    // Fall back to environment variable
    return process.env.JWT_SECRET;
  }
}

/**
 * Authentication middleware for protecting API routes
 */
async function authMiddleware(req, res, next) {
  // Skip auth for public routes
  if (req.path.startsWith('/public') || req.path === '/health' || req.path === '/webhook/stripe') {
    return next();
  }
  
  // Get token from Authorization header
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ 
      success: false, 
      error: 'Authentication required',
      message: 'No valid authentication token provided'
    });
  }
  
  const token = authHeader.split(' ')[1];
  
  try {
    // Get JWT secret
    const jwtSecret = await getJwtSecret();
    
    // Verify token
    const decoded = jwt.verify(token, jwtSecret);
    
    // Check if token is expired
    const now = Math.floor(Date.now() / 1000);
    if (decoded.exp && decoded.exp < now) {
      return res.status(401).json({ 
        success: false, 
        error: 'Token expired',
        message: 'Your session has expired, please log in again'
      });
    }
    
    // Add user info to request object
    req.user = decoded;
    
    // Continue to next middleware or route handler
    next();
  } catch (error) {
    console.error('Authentication error:', error.message);
    return res.status(401).json({ 
      success: false, 
      error: 'Invalid token',
      message: 'Your authentication token is invalid'
    });
  }
}

/**
 * Role-based authorization middleware
 * @param {Array} allowedRoles - Array of roles allowed to access the route
 */
function authorizeRoles(allowedRoles) {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ 
        success: false, 
        error: 'Authentication required',
        message: 'You must be logged in to access this resource'
      });
    }
    
    const userRole = req.user.role || 'user';
    
    if (allowedRoles.includes(userRole)) {
      next();
    } else {
      return res.status(403).json({ 
        success: false, 
        error: 'Insufficient permissions',
        message: 'You do not have permission to access this resource'
      });
    }
  };
}

module.exports = {
  authMiddleware,
  authorizeRoles
};
