/**
 * Lil Playbook - Main Application Server
 * 
 * A sports learning platform for kids ages 5-17
 */

const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');
const AWS = require('aws-sdk');
const multer = require('multer');
const { v4: uuidv4 } = require('uuid');

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// Database connection (replace with actual credentials from CredentialsAgent)
mongoose.connect('mongodb://localhost:27017/lil_playbook', {
  useNewUrlParser: true,
  useUnifiedTopology: true
})
.then(() => console.log('Connected to MongoDB'))
.catch(err => console.error('MongoDB connection error:', err));

// Configure AWS (credentials would come from CredentialsAgent)
const s3 = new AWS.S3({
  region: 'us-west-2'
});

// Set up file upload with multer
const storage = multer.memoryStorage();
const upload = multer({
  storage: storage,
  limits: {
    fileSize: 50 * 1024 * 1024, // 50MB limit
  },
  fileFilter: (req, file, cb) => {
    // Only allow video files
    if (file.mimetype.startsWith('video/')) {
      cb(null, true);
    } else {
      cb(new Error('Only video files are allowed'));
    }
  }
});

// Define schemas
const userSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  age: { type: Number, required: true },
  parentEmail: { type: String, required: true },
  parentVerified: { type: Boolean, default: false },
  favoritesSports: [String],
  skillLevel: { type: String, enum: ['beginner', 'intermediate', 'advanced'] },
  createdAt: { type: Date, default: Date.now },
  lastLogin: Date
});

const videoSchema = new mongoose.Schema({
  title: { type: String, required: true },
  description: String,
  s3Key: { type: String, required: true },
  thumbnailKey: String,
  uploadedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  sport: { type: String, required: true },
  ageRange: {
    min: { type: Number, required: true },
    max: { type: Number, required: true }
  },
  skillLevel: { type: String, enum: ['beginner', 'intermediate', 'advanced'] },
  isProHighlight: { type: Boolean, default: false },
  isDrill: { type: Boolean, default: false },
  isUserHighlight: { type: Boolean, default: false },
  approved: { type: Boolean, default: false },
  views: { type: Number, default: 0 },
  likes: { type: Number, default: 0 },
  tags: [String],
  createdAt: { type: Date, default: Date.now }
});

const trainerSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  bio: String,
  sports: [String],
  specialties: [String],
  experience: Number, // years
  virtualSessionsAvailable: { type: Boolean, default: true },
  inPersonSessionsAvailable: { type: Boolean, default: true },
  location: {
    city: String,
    state: String,
    country: String,
    coordinates: {
      lat: Number,
      lng: Number
    }
  },
  ageGroupsServed: [String], // e.g. ["5-8", "9-12", "13-17"]
  hourlyRate: Number,
  verified: { type: Boolean, default: false },
  rating: { type: Number, default: 0 },
  reviewCount: { type: Number, default: 0 },
  createdAt: { type: Date, default: Date.now }
});

// Create models
const User = mongoose.model('User', userSchema);
const Video = mongoose.model('Video', videoSchema);
const Trainer = mongoose.model('Trainer', trainerSchema);

// Routes

// User registration
app.post('/api/users/register', async (req, res) => {
  try {
    const { username, email, password, age, parentEmail } = req.body;
    
    // Basic validation
    if (!username || !email || !password || !age || !parentEmail) {
      return res.status(400).json({ message: 'All fields are required' });
    }
    
    // Check if user already exists
    const existingUser = await User.findOne({ $or: [{ email }, { username }] });
    if (existingUser) {
      return res.status(400).json({ message: 'Username or email already in use' });
    }
    
    // Create new user (in production, hash the password)
    const user = new User({
      username,
      email,
      password, // Should be hashed in production
      age,
      parentEmail
    });
    
    await user.save();
    
    // Send parent verification email (would implement in production)
    
    res.status(201).json({ 
      message: 'User registered successfully. Parent verification email sent.',
      userId: user._id
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ message: 'Server error during registration' });
  }
});

// Video upload
app.post('/api/videos/upload', upload.single('video'), async (req, res) => {
  try {
    const { title, description, sport, minAge, maxAge, skillLevel, videoType } = req.body;
    const userId = req.body.userId; // In production, get from auth token
    
    // Basic validation
    if (!title || !sport || !minAge || !maxAge || !skillLevel || !videoType) {
      return res.status(400).json({ message: 'Missing required fields' });
    }
    
    // Check if user exists
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    // Upload to S3
    const fileKey = `videos/${uuidv4()}-${req.file.originalname}`;
    const uploadParams = {
      Bucket: 'lil-playbook-videos', // Would come from config
      Key: fileKey,
      Body: req.file.buffer,
      ContentType: req.file.mimetype
    };
    
    await s3.upload(uploadParams).promise();
    
    // Create video record
    const video = new Video({
      title,
      description,
      s3Key: fileKey,
      uploadedBy: userId,
      sport,
      ageRange: {
        min: parseInt(minAge),
        max: parseInt(maxAge)
      },
      skillLevel,
      isDrill: videoType === 'drill',
      isProHighlight: videoType === 'pro',
      isUserHighlight: videoType === 'user',
      // For user uploads, require approval
      approved: videoType === 'user' ? false : true,
      tags: req.body.tags ? req.body.tags.split(',') : []
    });
    
    await video.save();
    
    res.status(201).json({
      message: 'Video uploaded successfully',
      videoId: video._id,
      approved: video.approved
    });
  } catch (error) {
    console.error('Video upload error:', error);
    res.status(500).json({ message: 'Server error during video upload' });
  }
});

// Get videos by age and sport
app.get('/api/videos', async (req, res) => {
  try {
    const { age, sport, type, skillLevel, limit = 20, page = 1 } = req.query;
    
    const query = { approved: true };
    
    // Filter by age if provided
    if (age) {
      query['ageRange.min'] = { $lte: parseInt(age) };
      query['ageRange.max'] = { $gte: parseInt(age) };
    }
    
    // Filter by sport if provided
    if (sport) {
      query.sport = sport;
    }
    
    // Filter by video type if provided
    if (type === 'drill') {
      query.isDrill = true;
    } else if (type === 'pro') {
      query.isProHighlight = true;
    } else if (type === 'user') {
      query.isUserHighlight = true;
    }
    
    // Filter by skill level if provided
    if (skillLevel) {
      query.skillLevel = skillLevel;
    }
    
    const skip = (parseInt(page) - 1) * parseInt(limit);
    
    const videos = await Video.find(query)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(parseInt(limit))
      .populate('uploadedBy', 'username');
    
    const total = await Video.countDocuments(query);
    
    res.json({
      videos,
      total,
      pages: Math.ceil(total / parseInt(limit)),
      currentPage: parseInt(page)
    });
  } catch (error) {
    console.error('Error fetching videos:', error);
    res.status(500).json({ message: 'Server error while fetching videos' });
  }
});

// Find trainers
app.get('/api/trainers', async (req, res) => {
  try {
    const { sport, virtual, inPerson, minAge, maxAge, location, radius } = req.query;
    
    const query = { verified: true };
    
    // Filter by sport if provided
    if (sport) {
      query.sports = sport;
    }
    
    // Filter by session type if provided
    if (virtual === 'true') {
      query.virtualSessionsAvailable = true;
    }
    
    if (inPerson === 'true') {
      query.inPersonSessionsAvailable = true;
    }
    
    // Filter by age group if provided
    if (minAge && maxAge) {
      // This is a simplified approach - in production would need more complex age range matching
      query.ageGroupsServed = { $in: [`${minAge}-${maxAge}`] };
    }
    
    // Location filtering would be implemented with geospatial queries in production
    
    const trainers = await Trainer.find(query).sort({ rating: -1 });
    
    res.json({ trainers });
  } catch (error) {
    console.error('Error finding trainers:', error);
    res.status(500).json({ message: 'Server error while finding trainers' });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`Lil Playbook server running on port ${PORT}`);
});
