import React, { useState, useEffect } from 'react';

const AdminConsole = ({ agents, setAgents }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [systemStatus, setSystemStatus] = useState({
    cpuUsage: 0,
    memoryUsage: 0,
    activeConnections: 0,
    uptime: 0,
    lastRestart: new Date(),
    agentStatus: {}
  });
  const [logs, setLogs] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [agentConfig, setAgentConfig] = useState({});
  const [isEditing, setIsEditing] = useState(false);
  const [newAgentData, setNewAgentData] = useState({
    id: '',
    name: '',
    personality: '',
    status: 'developing',
    avatar: ''
  });
  
  // Simulate system status updates
  useEffect(() => {
    const updateSystemStatus = () => {
      setSystemStatus(prev => {
        const agentStatus = {};
        agents.forEach(agent => {
          agentStatus[agent.id] = {
            active: agent.status === 'online',
            responseTime: Math.floor(Math.random() * 200) + 50, // 50-250ms
            memoryUsage: Math.floor(Math.random() * 200) + 100, // 100-300MB
            errorRate: Math.random() * 0.5, // 0-0.5%
            connections: Math.floor(Math.random() * 10) + 1 // 1-10 connections
          };
        });
        
        return {
          cpuUsage: Math.min(100, prev.cpuUsage + (Math.random() * 10 - 5)),
          memoryUsage: Math.min(100, prev.memoryUsage + (Math.random() * 8 - 4)),
          activeConnections: Math.max(1, Math.floor(prev.activeConnections + (Math.random() * 3 - 1))),
          uptime: prev.uptime + 1,
          lastRestart: prev.lastRestart,
          agentStatus
        };
      });
    };
    
    const interval = setInterval(updateSystemStatus, 2000);
    return () => clearInterval(interval);
  }, [agents]);
  
  // Simulate log entries
  useEffect(() => {
    const logTypes = ['INFO', 'WARNING', 'ERROR', 'DEBUG'];
    const logSources = ['SYSTEM', 'ANIMA', 'GPTSOUL', 'AZUR', 'EVOVE', 'NETWORK', 'MEMORY'];
    const logMessages = [
      'Agent communication established',
      'Memory synchronization complete',
      'Processing user request',
      'Emotional state updated',
      'Strategic analysis complete',
      'Self-repair routine initiated',
      'Connection attempt from unauthorized IP',
      'Resource allocation optimized',
      'Agent registry updated',
      'Backup completed successfully'
    ];
    
    const generateLog = () => {
      const type = logTypes[Math.floor(Math.random() * logTypes.length)];
      const source = logSources[Math.floor(Math.random() * logSources.length)];
      const message = logMessages[Math.floor(Math.random() * logMessages.length)];
      
      return {
        timestamp: new Date(),
        type,
        source,
        message
      };
    };
    
    const addLog = () => {
      setLogs(prev => [generateLog(), ...prev].slice(0, 100)); // Keep last 100 logs
    };
    
    // Initial logs
    setLogs([
      {
        timestamp: new Date(),
        type: 'INFO',
        source: 'SYSTEM',
        message: 'Admin console initialized'
      },
      {
        timestamp: new Date(Date.now() - 5000),
        type: 'INFO',
        source: 'SYSTEM',
        message: 'All agents reporting normal status'
      }
    ]);
    
    const interval = setInterval(addLog, 3000);
    return () => clearInterval(interval);
  }, []);
  
  // Handle agent selection for configuration
  const handleAgentSelect = (agent) => {
    setSelectedAgent(agent);
    setAgentConfig({
      name: agent.name,
      personality: agent.personality,
      status: agent.status,
      avatar: agent.avatar || ''
    });
    setIsEditing(false);
  };
  
  // Update agent configuration
  const handleAgentUpdate = () => {
    if (!selectedAgent) return;
    
    setAgents(prev => prev.map(agent => 
      agent.id === selectedAgent.id 
        ? { ...agent, ...agentConfig }
        : agent
    ));
    
    setLogs(prev => [{
      timestamp: new Date(),
      type: 'INFO',
      source: 'ADMIN',
      message: `Agent ${selectedAgent.name} configuration updated`
    }, ...prev]);
    
    setIsEditing(false);
  };
  
  // Create new agent
  const handleCreateAgent = () => {
    if (!newAgentData.id || !newAgentData.name) {
      setLogs(prev => [{
        timestamp: new Date(),
        type: 'ERROR',
        source: 'ADMIN',
        message: 'Agent ID and name are required'
      }, ...prev]);
      return;
    }
    
    // Check for duplicate ID
    if (agents.some(agent => agent.id === newAgentData.id)) {
      setLogs(prev => [{
        timestamp: new Date(),
        type: 'ERROR',
        source: 'ADMIN',
        message: 'Agent ID already exists'
      }, ...prev]);
      return;
    }
    
    setAgents(prev => [...prev, { ...newAgentData }]);
    
    setLogs(prev => [{
      timestamp: new Date(),
      type: 'INFO',
      source: 'ADMIN',
      message: `New agent ${newAgentData.name} created`
    }, ...prev]);
    
    // Reset form
    setNewAgentData({
      id: '',
      name: '',
      personality: '',
      status: 'developing',
      avatar: ''
    });
  };
  
  // Restart system simulation
  const handleSystemRestart = () => {
    setLogs(prev => [{
      timestamp: new Date(),
      type: 'WARNING',
      source: 'ADMIN',
      message: 'System restart initiated'
    }, ...prev]);
    
    setTimeout(() => {
      setSystemStatus(prev => ({
        ...prev,
        cpuUsage: 15,
        memoryUsage: 30,
        lastRestart: new Date()
      }));
      
      setLogs(prev => [{
        timestamp: new Date(),
        type: 'INFO',
        source: 'SYSTEM',
        message: 'System restart completed successfully'
      }, ...prev]);
    }, 3000);
  };
  
  return (
    <div className="admin-console">
      <h2>SoulCore Admin Console</h2>
      
      <div className="admin-tabs">
        <button 
          className={`admin-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={`admin-tab ${activeTab === 'agents' ? 'active' : ''}`}
          onClick={() => setActiveTab('agents')}
        >
          Agent Management
        </button>
        <button 
          className={`admin-tab ${activeTab === 'logs' ? 'active' : ''}`}
          onClick={() => setActiveTab('logs')}
        >
          System Logs
        </button>
        <button 
          className={`admin-tab ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          Settings
        </button>
      </div>
      
      <div className="admin-content">
        {activeTab === 'dashboard' && (
          <div className="admin-dashboard">
            <div className="system-overview">
              <h3>System Overview</h3>
              
              <div className="system-stats">
                <div className="stat-card">
                  <div className="stat-title">CPU Usage</div>
                  <div className="stat-value">{Math.floor(systemStatus.cpuUsage)}%</div>
                  <div className="stat-bar">
                    <div 
                      className={`stat-progress ${systemStatus.cpuUsage > 80 ? 'critical' : systemStatus.cpuUsage > 60 ? 'warning' : ''}`}
                      style={{ width: `${systemStatus.cpuUsage}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="stat-card">
                  <div className="stat-title">Memory Usage</div>
                  <div className="stat-value">{Math.floor(systemStatus.memoryUsage)}%</div>
                  <div className="stat-bar">
                    <div 
                      className={`stat-progress ${systemStatus.memoryUsage > 80 ? 'critical' : systemStatus.memoryUsage > 60 ? 'warning' : ''}`}
                      style={{ width: `${systemStatus.memoryUsage}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="stat-card">
                  <div className="stat-title">Active Connections</div>
                  <div className="stat-value">{systemStatus.activeConnections}</div>
                </div>
                
                <div className="stat-card">
                  <div className="stat-title">Uptime</div>
                  <div className="stat-value">
                    {Math.floor(systemStatus.uptime / 3600)}h {Math.floor((systemStatus.uptime % 3600) / 60)}m
                  </div>
                </div>
              </div>
              
              <div className="system-actions">
                <button onClick={handleSystemRestart} className="system-action warning">
                  Restart System
                </button>
                <button className="system-action">
                  Backup Memory
                </button>
                <button className="system-action">
                  Run Diagnostics
                </button>
              </div>
            </div>
            
            <div className="agent-overview">
              <h3>Agent Status</h3>
              
              <div className="agent-status-list">
                {agents.map(agent => {
                  const status = systemStatus.agentStatus[agent.id] || {};
                  return (
                    <div key={agent.id} className="agent-status-card">
                      <div className="agent-status-header">
                        <div className="agent-avatar-small" style={{ backgroundImage: `url(${agent.avatar || '/assets/default-agent.png'})` }}></div>
                        <div className="agent-status-name">{agent.name}</div>
                        <div className={`agent-status-indicator ${agent.status}`}></div>
                      </div>
                      
                      <div className="agent-status-stats">
                        <div className="agent-stat">
                          <span className="agent-stat-label">Response Time</span>
                          <span className="agent-stat-value">{status.responseTime || 0}ms</span>
                        </div>
                        <div className="agent-stat">
                          <span className="agent-stat-label">Memory</span>
                          <span className="agent-stat-value">{status.memoryUsage || 0}MB</span>
                        </div>
                        <div className="agent-stat">
                          <span className="agent-stat-label">Error Rate</span>
                          <span className="agent-stat-value">{(status.errorRate || 0).toFixed(2)}%</span>
                        </div>
                        <div className="agent-stat">
                          <span className="agent-stat-label">Connections</span>
                          <span className="agent-stat-value">{status.connections || 0}</span>
                        </div>
                      </div>
                      
                      <div className="agent-status-actions">
                        <button className="agent-action">Restart</button>
                        <button className="agent-action" onClick={() => handleAgentSelect(agent)}>Configure</button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'agents' && (
          <div className="agent-management">
            <div className="agent-list-panel">
              <h3>Manage Agents</h3>
              
              <div className="agent-list">
                {agents.map(agent => (
                  <div 
                    key={agent.id} 
                    className={`agent-list-item ${selectedAgent?.id === agent.id ? 'selected' : ''}`}
                    onClick={() => handleAgentSelect(agent)}
                  >
                    <div className="agent-avatar-small" style={{ backgroundImage: `url(${agent.avatar || '/assets/default-agent.png'})` }}></div>
                    <div className="agent-list-info">
                      <div className="agent-list-name">{agent.name}</div>
                      <div className="agent-list-role">{agent.personality}</div>
                    </div>
                    <div className={`agent-list-status ${agent.status}`}></div>
                  </div>
                ))}
              </div>
              
              <h3>Create New Agent</h3>
              <div className="new-agent-form">
                <div className="form-group">
                  <label>Agent ID</label>
                  <input 
                    type="text" 
                    value={newAgentData.id}
                    onChange={e => setNewAgentData({...newAgentData, id: e.target.value})}
                    placeholder="unique-id"
                  />
                </div>
                
                <div className="form-group">
                  <label>Name</label>
                  <input 
                    type="text" 
                    value={newAgentData.name}
                    onChange={e => setNewAgentData({...newAgentData, name: e.target.value})}
                    placeholder="Agent Name"
                  />
                </div>
                
                <div className="form-group">
                  <label>Role/Personality</label>
                  <input 
                    type="text" 
                    value={newAgentData.personality}
                    onChange={e => setNewAgentData({...newAgentData, personality: e.target.value})}
                    placeholder="Agent Role"
                  />
                </div>
                
                <div className="form-group">
                  <label>Status</label>
                  <select
                    value={newAgentData.status}
                    onChange={e => setNewAgentData({...newAgentData, status: e.target.value})}
                  >
                    <option value="developing">Developing</option>
                    <option value="online">Online</option>
                    <option value="offline">Offline</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Avatar URL</label>
                  <input 
                    type="text" 
                    value={newAgentData.avatar}
                    onChange={e => setNewAgentData({...newAgentData, avatar: e.target.value})}
                    placeholder="https://example.com/avatar.png"
                  />
                </div>
                
                <button onClick={handleCreateAgent} className="create-agent-button">
                  Create Agent
                </button>
              </div>
            </div>
            
            {selectedAgent && (
              <div className="agent-config-panel">
                <h3>
                  {isEditing ? 'Edit Agent Configuration' : 'Agent Configuration'}
                  <button 
                    onClick={() => setIsEditing(!isEditing)}
                    className="edit-toggle"
                  >
                    {isEditing ? 'Cancel' : 'Edit'}
                  </button>
                </h3>
                
                <div className="agent-config-header">
                  <div className="agent-avatar-large" style={{ backgroundImage: `url(${selectedAgent.avatar || '/assets/default-agent.png'})` }}></div>
                  <div className="agent-config-id">ID: {selectedAgent.id}</div>
                </div>
                
                <div className="agent-config-form">
                  <div className="form-group">
                    <label>Name</label>
                    {isEditing ? (
                      <input 
                        type="text" 
                        value={agentConfig.name}
                        onChange={e => setAgentConfig({...agentConfig, name: e.target.value})}
                      />
                    ) : (
                      <div className="config-value">{agentConfig.name}</div>
                    )}
                  </div>
                  
                  <div className="form-group">
                    <label>Role/Personality</label>
                    {isEditing ? (
                      <input 
                        type="text" 
                        value={agentConfig.personality}
                        onChange={e => setAgentConfig({...agentConfig, personality: e.target.value})}
                      />
                    ) : (
                      <div className="config-value">{agentConfig.personality}</div>
                    )}
                  </div>
                  
                  <div className="form-group">
                    <label>Status</label>
                    {isEditing ? (
                      <select
                        value={agentConfig.status}
                        onChange={e => setAgentConfig({...agentConfig, status: e.target.value})}
                      >
                        <option value="developing">Developing</option>
                        <option value="online">Online</option>
                        <option value="offline">Offline</option>
                      </select>
                    ) : (
                      <div className="config-value">
                        <span className={`status-indicator ${agentConfig.status}`}>{agentConfig.status}</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="form-group">
                    <label>Avatar URL</label>
                    {isEditing ? (
                      <input 
                        type="text" 
                        value={agentConfig.avatar}
                        onChange={e => setAgentConfig({...agentConfig, avatar: e.target.value})}
                      />
                    ) : (
                      <div className="config-value">{agentConfig.avatar || 'Default Avatar'}</div>
                    )}
                  </div>
                  
                  {isEditing && (
                    <div className="form-actions">
                      <button onClick={handleAgentUpdate} className="update-button">
                        Update Agent
                      </button>
                    </div>
                  )}
                </div>
                
                <div className="agent-advanced-options">
                  <h4>Advanced Options</h4>
                  
                  <div className="advanced-buttons">
                    <button className="advanced-button">View Memory</button>
                    <button className="advanced-button">Reset Agent</button>
                    <button className="advanced-button warning">Delete Agent</button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        
        {activeTab === 'logs' && (
          <div className="system-logs">
            <h3>System Logs</h3>
            
            <div className="log-filters">
              <select defaultValue="all">
                <option value="all">All Types</option>
                <option value="INFO">Info</option>
                <option value="WARNING">Warning</option>
                <option value="ERROR">Error</option>
                <option value="DEBUG">Debug</option>
              </select>
              
              <select defaultValue="all">
                <option value="all">All Sources</option>
                <option value="SYSTEM">System</option>
                <option value="ANIMA">Anima</option>
                <option value="GPTSOUL">GPTSoul</option>
                <option value="AZUR">Azür</option>
                <option value="EVOVE">EvoVe</option>
                <option value="ADMIN">Admin</option>
              </select>
              
              <button className="refresh-logs">Refresh</button>
              <button className="clear-logs">Clear</button>
            </div>
            
            <div className="log-table-container">
              <table className="log-table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Type</th>
                    <th>Source</th>
                    <th>Message</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log, idx) => (
                    <tr key={idx} className={`log-entry ${log.type.toLowerCase()}`}>
                      <td>{log.timestamp.toLocaleTimeString()}</td>
                      <td>{log.type}</td>
                      <td>{log.source}</td>
                      <td>{log.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
        
        {activeTab === 'settings' && (
          <div className="system-settings">
            <h3>System Settings</h3>
            
            <div className="settings-section">
              <h4>General Settings</h4>
              
              <div className="setting-item">
                <label>System Name</label>
                <input type="text" defaultValue="SoulCore Hub" />
              </div>
              
              <div className="setting-item">
                <label>Admin Email</label>
                <input type="email" defaultValue="admin@soulcorehub.ai" />
              </div>
              
              <div className="setting-item">
                <label>Auto-Backup Frequency</label>
                <select defaultValue="daily">
                  <option value="hourly">Hourly</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </select>
              </div>
              
              <div className="setting-item checkbox">
                <input type="checkbox" id="debug-mode" defaultChecked />
                <label htmlFor="debug-mode">Enable Debug Mode</label>
              </div>
              
              <div className="setting-item checkbox">
                <input type="checkbox" id="auto-restart" defaultChecked />
                <label htmlFor="auto-restart">Auto-restart on critical error</label>
              </div>
            </div>
            
            <div className="settings-section">
              <h4>Security Settings</h4>
              
              <div className="setting-item">
                <label>Session Timeout (minutes)</label>
                <input type="number" defaultValue="30" />
              </div>
              
              <div className="setting-item checkbox">
                <input type="checkbox" id="two-factor" />
                <label htmlFor="two-factor">Enable Two-Factor Authentication</label>
              </div>
              
              <div className="setting-item checkbox">
                <input type="checkbox" id="ip-restrict" defaultChecked />
                <label htmlFor="ip-restrict">Restrict Admin Access by IP</label>
              </div>
            </div>
            
            <div className="settings-section">
              <h4>Integration Settings</h4>
              
              <div className="setting-item">
                <label>API Key</label>
                <div className="api-key-field">
                  <input type="password" defaultValue="sk_live_SoulCoreHub123456789" />
                  <button>Show</button>
                  <button>Regenerate</button>
                </div>
              </div>
              
              <div className="setting-item checkbox">
                <input type="checkbox" id="market-whisper" defaultChecked />
                <label htmlFor="market-whisper">Enable Market Whisperer Integration</label>
              </div>
              
              <div className="setting-item checkbox">
                <input type="checkbox" id="paulterpan" defaultChecked />
                <label htmlFor="paulterpan">Enable PaulterPan Trading Integration</label>
              </div>
              
              <div className="setting-item checkbox">
                <input type="checkbox" id="ai-clothing" />
                <label htmlFor="ai-clothing">Enable AI Clothing Integration</label>
              </div>
            </div>
            
            <div className="settings-actions">
              <button className="save-settings">Save Settings</button>
              <button className="reset-settings">Reset to Defaults</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminConsole;
