import React from 'react';
import { useUserPlanContext } from '../../context/UserPlanContext';
import './RiskManagement.css';

export function RiskManagement() {
  const { userPlan } = useUserPlanContext();
  const isTraderPro = userPlan === 'trader-pro';
  
  return (
    <div className="risk-management">
      <header className="risk-header">
        <h1>Risk Management</h1>
        <div className="risk-actions">
          <button className="refresh-button">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2" />
            </svg>
            Refresh
          </button>
        </div>
      </header>
      
      <div className="risk-overview">
        <div className="risk-card market-risk">
          <h2>Market Risk Assessment</h2>
          <div className="risk-level">
            <div className="risk-meter">
              <div className="risk-indicator" style={{ left: '65%' }}></div>
              <div className="risk-scale">
                <span>Low</span>
                <span>Medium</span>
                <span>High</span>
              </div>
            </div>
            <div className="risk-value">65%</div>
          </div>
          <div className="risk-factors">
            <div className="risk-factor">
              <span className="factor-name">Volatility (VIX)</span>
              <div className="factor-bar-container">
                <div className="factor-bar" style={{ width: '70%' }}></div>
              </div>
              <span className="factor-value high">High</span>
            </div>
            <div className="risk-factor">
              <span className="factor-name">Market Breadth</span>
              <div className="factor-bar-container">
                <div className="factor-bar" style={{ width: '45%' }}></div>
              </div>
              <span className="factor-value medium">Medium</span>
            </div>
            <div className="risk-factor">
              <span className="factor-name">Interest Rate Risk</span>
              <div className="factor-bar-container">
                <div className="factor-bar" style={{ width: '60%' }}></div>
              </div>
              <span className="factor-value medium">Medium</span>
            </div>
            <div className="risk-factor">
              <span className="factor-name">Liquidity Risk</span>
              <div className="factor-bar-container">
                <div className="factor-bar" style={{ width: '30%' }}></div>
              </div>
              <span className="factor-value low">Low</span>
            </div>
          </div>
        </div>
        
        <div className="risk-card portfolio-risk">
          <h2>Portfolio Risk Analysis</h2>
          <div className="portfolio-metrics">
            <div className="metric">
              <span className="metric-name">Beta</span>
              <span className="metric-value">1.2</span>
              <span className="metric-desc">Higher volatility than market</span>
            </div>
            <div className="metric">
              <span className="metric-name">Sharpe Ratio</span>
              <span className="metric-value">0.85</span>
              <span className="metric-desc">Moderate risk-adjusted return</span>
            </div>
            <div className="metric">
              <span className="metric-name">Max Drawdown</span>
              <span className="metric-value">-12.4%</span>
              <span className="metric-desc">Largest peak-to-trough decline</span>
            </div>
            <div className="metric">
              <span className="metric-name">Value at Risk (95%)</span>
              <span className="metric-value">-3.2%</span>
              <span className="metric-desc">Potential daily loss</span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="risk-recommendations">
        <h2>Risk Management Recommendations</h2>
        <div className="recommendations-list">
          <div className="recommendation">
            <div className="recommendation-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
            </div>
            <div className="recommendation-content">
              <h3>Reduce Technology Exposure</h3>
              <p>Your portfolio has a 45% allocation to technology stocks, which is significantly higher than the recommended 25-30% for your risk profile. Consider rebalancing to reduce sector concentration risk.</p>
              <div className="recommendation-priority high">High Priority</div>
            </div>
          </div>
          
          <div className="recommendation">
            <div className="recommendation-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            </div>
            <div className="recommendation-content">
              <h3>Implement Stop-Loss Orders</h3>
              <p>Several of your positions lack stop-loss protection. Consider setting stop-loss orders at 10-15% below current prices to limit potential losses in volatile market conditions.</p>
              <div className="recommendation-priority medium">Medium Priority</div>
            </div>
          </div>
          
          <div className="recommendation">
            <div className="recommendation-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </svg>
            </div>
            <div className="recommendation-content">
              <h3>Increase Defensive Positions</h3>
              <p>With current market volatility, consider allocating 15-20% of your portfolio to defensive sectors such as consumer staples and utilities to provide stability during market downturns.</p>
              <div className="recommendation-priority medium">Medium Priority</div>
            </div>
          </div>
        </div>
      </div>
      
      {isTraderPro && (
        <div className="advanced-risk-tools">
          <div className="pro-badge">PRO</div>
          <h2>Advanced Risk Management Tools</h2>
          
          <div className="risk-tools-grid">
            <div className="risk-tool-card">
              <h3>Position Sizing Calculator</h3>
              <p>Optimize your position sizes based on your risk tolerance and account size.</p>
              <div className="tool-inputs">
                <div className="input-group">
                  <label>Account Size ($)</label>
                  <input type="number" defaultValue="10000" />
                </div>
                <div className="input-group">
                  <label>Risk Per Trade (%)</label>
                  <input type="number" defaultValue="2" />
                </div>
                <div className="input-group">
                  <label>Stop Loss (%)</label>
                  <input type="number" defaultValue="5" />
                </div>
              </div>
              <div className="tool-result">
                <span className="result-label">Recommended Position Size:</span>
                <span className="result-value">$4,000</span>
              </div>
              <button className="tool-button">Calculate</button>
            </div>
            
            <div className="risk-tool-card">
              <h3>Correlation Matrix</h3>
              <p>Analyze how your holdings move in relation to each other to identify diversification opportunities.</p>
              <div className="correlation-preview">
                <div className="correlation-cell header">Assets</div>
                <div className="correlation-cell header">SPY</div>
                <div className="correlation-cell header">QQQ</div>
                <div className="correlation-cell header">GLD</div>
                <div className="correlation-cell header">AAPL</div>
                
                <div className="correlation-cell header">SPY</div>
                <div className="correlation-cell high">1.00</div>
                <div className="correlation-cell high">0.92</div>
                <div className="correlation-cell low">0.12</div>
                <div className="correlation-cell medium">0.65</div>
                
                <div className="correlation-cell header">QQQ</div>
                <div className="correlation-cell high">0.92</div>
                <div className="correlation-cell high">1.00</div>
                <div className="correlation-cell low">0.08</div>
                <div className="correlation-cell high">0.85</div>
                
                <div className="correlation-cell header">GLD</div>
                <div className="correlation-cell low">0.12</div>
                <div className="correlation-cell low">0.08</div>
                <div className="correlation-cell high">1.00</div>
                <div className="correlation-cell low">0.15</div>
                
                <div className="correlation-cell header">AAPL</div>
                <div className="correlation-cell medium">0.65</div>
                <div className="correlation-cell high">0.85</div>
                <div className="correlation-cell low">0.15</div>
                <div className="correlation-cell high">1.00</div>
              </div>
              <button className="tool-button">View Full Matrix</button>
            </div>
            
            <div className="risk-tool-card">
              <h3>Monte Carlo Simulation</h3>
              <p>Project potential portfolio outcomes using statistical modeling.</p>
              <div className="simulation-preview">
                <div className="simulation-chart">
                  <div className="chart-placeholder">
                    <span>Simulation Chart</span>
                  </div>
                </div>
                <div className="simulation-stats">
                  <div className="stat">
                    <span className="stat-label">Median Return (1Y):</span>
                    <span className="stat-value">+12.4%</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Worst Case (5%):</span>
                    <span className="stat-value">-18.7%</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Best Case (95%):</span>
                    <span className="stat-value">+32.5%</span>
                  </div>
                </div>
              </div>
              <button className="tool-button">Run Simulation</button>
            </div>
          </div>
        </div>
      )}
      
      <div className="risk-education">
        <h2>Risk Management Education</h2>
        <div className="education-resources">
          <div className="resource-card">
            <h3>Understanding Risk Metrics</h3>
            <p>Learn how to interpret key risk metrics like Beta, Sharpe Ratio, and Value at Risk.</p>
            <a href="#" className="resource-link">Read Article</a>
          </div>
          <div className="resource-card">
            <h3>Portfolio Diversification Strategies</h3>
            <p>Discover effective techniques to diversify your investments across asset classes.</p>
            <a href="#" className="resource-link">Watch Video</a>
          </div>
          <div className="resource-card">
            <h3>Risk Management for Volatile Markets</h3>
            <p>Strategies to protect your portfolio during periods of high market volatility.</p>
            <a href="#" className="resource-link">Download Guide</a>
          </div>
        </div>
      </div>
    </div>
  );
}
