import React, { useState } from 'react';
import { useUserPlanContext } from '../../context/UserPlanContext';
import './TradingSignals.css';

export function TradingSignals() {
  const { userPlan } = useUserPlanContext();
  const isTraderPro = userPlan === 'trader-pro';
  
  const [activeTab, setActiveTab] = useState('stocks');
  const [timeFrame, setTimeFrame] = useState('daily');
  const [riskLevel, setRiskLevel] = useState('all');
  
  return (
    <div className="trading-signals">
      <header className="signals-header">
        <h1>Trading Signals</h1>
        <div className="signals-meta">
          <div className="signals-count">
            <span className="count">{isTraderPro ? 50 : 10}</span>
            <span className="label">Available Signals</span>
          </div>
          <div className="signals-refresh">
            <span className="refresh-label">Last updated:</span>
            <span className="refresh-time">10 minutes ago</span>
            <button className="refresh-button">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2" />
              </svg>
            </button>
          </div>
        </div>
      </header>
      
      <div className="signals-tabs">
        <button 
          className={`tab-button ${activeTab === 'stocks' ? 'active' : ''}`}
          onClick={() => setActiveTab('stocks')}
        >
          Stocks
        </button>
        <button 
          className={`tab-button ${activeTab === 'crypto' ? 'active' : ''}`}
          onClick={() => setActiveTab('crypto')}
        >
          Crypto
        </button>
        <button 
          className={`tab-button ${activeTab === 'forex' ? 'active' : ''}`}
          onClick={() => setActiveTab('forex')}
        >
          Forex
        </button>
        {isTraderPro && (
          <button 
            className={`tab-button ${activeTab === 'options' ? 'active' : ''}`}
            onClick={() => setActiveTab('options')}
          >
            Options
          </button>
        )}
      </div>
      
      <div className="signals-filters">
        <div className="filter-group">
          <label>Time Frame:</label>
          <div className="button-group">
            <button 
              className={timeFrame === 'intraday' ? 'active' : ''}
              onClick={() => setTimeFrame('intraday')}
            >
              Intraday
            </button>
            <button 
              className={timeFrame === 'daily' ? 'active' : ''}
              onClick={() => setTimeFrame('daily')}
            >
              Daily
            </button>
            <button 
              className={timeFrame === 'weekly' ? 'active' : ''}
              onClick={() => setTimeFrame('weekly')}
            >
              Weekly
            </button>
          </div>
        </div>
        
        <div className="filter-group">
          <label>Risk Level:</label>
          <div className="button-group">
            <button 
              className={riskLevel === 'all' ? 'active' : ''}
              onClick={() => setRiskLevel('all')}
            >
              All
            </button>
            <button 
              className={riskLevel === 'low' ? 'active' : ''}
              onClick={() => setRiskLevel('low')}
            >
              Low
            </button>
            <button 
              className={riskLevel === 'medium' ? 'active' : ''}
              onClick={() => setRiskLevel('medium')}
            >
              Medium
            </button>
            <button 
              className={riskLevel === 'high' ? 'active' : ''}
              onClick={() => setRiskLevel('high')}
            >
              High
            </button>
          </div>
        </div>
        
        <div className="search-filter">
          <input type="text" placeholder="Search symbols..." />
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
        </div>
      </div>
      
      <div className="signals-table-container">
        <table className="signals-table">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Name</th>
              <th>Signal</th>
              <th>Price</th>
              <th>Target</th>
              <th>Stop Loss</th>
              <th>Confidence</th>
              <th>Risk</th>
              {isTraderPro && <th>Strategy</th>}
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="symbol">AAPL</td>
              <td className="name">Apple Inc.</td>
              <td className="signal buy">BUY</td>
              <td className="price">$198.45</td>
              <td className="target">$215.00</td>
              <td className="stop-loss">$190.00</td>
              <td className="confidence high">92%</td>
              <td className="risk medium">Medium</td>
              {isTraderPro && <td className="strategy">Momentum</td>}
              <td className="actions">
                <button className="action-button">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 5v14M5 12h14" />
                  </svg>
                </button>
              </td>
            </tr>
            <tr>
              <td className="symbol">MSFT</td>
              <td className="name">Microsoft Corp.</td>
              <td className="signal buy">BUY</td>
              <td className="price">$415.72</td>
              <td className="target">$440.00</td>
              <td className="stop-loss">$400.00</td>
              <td className="confidence high">89%</td>
              <td className="risk low">Low</td>
              {isTraderPro && <td className="strategy">Breakout</td>}
              <td className="actions">
                <button className="action-button">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 5v14M5 12h14" />
                  </svg>
                </button>
              </td>
            </tr>
            <tr>
              <td className="symbol">TSLA</td>
              <td className="name">Tesla Inc.</td>
              <td className="signal sell">SELL</td>
              <td className="price">$187.23</td>
              <td className="target">$165.00</td>
              <td className="stop-loss">$195.00</td>
              <td className="confidence medium">78%</td>
              <td className="risk high">High</td>
              {isTraderPro && <td className="strategy">Reversal</td>}
              <td className="actions">
                <button className="action-button">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 5v14M5 12h14" />
                  </svg>
                </button>
              </td>
            </tr>
            <tr>
              <td className="symbol">NVDA</td>
              <td className="name">NVIDIA Corp.</td>
              <td className="signal buy">BUY</td>
              <td className="price">$924.58</td>
              <td className="target">$1000.00</td>
              <td className="stop-loss">$880.00</td>
              <td className="confidence high">85%</td>
              <td className="risk medium">Medium</td>
              {isTraderPro && <td className="strategy">Momentum</td>}
              <td className="actions">
                <button className="action-button">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 5v14M5 12h14" />
                  </svg>
                </button>
              </td>
            </tr>
            <tr>
              <td className="symbol">AMZN</td>
              <td className="name">Amazon.com Inc.</td>
              <td className="signal buy">BUY</td>
              <td className="price">$178.75</td>
              <td className="target">$195.00</td>
              <td className="stop-loss">$170.00</td>
              <td className="confidence medium">76%</td>
              <td className="risk low">Low</td>
              {isTraderPro && <td className="strategy">Value</td>}
              <td className="actions">
                <button className="action-button">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 5v14M5 12h14" />
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      {isTraderPro && (
        <div className="pro-features">
          <div className="pro-feature-card">
            <div className="pro-badge">PRO</div>
            <h3>Custom Signal Alerts</h3>
            <p>Set up custom alerts for specific symbols or conditions.</p>
            <button className="feature-button">Configure Alerts</button>
          </div>
          
          <div className="pro-feature-card">
            <div className="pro-badge">PRO</div>
            <h3>Signal Backtesting</h3>
            <p>Test signal performance against historical data.</p>
            <button className="feature-button">Run Backtest</button>
          </div>
          
          <div className="pro-feature-card">
            <div className="pro-badge">PRO</div>
            <h3>Export Signals</h3>
            <p>Export signals to CSV or integrate with trading platforms.</p>
            <button className="feature-button">Export</button>
          </div>
        </div>
      )}
      
      <div className="signals-pagination">
        <button className="pagination-button" disabled>
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 18 9 12 15 6" />
          </svg>
          Previous
        </button>
        <div className="pagination-info">
          Page 1 of 3
        </div>
        <button className="pagination-button">
          Next
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>
      </div>
    </div>
  );
}
