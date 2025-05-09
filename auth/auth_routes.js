/**
 * SoulCoreHub Authentication Routes
 * 
 * This module provides API routes for user authentication:
 * - User registration
 * - Login
 * - Password reset
 * - Token refresh
 */

const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');
const { getSecrets } = require('../aws/secrets_manager');

// In production, this would be a database connection
// For now, we'll use an in-memory store for demonstration
const users = {};

/**
 * Get JWT secret from AWS Secrets Manager or environment variable
 */
async function getJwtSecret() {
  try {
    const secrets = await getSecrets('SoulCoreSecrets');
    return secrets.JWT_SECRET;
  } catch (error) {
    console.warn('Failed to fetch JWT secret from AWS Secrets Manager, falling back to environment variable');
    return process.env.JWT_SECRET;
  }
}

/**
 * Generate JWT token for a user
 */
async function generateToken(user) {
  const jwtSecret = await getJwtSecret();
  
  // Create token payload
  const payload = {
    id: user.id,
    email: user.email,
    role: user.role || 'user',
    tier: user.subscription?.tier || 'free'
  };
  
  // Sign token with 24 hour expiration
  return jwt.sign(payload, jwtSecret, { expiresIn: '24h' });
}

/**
 * @route POST /auth/register
 * @desc Register a new user
 * @access Public
 */
router.post('/register', async (req, res) => {
  try {
    const { email, password, name } = req.body;
    
    // Validate input
    if (!email || !password) {
      return res.status(400).json({ 
        success: false, 
        error: 'Missing required fields',
        message: 'Email and password are required'
      });
    }
    
    // Check if user already exists
    if (Object.values(users).some(user => user.email === email)) {
      return res.status(400).json({ 
        success: false, 
        error: 'User already exists',
        message: 'A user with this email already exists'
      });
    }
    
    // Hash password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);
    
    // Create user ID
    const id = uuidv4();
    
    // Create user object
    const user = {
      id,
      email,
      password: hashedPassword,
      name: name || email.split('@')[0],
      role: 'user',
      createdAt: new Date().toISOString(),
      subscription: {
        tier: 'free',
        status: 'active'
      }
    };
    
    // Store user
    users[id] = user;
    
    // Generate token
    const token = await generateToken(user);
    
    // Return success with token
    return res.status(201).json({
      success: true,
      message: 'User registered successfully',
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
        subscription: user.subscription
      }
    });
  } catch (error) {
    console.error('Registration error:', error);
    return res.status(500).json({ 
      success: false, 
      error: 'Server error',
      message: 'An error occurred during registration'
    });
  }
});

/**
 * @route POST /auth/login
 * @desc Authenticate user & get token
 * @access Public
 */
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Validate input
    if (!email || !password) {
      return res.status(400).json({ 
        success: false, 
        error: 'Missing required fields',
        message: 'Email and password are required'
      });
    }
    
    // Find user by email
    const user = Object.values(users).find(user => user.email === email);
    
    // Check if user exists
    if (!user) {
      return res.status(400).json({ 
        success: false, 
        error: 'Invalid credentials',
        message: 'Invalid email or password'
      });
    }
    
    // Check password
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(400).json({ 
        success: false, 
        error: 'Invalid credentials',
        message: 'Invalid email or password'
      });
    }
    
    // Generate token
    const token = await generateToken(user);
    
    // Return success with token
    return res.json({
      success: true,
      message: 'Login successful',
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
        subscription: user.subscription
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    return res.status(500).json({ 
      success: false, 
      error: 'Server error',
      message: 'An error occurred during login'
    });
  }
});

/**
 * @route POST /auth/refresh
 * @desc Refresh JWT token
 * @access Private
 */
router.post('/refresh', async (req, res) => {
  try {
    const { token } = req.body;
    
    if (!token) {
      return res.status(400).json({ 
        success: false, 
        error: 'Token required',
        message: 'Refresh token is required'
      });
    }
    
    // Get JWT secret
    const jwtSecret = await getJwtSecret();
    
    // Verify token
    const decoded = jwt.verify(token, jwtSecret);
    
    // Get user
    const user = users[decoded.id];
    
    if (!user) {
      return res.status(400).json({ 
        success: false, 
        error: 'Invalid token',
        message: 'User not found'
      });
    }
    
    // Generate new token
    const newToken = await generateToken(user);
    
    // Return success with new token
    return res.json({
      success: true,
      message: 'Token refreshed',
      token: newToken
    });
  } catch (error) {
    console.error('Token refresh error:', error);
    return res.status(401).json({ 
      success: false, 
      error: 'Invalid token',
      message: 'Invalid or expired token'
    });
  }
});

/**
 * @route POST /auth/forgot-password
 * @desc Request password reset
 * @access Public
 */
router.post('/forgot-password', async (req, res) => {
  try {
    const { email } = req.body;
    
    if (!email) {
      return res.status(400).json({ 
        success: false, 
        error: 'Email required',
        message: 'Email is required'
      });
    }
    
    // Find user by email
    const user = Object.values(users).find(user => user.email === email);
    
    // Don't reveal if user exists or not for security
    if (!user) {
      return res.json({
        success: true,
        message: 'If your email is registered, you will receive a password reset link'
      });
    }
    
    // Generate reset token
    const resetToken = uuidv4();
    
    // In a real app, store this token in the database with an expiration
    user.resetToken = resetToken;
    user.resetTokenExpires = new Date(Date.now() + 3600000); // 1 hour
    
    // In a real app, send an email with the reset link
    console.log(`Password reset link for ${email}: /reset-password?token=${resetToken}`);
    
    return res.json({
      success: true,
      message: 'If your email is registered, you will receive a password reset link'
    });
  } catch (error) {
    console.error('Password reset request error:', error);
    return res.status(500).json({ 
      success: false, 
      error: 'Server error',
      message: 'An error occurred while processing your request'
    });
  }
});

/**
 * @route POST /auth/reset-password
 * @desc Reset password with token
 * @access Public
 */
router.post('/reset-password', async (req, res) => {
  try {
    const { token, password } = req.body;
    
    if (!token || !password) {
      return res.status(400).json({ 
        success: false, 
        error: 'Missing required fields',
        message: 'Token and new password are required'
      });
    }
    
    // Find user by reset token
    const user = Object.values(users).find(user => 
      user.resetToken === token && 
      user.resetTokenExpires > new Date()
    );
    
    if (!user) {
      return res.status(400).json({ 
        success: false, 
        error: 'Invalid token',
        message: 'Password reset token is invalid or has expired'
      });
    }
    
    // Hash new password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);
    
    // Update user password
    user.password = hashedPassword;
    
    // Clear reset token
    delete user.resetToken;
    delete user.resetTokenExpires;
    
    return res.json({
      success: true,
      message: 'Password has been reset successfully'
    });
  } catch (error) {
    console.error('Password reset error:', error);
    return res.status(500).json({ 
      success: false, 
      error: 'Server error',
      message: 'An error occurred while resetting your password'
    });
  }
});

/**
 * @route GET /auth/me
 * @desc Get current user
 * @access Private
 */
router.get('/me', async (req, res) => {
  try {
    // User is added to req by auth middleware
    const user = users[req.user.id];
    
    if (!user) {
      return res.status(404).json({ 
        success: false, 
        error: 'User not found',
        message: 'User not found'
      });
    }
    
    return res.json({
      success: true,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
        subscription: user.subscription
      }
    });
  } catch (error) {
    console.error('Get user error:', error);
    return res.status(500).json({ 
      success: false, 
      error: 'Server error',
      message: 'An error occurred while fetching user data'
    });
  }
});

module.exports = router;
