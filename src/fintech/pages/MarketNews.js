import React, { useState } from 'react';
import './MarketNews.css';

export function MarketNews() {
  const [activeCategory, setActiveCategory] = useState('all');
  
  return (
    <div className="market-news-page">
      <header className="news-header">
        <h1>Market News</h1>
        <div className="news-actions">
          <button className="refresh-button">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2" />
            </svg>
            Refresh
          </button>
        </div>
      </header>
      
      <div className="news-categories">
        <button 
          className={`category-button ${activeCategory === 'all' ? 'active' : ''}`}
          onClick={() => setActiveCategory('all')}
        >
          All News
        </button>
        <button 
          className={`category-button ${activeCategory === 'market' ? 'active' : ''}`}
          onClick={() => setActiveCategory('market')}
        >
          Market Updates
        </button>
        <button 
          className={`category-button ${activeCategory === 'economy' ? 'active' : ''}`}
          onClick={() => setActiveCategory('economy')}
        >
          Economy
        </button>
        <button 
          className={`category-button ${activeCategory === 'earnings' ? 'active' : ''}`}
          onClick={() => setActiveCategory('earnings')}
        >
          Earnings
        </button>
        <button 
          className={`category-button ${activeCategory === 'crypto' ? 'active' : ''}`}
          onClick={() => setActiveCategory('crypto')}
        >
          Crypto
        </button>
      </div>
      
      <div className="news-grid">
        <div className="featured-news">
          <div className="news-card featured">
            <div className="news-image" style={{ backgroundImage: 'url(https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80)' }}></div>
            <div className="news-content">
              <div className="news-meta">
                <span className="news-source">Bloomberg</span>
                <span className="news-time">2 hours ago</span>
              </div>
              <h2 className="news-title">Fed Signals Potential Rate Cut in September Meeting</h2>
              <p className="news-summary">
                Federal Reserve officials indicated they may be ready to cut interest rates at their next meeting, 
                citing improving inflation data and concerns about labor market cooling.
              </p>
              <div className="news-tags">
                <span className="news-tag">Federal Reserve</span>
                <span className="news-tag">Interest Rates</span>
                <span className="news-tag">Economy</span>
              </div>
              <button className="read-more">Read Full Story</button>
            </div>
          </div>
        </div>
        
        <div className="news-list">
          <div className="news-card">
            <div className="news-content">
              <div className="news-meta">
                <span className="news-source">CNBC</span>
                <span className="news-time">4 hours ago</span>
              </div>
              <h3 className="news-title">Tech Stocks Rally on Strong Earnings Reports</h3>
              <p className="news-summary">
                Major tech companies exceeded analyst expectations, driving market gains as investors react positively to quarterly results.
              </p>
              <div className="news-tags">
                <span className="news-tag">Tech</span>
                <span className="news-tag">Earnings</span>
              </div>
            </div>
          </div>
          
          <div className="news-card">
            <div className="news-content">
              <div className="news-meta">
                <span className="news-source">Reuters</span>
                <span className="news-time">6 hours ago</span>
              </div>
              <h3 className="news-title">Oil Prices Stabilize After Recent Volatility</h3>
              <p className="news-summary">
                Crude oil futures found support after a week of fluctuations due to supply concerns and changing demand forecasts.
              </p>
              <div className="news-tags">
                <span className="news-tag">Oil</span>
                <span className="news-tag">Commodities</span>
              </div>
            </div>
          </div>
          
          <div className="news-card">
            <div className="news-content">
              <div className="news-meta">
                <span className="news-source">Wall Street Journal</span>
                <span className="news-time">8 hours ago</span>
              </div>
              <h3 className="news-title">Housing Market Shows Signs of Cooling as Mortgage Rates Rise</h3>
              <p className="news-summary">
                New home sales declined for the third consecutive month as higher mortgage rates impact buyer demand and affordability.
              </p>
              <div className="news-tags">
                <span className="news-tag">Housing</span>
                <span className="news-tag">Economy</span>
              </div>
            </div>
          </div>
          
          <div className="news-card">
            <div className="news-content">
              <div className="news-meta">
                <span className="news-source">Financial Times</span>
                <span className="news-time">10 hours ago</span>
              </div>
              <h3 className="news-title">European Markets Close Higher on ECB Policy Outlook</h3>
              <p className="news-summary">
                European stocks finished the day in positive territory after the European Central Bank signaled a potential pause in rate hikes.
              </p>
              <div className="news-tags">
                <span className="news-tag">Europe</span>
                <span className="news-tag">ECB</span>
              </div>
            </div>
          </div>
          
          <div className="news-card">
            <div className="news-content">
              <div className="news-meta">
                <span className="news-source">CoinDesk</span>
                <span className="news-time">12 hours ago</span>
              </div>
              <h3 className="news-title">Bitcoin Surges Past $60,000 on ETF Inflow Reports</h3>
              <p className="news-summary">
                The leading cryptocurrency broke through key resistance levels after reports showed significant inflows to Bitcoin ETFs.
              </p>
              <div className="news-tags">
                <span className="news-tag">Crypto</span>
                <span className="news-tag">Bitcoin</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="market-calendar">
        <h2>Upcoming Market Events</h2>
        <div className="calendar-events">
          <div className="calendar-event">
            <div className="event-date">
              <span className="event-day">15</span>
              <span className="event-month">MAY</span>
            </div>
            <div className="event-details">
              <h3 className="event-title">FOMC Meeting Minutes Release</h3>
              <p className="event-description">Federal Reserve to release minutes from the latest Federal Open Market Committee meeting</p>
            </div>
            <div className="event-impact high">
              High Impact
            </div>
          </div>
          
          <div className="calendar-event">
            <div className="event-date">
              <span className="event-day">18</span>
              <span className="event-month">MAY</span>
            </div>
            <div className="event-details">
              <h3 className="event-title">U.S. Retail Sales Data</h3>
              <p className="event-description">Monthly report on retail sales figures and consumer spending trends</p>
            </div>
            <div className="event-impact medium">
              Medium Impact
            </div>
          </div>
          
          <div className="calendar-event">
            <div className="event-date">
              <span className="event-day">20</span>
              <span className="event-month">MAY</span>
            </div>
            <div className="event-details">
              <h3 className="event-title">NVIDIA Earnings Report</h3>
              <p className="event-description">Q1 2025 earnings release for NVIDIA Corporation (NVDA)</p>
            </div>
            <div className="event-impact high">
              High Impact
            </div>
          </div>
        </div>
      </div>
      
      <div className="news-pagination">
        <button className="pagination-button" disabled>
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 18 9 12 15 6" />
          </svg>
          Previous
        </button>
        <div className="pagination-info">
          Page 1 of 5
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
