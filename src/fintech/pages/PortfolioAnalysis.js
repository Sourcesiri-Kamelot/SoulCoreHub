import React from 'react';
import './PortfolioAnalysis.css';

export function PortfolioAnalysis() {
  return (
    <div className="portfolio-analysis">
      <header className="portfolio-header">
        <h1>Portfolio Analysis</h1>
        <div className="portfolio-actions">
          <button className="refresh-button">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2" />
            </svg>
            Refresh
          </button>
          <button className="action-button">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            Export
          </button>
        </div>
      </header>
      
      <div className="portfolio-summary">
        <div className="summary-card">
          <div className="summary-value">$124,856.32</div>
          <div className="summary-label">Total Value</div>
          <div className="summary-change positive">+$2,345.67 (1.9%)</div>
        </div>
        
        <div className="summary-card">
          <div className="summary-value">18.4%</div>
          <div className="summary-label">YTD Return</div>
          <div className="summary-comparison positive">+5.2% vs S&P 500</div>
        </div>
        
        <div className="summary-card">
          <div className="summary-value">1.2</div>
          <div className="summary-label">Portfolio Beta</div>
          <div className="summary-desc">Higher volatility than market</div>
        </div>
        
        <div className="summary-card">
          <div className="summary-value">0.85</div>
          <div className="summary-label">Sharpe Ratio</div>
          <div className="summary-desc">Moderate risk-adjusted return</div>
        </div>
      </div>
      
      <div className="portfolio-charts">
        <div className="chart-card allocation-chart">
          <h2>Asset Allocation</h2>
          <div className="chart-container">
            <div className="chart-placeholder">
              <span>Asset Allocation Chart</span>
            </div>
          </div>
          <div className="allocation-legend">
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#38bdf8' }}></div>
              <div className="legend-label">Stocks (65%)</div>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#818cf8' }}></div>
              <div className="legend-label">Bonds (20%)</div>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#c084fc' }}></div>
              <div className="legend-label">Cash (10%)</div>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#f472b6' }}></div>
              <div className="legend-label">Alternative (5%)</div>
            </div>
          </div>
        </div>
        
        <div className="chart-card sector-chart">
          <h2>Sector Breakdown</h2>
          <div className="chart-container">
            <div className="chart-placeholder">
              <span>Sector Breakdown Chart</span>
            </div>
          </div>
          <div className="sector-legend">
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#38bdf8' }}></div>
              <div className="legend-label">Technology (45%)</div>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#818cf8' }}></div>
              <div className="legend-label">Healthcare (15%)</div>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#c084fc' }}></div>
              <div className="legend-label">Financials (12%)</div>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#f472b6' }}></div>
              <div className="legend-label">Consumer (10%)</div>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#fb7185' }}></div>
              <div className="legend-label">Other (18%)</div>
            </div>
          </div>
        </div>
        
        <div className="chart-card performance-chart">
          <h2>Performance History</h2>
          <div className="chart-container large">
            <div className="chart-placeholder">
              <span>Performance History Chart</span>
            </div>
          </div>
          <div className="chart-timeframes">
            <button className="timeframe-button">1M</button>
            <button className="timeframe-button active">3M</button>
            <button className="timeframe-button">6M</button>
            <button className="timeframe-button">YTD</button>
            <button className="timeframe-button">1Y</button>
            <button className="timeframe-button">5Y</button>
          </div>
        </div>
      </div>
      
      <div className="portfolio-holdings">
        <h2>Holdings Analysis</h2>
        <div className="holdings-table-container">
          <table className="holdings-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Name</th>
                <th>Shares</th>
                <th>Price</th>
                <th>Value</th>
                <th>Allocation</th>
                <th>Return</th>
                <th>AI Rating</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="symbol">AAPL</td>
                <td className="name">Apple Inc.</td>
                <td className="shares">125</td>
                <td className="price">$198.45</td>
                <td className="value">$24,806.25</td>
                <td className="allocation">19.9%</td>
                <td className="return positive">+32.4%</td>
                <td className="rating">
                  <div className="rating-stars">
                    <span className="filled">★</span>
                    <span className="filled">★</span>
                    <span className="filled">★</span>
                    <span className="filled">★</span>
                    <span>★</span>
                  </div>
                </td>
              </tr>
              <tr>
                <td className="symbol">MSFT</td>
                <td className="name">Microsoft Corp.</td>
                <td className="shares">85</td>
                <td className="price">$415.72</td>
                <td className="value">$35,336.20</td>
                <td className="allocation">28.3%</td>
                <td className="return positive">+28.7%</td>
                <td className="rating">
                  <div className="rating-stars">
                    <span className="filled">★</span>
                    <span className="filled">★</span>
                    <span className="filled">★</span>
                    <span className="filled">★</span>
                    <span className="filled">★</span>
                  </div>
                </td>
              </tr>
              <tr>
                <td className="symbol">TSLA</td>
                <td className="name">Tesla Inc.</td>
                <td className="shares">50</td>
                <td className="price">$187.23</td>
                <td className="value">$9,361.50</td>
                <td className="allocation">7.5%</td>
                <td className="return negative">-12.8%</td>
                <td className="rating">
                  <div className="rating-stars">
                    <span className="filled">★</span>
                    <span className="filled">★</span>
                    <span>★</span>
                    <span>★</span>
                    <span>★</span>
                  </div>
                </td>
              </tr>
              <tr>
                <td className="symbol">NVDA</td>
                <td className="name">NVIDIA Corp.</td>
                <td className="shares">30</td>
                <td className="price">$924.58</td>
                <td className="value">$27,737.40</td>
                <td className="allocation">22.2%</td>
                <td className="return positive">+124.5%</td>
                <td className="rating">
                  <div className="rating-stars">
                    <span className="filled">★</span>
                    <span className="filled">★</span>
                    <span className="filled">★</span>
                    <span className="filled">★</span>
                    <span>★</span>
                  </div>
                </td>
              </tr>
              <tr>
                <td className="symbol">AMZN</td>
                <td className="name">Amazon.com Inc.</td>
                <td className="shares">45</td>
                <td className="price">$178.75</td>
                <td className="value">$8,043.75</td>
                <td className="allocation">6.4%</td>
                <td className="return positive">+15.2%</td>
                <td className="rating">
                  <div className="rating-stars">
                    <span className="filled">★</span>
                    <span className="filled">★</span>
                    <span className="filled">★</span>
                    <span className="filled">★</span>
                    <span>★</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div className="portfolio-optimization">
        <h2>Portfolio Optimization</h2>
        <div className="optimization-content">
          <div className="optimization-summary">
            <p>
              Market Whisperer AI has analyzed your portfolio and identified several optimization opportunities 
              to improve your risk-adjusted returns. The recommended changes could potentially increase your 
              Sharpe ratio from 0.85 to 1.12 while maintaining similar expected returns.
            </p>
          </div>
          
          <div className="optimization-recommendations">
            <div className="recommendation-card">
              <h3>Reduce Technology Concentration</h3>
              <p>Your portfolio has a 45% allocation to technology stocks, which creates significant sector concentration risk.</p>
              <div className="recommendation-actions">
                <div className="action">
                  <span className="action-type sell">Reduce</span>
                  <span className="action-details">NVDA by 10 shares ($9,245.80)</span>
                </div>
                <div className="action">
                  <span className="action-type sell">Reduce</span>
                  <span className="action-details">AAPL by 25 shares ($4,961.25)</span>
                </div>
              </div>
            </div>
            
            <div className="recommendation-card">
              <h3>Increase Defensive Positions</h3>
              <p>Adding defensive positions can help reduce portfolio volatility and provide stability during market downturns.</p>
              <div className="recommendation-actions">
                <div className="action">
                  <span className="action-type buy">Add</span>
                  <span className="action-details">PG (Procter & Gamble) - $10,000</span>
                </div>
                <div className="action">
                  <span className="action-type buy">Add</span>
                  <span className="action-details">VYM (Vanguard High Dividend) - $5,000</span>
                </div>
              </div>
            </div>
            
            <div className="recommendation-card">
              <h3>Implement Hedging Strategy</h3>
              <p>Consider adding a small allocation to hedging instruments to protect against market downturns.</p>
              <div className="recommendation-actions">
                <div className="action">
                  <span className="action-type buy">Add</span>
                  <span className="action-details">GLD (Gold ETF) - $5,000</span>
                </div>
                <div className="action">
                  <span className="action-type buy">Add</span>
                  <span className="action-details">TAIL (Tail Risk ETF) - $3,000</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="optimization-actions">
            <button className="primary-button">Apply Recommendations</button>
            <button className="secondary-button">Customize Optimization</button>
          </div>
        </div>
      </div>
    </div>
  );
}
