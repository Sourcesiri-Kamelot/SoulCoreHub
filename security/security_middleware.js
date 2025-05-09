/**
 * SoulCoreHub Security Middleware
 * 
 * This module provides security middleware for Express:
 * - Content Security Policy
 * - XSS Protection
 * - CSRF Protection
 * - Rate Limiting
 * - Input Validation
 */

const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { body, validationResult } = require('express-validator');
const csrf = require('csurf');
const { v4: uuidv4 } = require('uuid');

/**
 * Configure security headers using helmet
 */
function securityHeaders() {
  return helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'", "'unsafe-inline'", "js.stripe.com"],
        styleSrc: ["'self'", "'unsafe-inline'", "fonts.googleapis.com"],
        imgSrc: ["'self'", "data:", "*.stripe.com"],
        connectSrc: ["'self'", "api.stripe.com"],
        fontSrc: ["'self'", "fonts.gstatic.com"],
        objectSrc: ["'none'"],
        mediaSrc: ["'self'"],
        frameSrc: ["js.stripe.com"]
      }
    },
    xssFilter: true,
    noSniff: true,
    referrerPolicy: { policy: 'same-origin' }
  });
}

/**
 * Configure rate limiting
 * @param {Object} options - Rate limiting options
 */
function rateLimiter(options = {}) {
  const defaultOptions = {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
    standardHeaders: true,
    legacyHeaders: false,
    message: {
      success: false,
      error: 'Too many requests',
      message: 'Too many requests from this IP, please try again later'
    }
  };
  
  return rateLimit({ ...defaultOptions, ...options });
}

/**
 * Configure stricter rate limiting for sensitive routes
 */
function strictRateLimiter() {
  return rateLimiter({
    windowMs: 60 * 60 * 1000, // 1 hour
    max: 10, // limit each IP to 10 requests per hour
    message: {
      success: false,
      error: 'Too many attempts',
      message: 'Too many attempts from this IP, please try again later'
    }
  });
}

/**
 * Configure CSRF protection
 */
function csrfProtection() {
  return csrf({ cookie: true });
}

/**
 * Validate registration input
 */
const validateRegistration = [
  body('email')
    .isEmail()
    .withMessage('Please provide a valid email address')
    .normalizeEmail(),
  body('password')
    .isLength({ min: 8 })
    .withMessage('Password must be at least 8 characters long')
    .matches(/[a-z]/)
    .withMessage('Password must contain at least one lowercase letter')
    .matches(/[A-Z]/)
    .withMessage('Password must contain at least one uppercase letter')
    .matches(/[0-9]/)
    .withMessage('Password must contain at least one number'),
  body('name')
    .optional()
    .isLength({ min: 2 })
    .withMessage('Name must be at least 2 characters long')
    .trim()
    .escape()
];

/**
 * Validate login input
 */
const validateLogin = [
  body('email')
    .isEmail()
    .withMessage('Please provide a valid email address')
    .normalizeEmail(),
  body('password')
    .notEmpty()
    .withMessage('Password is required')
];

/**
 * Validate subscription input
 */
const validateSubscription = [
  body('planTier')
    .isIn(['free', 'pro', 'enterprise', 'trader', 'trader_pro'])
    .withMessage('Invalid subscription plan')
];

/**
 * Handle validation errors
 */
function handleValidationErrors(req, res, next) {
  const errors = validationResult(req);
  
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      error: 'Validation error',
      message: 'Please check your input',
      errors: errors.array()
    });
  }
  
  next();
}

/**
 * Generate request ID middleware
 */
function requestId() {
  return (req, res, next) => {
    req.id = uuidv4();
    res.setHeader('X-Request-ID', req.id);
    next();
  };
}

/**
 * Log requests middleware
 */
function requestLogger() {
  return (req, res, next) => {
    const start = Date.now();
    
    // Log when response is finished
    res.on('finish', () => {
      const duration = Date.now() - start;
      console.log(`${req.method} ${req.originalUrl} ${res.statusCode} ${duration}ms [${req.id}]`);
    });
    
    next();
  };
}

/**
 * Sanitize request parameters middleware
 */
function sanitizeParams() {
  return (req, res, next) => {
    // Sanitize query parameters
    if (req.query) {
      Object.keys(req.query).forEach(key => {
        if (typeof req.query[key] === 'string') {
          req.query[key] = req.query[key].trim();
        }
      });
    }
    
    // Sanitize body parameters
    if (req.body) {
      Object.keys(req.body).forEach(key => {
        if (typeof req.body[key] === 'string') {
          req.body[key] = req.body[key].trim();
        }
      });
    }
    
    next();
  };
}

module.exports = {
  securityHeaders,
  rateLimiter,
  strictRateLimiter,
  csrfProtection,
  validateRegistration,
  validateLogin,
  validateSubscription,
  handleValidationErrors,
  requestId,
  requestLogger,
  sanitizeParams
};
