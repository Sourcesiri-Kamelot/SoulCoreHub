import React from 'react';
import { useUserPlanContext } from '../../context/UserPlanContext';
import './MarketDashboard.css';

export function MarketDashboard() {
  const { userPlan } = useUserPlanContext();
  const isTraderPro = userPlan === 'trader-pro';
  
  return (
    <div className="market-dashboard">
      <header className="dashboard-header">
        <h1>Market Dashboard</h1>
        <div className="dashboard-actions">
          <button className="refresh-button">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2" />
            </svg>
            Refresh
          </button>
          <div className="date-display">
            {new Date().toLocaleDateString('en-US', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </div>
        </div>
      </header>
      
      <div className="dashboard-grid">
        <div className="dashboard-card market-summary">
          <h2>Market Summary</h2>
          <div className="market-indices">
            <div className="market-index">
              <span className="index-name">S&P 500</span>
              <span className="index-value">4,783.45</span>
              <span className="index-change positive">+1.2%</span>
            </div>
            <div className="market-index">
              <span className="index-name">NASDAQ</span>
              <span className="index-value">16,742.39</span>
              <span className="index-change positive">+1.8%</span>
            </div>
            <div className="market-index">
              <span className="index-name">DOW</span>
              <span className="index-value">38,239.98</span>
              <span className="index-change positive">+0.9%</span>
            </div>
            <div className="market-index">
              <span className="index-name">VIX</span>
              <span className="index-value">17.25</span>
              <span className="index-change negative">-5.3%</span>
            </div>
          </div>
        </div>
        
        <div className="dashboard-card top-signals">
          <h2>Top Trading Signals</h2>
          <div className="signal-list">
            <div className="signal-item">
              <div className="signal-info">
                <span className="signal-symbol">AAPL</span>
                <span className="signal-name">Apple Inc.</span>
              </div>
              <div className="signal-action buy">BUY</div>
              <div className="signal-price">$198.45</div>
              <div className="signal-confidence">92%</div>
            </div>
            <div className="signal-item">
              <div className="signal-info">
                <span className="signal-symbol">MSFT</span>
                <span className="signal-name">Microsoft Corp.</span>
              </div>
              <div className="signal-action buy">BUY</div>
              <div className="signal-price">$415.72</div>
              <div className="signal-confidence">89%</div>
            </div>
            <div className="signal-item">
              <div className="signal-info">
                <span className="signal-symbol">TSLA</span>
                <span className="signal-name">Tesla Inc.</span>
              </div>
              <div className="signal-action sell">SELL</div>
              <div className="signal-price">$187.23</div>
              <div className="signal-confidence">78%</div>
            </div>
            <div className="signal-item">
              <div className="signal-info">
                <span className="signal-symbol">NVDA</span>
                <span className="signal-name">NVIDIA Corp.</span>
              </div>
              <div className="signal-action buy">BUY</div>
              <div className="signal-price">$924.58</div>
              <div className="signal-confidence">85%</div>
            </div>
          </div>
          <div className="card-footer">
            <a href="/fintech/signals" className="view-all">View All Signals</a>
          </div>
        </div>
        
        <div className="dashboard-card market-sentiment">
          <h2>Market Sentiment</h2>
          <div className="sentiment-gauge">
            <div className="gauge-label">Bullish</div>
            <div className="gauge-container">
              <div className="gauge-bar" style={{ width: '65%' }}></div>
            </div>
            <div className="gauge-value">65%</div>
          </div>
          <div className="sentiment-factors">
            <div className="sentiment-factor">
              <span className="factor-name">Technical Indicators</span>
              <span className="factor-value positive">Bullish</span>
            </div>
            <div className="sentiment-factor">
              <span className="factor-name">Market Breadth</span>
              <span className="factor-value positive">Positive</span>
            </div>
            <div className="sentiment-factor">
              <span className="factor-name">Volatility</span>
              <span className="factor-value negative">Elevated</span>
            </div>
            <div className="sentiment-factor">
              <span className="factor-name">Put/Call Ratio</span>
              <span className="factor-value neutral">Neutral</span>
            </div>
          </div>
        </div>
        
        <div className="dashboard-card market-news">
          <h2>Latest Market News</h2>
          <div className="news-list">
            <div className="news-item">
              <div className="news-time">10:45 AM</div>
              <div className="news-content">
                <h3>Fed Signals Potential Rate Cut in September Meeting</h3>
                <p>Federal Reserve officials indicated they may be ready to cut interest rates at their next meeting...</p>
              </div>
            </div>
            <div className="news-item">
              <div className="news-time">9:30 AM</div>
              <div className="news-content">
                <h3>Tech Stocks Rally on Strong Earnings Reports</h3>
                <p>Major tech companies exceeded analyst expectations, driving market gains...</p>
              </div>
            </div>
            <div className="news-item">
              <div className="news-time">8:15 AM</div>
              <div className="news-content">
                <h3>Oil Prices Stabilize After Recent Volatility</h3>
                <p>Crude oil futures found support after a week of fluctuations due to supply concerns...</p>
              </div>
            </div>
          </div>
          <div className="card-footer">
            <a href="/fintech/news" className="view-all">View All News</a>
          </div>
        </div>
        
        {isTraderPro && (
          <div className="dashboard-card pro-analysis">
            <div className="pro-badge">PRO</div>
            <h2>Advanced Market Analysis</h2>
            <div className="analysis-content">
              <div className="analysis-section">
                <h3>Market Cycle Position</h3>
                <div className="cycle-indicator">
                  <div className="cycle-stage current">Expansion</div>
                  <div className="cycle-stage">Peak</div>
                  <div className="cycle-stage">Contraction</div>
                  <div className="cycle-stage">Trough</div>
                </div>
              </div>
              <div className="analysis-section">
                <h3>Sector Rotation</h3>
                <div className="sector-list">
                  <div className="sector-item outperforming">
                    <span className="sector-name">Technology</span>
                    <span className="sector-performance">+2.4%</span>
                  </div>
                  <div className="sector-item outperforming">
                    <span className="sector-name">Healthcare</span>
                    <span className="sector-performance">+1.8%</span>
                  </div>
                  <div className="sector-item underperforming">
                    <span className="sector-name">Energy</span>
                    <span className="sector-performance">-0.7%</span>
                  </div>
                  <div className="sector-item neutral">
                    <span className="sector-name">Financials</span>
                    <span className="sector-performance">+0.3%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div className="dashboard-card ai-insights">
          <h2>AI Market Insights</h2>
          <div className="insight-content">
            <p className="insight-summary">
              Market Whisperer AI detects a potential bullish trend continuation with strong momentum in technology and healthcare sectors. 
              Consider increasing exposure to quality growth stocks while maintaining defensive positions.
            </p>
            <div className="insight-details">
              <div className="insight-detail">
                <span className="detail-label">Risk Level:</span>
                <span className="detail-value moderate">Moderate</span>
              </div>
              <div className="insight-detail">
                <span className="detail-label">Time Horizon:</span>
                <span className="detail-value">1-3 Months</span>
              </div>
              <div className="insight-detail">
                <span className="detail-label">Confidence:</span>
                <span className="detail-value high">High (82%)</span>
              </div>
            </div>
            <div className="insight-actions">
              <button className="action-button">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="7 10 12 15 17 10" />
                  <line x1="12" y1="15" x2="12" y2="3" />
                </svg>
                Save Insight
              </button>
              <button className="action-button">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" />
                  <polyline points="16 6 12 2 8 6" />
                  <line x1="12" y1="2" x2="12" y2="15" />
                </svg>
                Export
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
