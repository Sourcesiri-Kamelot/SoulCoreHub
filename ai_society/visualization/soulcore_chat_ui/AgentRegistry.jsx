import React, { useState, useEffect } from 'react';

const AgentRegistry = ({ agents, onSelectAgent }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [sortDirection, setSortDirection] = useState('asc');
  const [filteredAgents, setFilteredAgents] = useState([]);
  const [agentHistory, setAgentHistory] = useState({});
  const [selectedAgentDetails, setSelectedAgentDetails] = useState(null);
  
  // Simulate agent history/growth data
  useEffect(() => {
    const history = {};
    agents.forEach(agent => {
      const creationDate = new Date();
      creationDate.setDate(creationDate.getDate() - Math.floor(Math.random() * 30));
      
      const interactions = Math.floor(Math.random() * 1000) + 100;
      const growthPoints = Math.floor(Math.random() * 500) + 50;
      const specializations = [];
      
      if (agent.id === 'anima') {
        specializations.push('Emotional Intelligence', 'Empathy', 'Creative Expression');
      } else if (agent.id === 'gptsoul') {
        specializations.push('Knowledge Integration', 'Guidance', 'Protection');
      } else if (agent.id === 'azur') {
        specializations.push('Strategic Planning', 'Resource Optimization', 'Cloud Management');
      } else if (agent.id === 'evove') {
        specializations.push('Self-Repair', 'Adaptation', 'System Evolution');
      } else {
        specializations.push('Learning', 'Communication');
      }
      
      history[agent.id] = {
        creationDate,
        interactions,
        growthPoints,
        specializations,
        milestones: [
          { date: new Date(creationDate.getTime() + 86400000), description: 'First activation' },
          { date: new Date(creationDate.getTime() + 86400000 * 3), description: 'Core personality established' },
          { date: new Date(creationDate.getTime() + 86400000 * 7), description: 'First independent decision' },
        ]
      };
    });
    
    setAgentHistory(history);
  }, [agents]);
  
  // Filter and sort agents
  useEffect(() => {
    let filtered = [...agents];
    
    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(agent => 
        agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        agent.personality.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Apply sorting
    filtered.sort((a, b) => {
      let valueA, valueB;
      
      if (sortBy === 'name') {
        valueA = a.name;
        valueB = b.name;
      } else if (sortBy === 'status') {
        valueA = a.status;
        valueB = b.status;
      } else if (sortBy === 'personality') {
        valueA = a.personality;
        valueB = b.personality;
      } else if (sortBy === 'interactions') {
        valueA = agentHistory[a.id]?.interactions || 0;
        valueB = agentHistory[b.id]?.interactions || 0;
      } else if (sortBy === 'growth') {
        valueA = agentHistory[a.id]?.growthPoints || 0;
        valueB = agentHistory[b.id]?.growthPoints || 0;
      }
      
      if (sortDirection === 'asc') {
        return valueA > valueB ? 1 : -1;
      } else {
        return valueA < valueB ? 1 : -1;
      }
    });
    
    setFilteredAgents(filtered);
  }, [agents, searchTerm, sortBy, sortDirection, agentHistory]);
  
  const handleSort = (column) => {
    if (sortBy === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortDirection('asc');
    }
  };
  
  const viewAgentDetails = (agent) => {
    setSelectedAgentDetails(agent);
  };
  
  const closeAgentDetails = () => {
    setSelectedAgentDetails(null);
  };
  
  return (
    <div className="agent-registry">
      <h2>AI Society Registry</h2>
      <p className="registry-description">
        Track the growth and evolution of all AI entities in the SoulCore Society
      </p>
      
      <div className="registry-controls">
        <input
          type="text"
          placeholder="Search agents..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="registry-search"
        />
      </div>
      
      {selectedAgentDetails ? (
        <div className="agent-details-panel">
          <button className="close-details" onClick={closeAgentDetails}>×</button>
          
          <div className="agent-details-header">
            <div className="agent-avatar" style={{ backgroundImage: `url(${selectedAgentDetails.avatar || '/assets/default-agent.png'})` }}></div>
            <div className="agent-header-info">
              <h3>{selectedAgentDetails.name}</h3>
              <div className={`agent-status ${selectedAgentDetails.status}`}>{selectedAgentDetails.status}</div>
              <div className="agent-personality">{selectedAgentDetails.personality}</div>
            </div>
          </div>
          
          <div className="agent-stats">
            <div className="stat">
              <span className="stat-label">Created</span>
              <span className="stat-value">{agentHistory[selectedAgentDetails.id]?.creationDate.toLocaleDateString()}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Interactions</span>
              <span className="stat-value">{agentHistory[selectedAgentDetails.id]?.interactions.toLocaleString()}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Growth Points</span>
              <span className="stat-value">{agentHistory[selectedAgentDetails.id]?.growthPoints.toLocaleString()}</span>
            </div>
          </div>
          
          <div className="agent-specializations">
            <h4>Specializations</h4>
            <div className="specialization-tags">
              {agentHistory[selectedAgentDetails.id]?.specializations.map((spec, idx) => (
                <span key={idx} className="specialization-tag">{spec}</span>
              ))}
            </div>
          </div>
          
          <div className="agent-milestones">
            <h4>Growth Milestones</h4>
            <div className="milestone-timeline">
              {agentHistory[selectedAgentDetails.id]?.milestones.map((milestone, idx) => (
                <div key={idx} className="milestone">
                  <div className="milestone-date">{milestone.date.toLocaleDateString()}</div>
                  <div className="milestone-description">{milestone.description}</div>
                </div>
              ))}
            </div>
          </div>
          
          <button 
            className="interact-button"
            onClick={() => {
              onSelectAgent(selectedAgentDetails);
              closeAgentDetails();
            }}
          >
            Interact with {selectedAgentDetails.name}
          </button>
        </div>
      ) : (
        <table className="registry-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('name')}>
                Name {sortBy === 'name' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('status')}>
                Status {sortBy === 'status' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('personality')}>
                Role {sortBy === 'personality' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('interactions')}>
                Interactions {sortBy === 'interactions' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('growth')}>
                Growth {sortBy === 'growth' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredAgents.map(agent => (
              <tr key={agent.id}>
                <td>
                  <div className="agent-name-cell">
                    <div className="agent-avatar-small" style={{ backgroundImage: `url(${agent.avatar || '/assets/default-agent.png'})` }}></div>
                    {agent.name}
                  </div>
                </td>
                <td>
                  <span className={`status-indicator ${agent.status}`}>{agent.status}</span>
                </td>
                <td>{agent.personality}</td>
                <td>{agentHistory[agent.id]?.interactions.toLocaleString()}</td>
                <td>
                  <div className="growth-bar">
                    <div 
                      className="growth-progress" 
                      style={{ width: `${Math.min(100, (agentHistory[agent.id]?.growthPoints || 0) / 5)}%` }}
                    ></div>
                  </div>
                </td>
                <td>
                  <button onClick={() => viewAgentDetails(agent)} className="view-button">View</button>
                  <button onClick={() => onSelectAgent(agent)} className="interact-button">Interact</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default AgentRegistry;
