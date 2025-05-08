
import React, { useState } from 'react';
import './App.css';

function App() {
  const [memoryLog, setMemoryLog] = useState([
    'Anima initialized...',
    'Memory engine stable.',
    'Awaiting commands...'
  ]);

  const agents = ['GPTSoul', 'Anima', 'EvoVe', 'Azür'];

  const handleCommand = (command) => {
    const timestamp = new Date().toLocaleTimeString();
    setMemoryLog(prev => [`[${timestamp}] Executed: ${command}`, ...prev]);
  };

  return (
    <div className="App" style={{ padding: '2rem', fontFamily: 'monospace', backgroundColor: '#0d1117', color: '#f0f6fc' }}>
      <h1>🧠 Anima Control Dashboard</h1>

      <section style={{ marginBottom: '2rem' }}>
        <h2>⚙️ Quick Actions</h2>
        <button onClick={() => handleCommand('Run diagnostics')}>Run Diagnostics</button>
        <button onClick={() => handleCommand('Sync with GPTSoul')}>Sync with GPTSoul</button>
        <button onClick={() => handleCommand('Upload memory logs')}>Upload Memory Logs</button>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2>🧬 Active Agents</h2>
        <ul>
          {agents.map(agent => (
            <li key={agent}>{agent} — <button onClick={() => handleCommand(`Ping ${agent}`)}>Ping</button></li>
          ))}
        </ul>
      </section>

      <section>
        <h2>🪵 Memory Log</h2>
        <div style={{ backgroundColor: '#161b22', padding: '1rem', borderRadius: '6px', maxHeight: '200px', overflowY: 'auto' }}>
          {memoryLog.map((entry, index) => (
            <div key={index}>📄 {entry}</div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default App;
