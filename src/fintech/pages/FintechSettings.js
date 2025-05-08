import React from 'react';
import { useUserPlanContext } from '../../context/UserPlanContext';
import './FintechSettings.css';

export function FintechSettings() {
  const { userPlan } = useUserPlanContext();
  const isTraderPro = userPlan === 'trader-pro';
  
  return (
    <div className="fintech-settings">
      <header className="settings-header">
        <h1>Settings</h1>
      </header>
      
      <div className="settings-grid">
        <div className="settings-card subscription-settings">
          <h2>Subscription</h2>
          <div className="current-plan">
            <div className="plan-badge">{isTraderPro ? 'Trader Pro' : 'Trader'}</div>
            <div className="plan-price">${isTraderPro ? '39.99' : '19.99'}<span>/month</span></div>
          </div>
          
          <div className="plan-features">
            <h3>Your Plan Features:</h3>
            <ul className="feature-list">
              {isTraderPro ? (
                <>
                  <li>Advanced technical analysis</li>
                  <li>Custom trading strategies</li>
                  <li>Portfolio optimization</li>
                  <li>Risk management tools</li>
                  <li>Priority market alerts</li>
                  <li>Historical backtesting</li>
                  <li>50 trading signals per day</li>
                  <li>20 market analyses per day</li>
                  <li>100 watchlist stocks</li>
                </>
              ) : (
                <>
                  <li>Access to Market Whisperer AI</li>
                  <li>Real-time trading signals</li>
                  <li>Market analysis</li>
                  <li>Risk assessment tools</li>
                  <li>Trading strategy recommendations</li>
                  <li>Daily market insights</li>
                  <li>10 trading signals per day</li>
                  <li>5 market analyses per day</li>
                  <li>20 watchlist stocks</li>
                </>
              )}
            </ul>
          </div>
          
          {!isTraderPro && (
            <div className="upgrade-section">
              <h3>Upgrade to Trader Pro</h3>
              <p>Get access to advanced features like portfolio optimization and custom trading strategies.</p>
              <button className="upgrade-button">Upgrade Now</button>
            </div>
          )}
          
          <div className="subscription-actions">
            <button className="secondary-button">Manage Subscription</button>
            <button className="text-button">View Billing History</button>
          </div>
        </div>
        
        <div className="settings-card notification-settings">
          <h2>Notifications</h2>
          <div className="settings-form">
            <div className="setting-item">
              <div className="setting-info">
                <h3>Trading Signals</h3>
                <p>Receive notifications when new trading signals are available.</p>
              </div>
              <div className="setting-control">
                <label className="toggle">
                  <input type="checkbox" defaultChecked />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>
            
            <div className="setting-item">
              <div className="setting-info">
                <h3>Market News</h3>
                <p>Get notified about important market news and events.</p>
              </div>
              <div className="setting-control">
                <label className="toggle">
                  <input type="checkbox" defaultChecked />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>
            
            <div className="setting-item">
              <div className="setting-info">
                <h3>Price Alerts</h3>
                <p>Receive alerts when stocks in your watchlist hit target prices.</p>
              </div>
              <div className="setting-control">
                <label className="toggle">
                  <input type="checkbox" defaultChecked />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>
            
            <div className="setting-item">
              <div className="setting-info">
                <h3>Risk Warnings</h3>
                <p>Get notified about potential risks in your portfolio.</p>
              </div>
              <div className="setting-control">
                <label className="toggle">
                  <input type="checkbox" defaultChecked />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>
            
            <div className="setting-item">
              <div className="setting-info">
                <h3>Email Notifications</h3>
                <p>Receive notifications via email in addition to in-app alerts.</p>
              </div>
              <div className="setting-control">
                <label className="toggle">
                  <input type="checkbox" />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
        
        <div className="settings-card preferences-settings">
          <h2>Preferences</h2>
          <div className="settings-form">
            <div className="setting-item">
              <div className="setting-info">
                <h3>Default Timeframe</h3>
                <p>Set the default timeframe for charts and analysis.</p>
              </div>
              <div className="setting-control">
                <select className="settings-select">
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
            </div>
            
            <div className="setting-item">
              <div className="setting-info">
                <h3>Risk Tolerance</h3>
                <p>Set your risk tolerance level for recommendations.</p>
              </div>
              <div className="setting-control">
                <select className="settings-select">
                  <option value="conservative">Conservative</option>
                  <option value="moderate" selected>Moderate</option>
                  <option value="aggressive">Aggressive</option>
                </select>
              </div>
            </div>
            
            <div className="setting-item">
              <div className="setting-info">
                <h3>Default Market</h3>
                <p>Set your primary market for analysis and signals.</p>
              </div>
              <div className="setting-control">
                <select className="settings-select">
                  <option value="us" selected>US Markets</option>
                  <option value="global">Global Markets</option>
                  <option value="crypto">Crypto Markets</option>
                </select>
              </div>
            </div>
            
            <div className="setting-item">
              <div className="setting-info">
                <h3>Dark Mode</h3>
                <p>Toggle between light and dark interface themes.</p>
              </div>
              <div className="setting-control">
                <label className="toggle">
                  <input type="checkbox" defaultChecked />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
        
        <div className="settings-card data-settings">
          <h2>Data & Privacy</h2>
          <div className="settings-form">
            <div className="setting-item">
              <div className="setting-info">
                <h3>Data Collection</h3>
                <p>Allow collection of usage data to improve recommendations.</p>
              </div>
              <div className="setting-control">
                <label className="toggle">
                  <input type="checkbox" defaultChecked />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>
            
            <div className="setting-item">
              <div className="setting-info">
                <h3>Trading History</h3>
                <p>Store your trading history for performance analysis.</p>
              </div>
              <div className="setting-control">
                <label className="toggle">
                  <input type="checkbox" defaultChecked />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>
            
            <div className="setting-item">
              <div className="setting-info">
                <h3>Third-Party Integrations</h3>
                <p>Allow integration with third-party trading platforms.</p>
              </div>
              <div className="setting-control">
                <label className="toggle">
                  <input type="checkbox" />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
          
          <div className="data-actions">
            <button className="secondary-button">Export My Data</button>
            <button className="danger-button">Delete Account</button>
          </div>
        </div>
      </div>
      
      <div className="settings-actions">
        <button className="primary-button">Save Changes</button>
        <button className="secondary-button">Reset to Defaults</button>
      </div>
    </div>
  );
}
