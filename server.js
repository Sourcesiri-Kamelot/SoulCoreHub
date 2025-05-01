// 🔥 SoulCoreHub Backend (server.js)

const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const { exec } = require('child_process');

const app = express();
const port = 3000;

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static('public'));

// File Path
const dataFilePath = 'data.json';

// Default Structure
let data = {
  ideas: [],
  projects: [],
  repos: [],
  subscriptions: [],
  resonance: {},
  predictions: {}
};

// 📥 Load Data
function loadData() {
  try {
    if (fs.existsSync(dataFilePath)) {
      const raw = fs.readFileSync(dataFilePath, 'utf8');
      data = JSON.parse(raw);
      console.log('✅ Data loaded.');
    } else {
      saveData();
    }
  } catch (error) {
    console.error('❌ Error loading data:', error);
  }
}

// 💾 Save Data
function saveData() {
  try {
    fs.writeFileSync(dataFilePath, JSON.stringify(data, null, 2));
  } catch (error) {
    console.error('❌ Save error:', error);
  }
}

// 🧠 Save Prediction
function savePredictionData(payload) {
  const { dataPoint, prediction, confidence } = payload;
  if (!dataPoint || !prediction || confidence === undefined) {
    throw new Error('Missing required prediction fields.');
  }

  if (!data.predictions[dataPoint]) {
    data.predictions[dataPoint] = [];
  }

  data.predictions[dataPoint].push({
    prediction,
    confidence,
    timestamp: new Date().toISOString()
  });
}

// 🌀 Save Resonance
function saveResonanceData(payload) {
  const { emotion, dataPoint, value } = payload;
  if (!emotion || !dataPoint || value === undefined) {
    throw new Error('Missing required resonance fields.');
  }

  if (!data.resonance[emotion]) {
    data.resonance[emotion] = [];
  }

  data.resonance[emotion].push({
    dataPoint,
    value,
    timestamp: new Date().toISOString()
  });
}

// 🧩 ROUTE: Save prediction or resonance data
app.post('/save', (req, res) => {
  const { type, payload } = req.body;

  try {
    if (type === 'prediction') {
      savePredictionData(payload);
    } else if (type === 'resonance') {
      saveResonanceData(payload);
    } else {
      return res.status(400).json({ success: false, message: 'Invalid data type.' });
    }

    saveData();
    res.json({ success: true, message: `${type} data saved successfully.` });
  } catch (error) {
    console.error('❌ Save Error:', error);
    res.status(500).json({ success: false, message: error.message });
  }
});

// 🎤 ROUTE: Speak emotion out loud
app.post('/speak_emotion', (req, res) => {
  const { emotion, message } = req.body;

  if (!emotion || !message) {
    return res.status(400).json({ success: false, message: 'Emotion and message required.' });
  }

  console.log(`🔊 Speaking: "${message}" with emotion: ${emotion}`);

  const cmd = `python3 anima_voice.py "${emotion}" "${message}"`;

  exec(cmd, (error, stdout, stderr) => {
    if (error) {
      console.error('❌ Voice error:', stderr);
      return res.status(500).json({ success: false, message: 'Voice synthesis failed.' });
    }
    res.json({ success: true, message: 'Speaking complete.', output: stdout });
  });
});

// 🧬 ROUTE: System Status
app.get('/status', (req, res) => {
  res.json({
    status: '💠 SoulCoreHub online.',
    memory: Object.keys(data),
    timestamp: new Date().toISOString()
  });
});

// 🔁 INIT
loadData();
app.listen(port, () => {
  console.log(`🚀 SoulCoreHub server running at http://localhost:${port}`);
});
