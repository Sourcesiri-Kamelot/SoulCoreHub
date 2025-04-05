// server.js (Conceptual Node.js Backend)
const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs'); // For file system operations

const app = express();
const port = 3000;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static('public')); // Serve static files (HTML, CSS, JS)

// Data Storage (Example: JSON file)
const dataFilePath = 'data.json';
let data = {};

try {
  const fileData = fs.readFileSync(dataFilePath, 'utf8');
  data = JSON.parse(fileData);
} catch (err) {
  // File doesn't exist or is invalid JSON
  console.log('Data file not found or invalid, creating new data.');
  data = { ideas: [], projects: [], repos: [], subscriptions: [] };
  fs.writeFileSync(dataFilePath, JSON.stringify(data, null, 2));
}

// Function to save data
function saveData() {
  fs.writeFileSync(dataFilePath, JSON.stringify(data, null, 2));
}

// API Endpoints
app.post('/save', (req, res) => {
  const { type, payload } = req.body;
  if (data[type]) {
    if (type === 'project'){
      data[type].push(payload);
    } else if (type === 'subscription'){
      data[type].push(payload);
    } else {
      data[type].push(payload);
    }

    saveData();
    res.json({ success: true, message: `${type} saved successfully.` });
  } else {
    res.status(400).json({ success: false, message: 'Invalid data type.' });
  }
});

app.get('/run', (req, res) => {
  const command = req.query.cmd;
  // In a real application, you'd execute commands here.
  console.log(`Executing command: ${command}`);
  // Simulate execution (for now):
  res.send(`Command executed: ${command}`);
});

app.get('/run_dialogue', (req, res) => {
  const message = req.query.msg;
  // In a real application, you'd process the dialogue here.
  console.log(`Dialogue message received: ${message}`);
  // Simulate response:
  res.send(`SoulCore responded: ${message} (simulation)`);
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
