import React, { useState } from 'react';

const AppIntegration = () => {
  const [activeApp, setActiveApp] = useState(null);
  
  const apps = [
    {
      id: 'market-whisperer',
      name: 'Market Whisperer AI',
      description: 'AI-powered trading signals and market analysis',
      icon: '/assets/market-whisperer-icon.png',
      color: '#3498db',
      features: [
        'Real-time trading signals',
        'Market sentiment analysis',
        'Portfolio optimization',
        'Risk assessment tools'
      ],
      subscription: {
        free: {
          name: 'Basic',
          features: ['Limited market data', '3 trading signals per day']
        },
        paid: [
          {
            name: 'Trader',
            price: '$19.99/month',
            features: ['Real-time market data', '10 trading signals per day', 'Basic risk assessment']
          },
          {
            name: 'Trader Pro',
            price: '$39.99/month',
            features: ['Advanced technical analysis', 'Portfolio optimization', '50 trading signals per day', 'Historical backtesting']
          }
        ]
      }
    },
    {
      id: 'paulterpan',
      name: 'PaulterPan Trading',
      description: 'Automated trading platform with AI-driven strategies',
      icon: '/assets/paulterpan-icon.png',
      color: '#2ecc71',
      features: [
        'Automated trading execution',
        'Custom strategy builder',
        'Multi-exchange support',
        'Performance analytics'
      ],
      subscription: {
        free: {
          name: 'Demo',
          features: ['Paper trading only', 'Basic strategies']
        },
        paid: [
          {
            name: 'Trader',
            price: '$29.99/month',
            features: ['Live trading', '5 custom strategies', 'Email alerts']
          },
          {
            name: 'Institutional',
            price: '$99.99/month',
            features: ['Unlimited strategies', 'API access', 'Priority execution', '24/7 support']
          }
        ]
      }
    },
    {
      id: 'ai-clothing',
      name: 'AI Clothing',
      description: 'AI-designed fashion with personalized recommendations',
      icon: '/assets/ai-clothing-icon.png',
      color: '#9b59b6',
      features: [
        'AI-generated clothing designs',
        'Virtual try-on',
        'Style recommendations',
        'Custom sizing'
      ],
      subscription: {
        free: {
          name: 'Browse',
          features: ['View AI designs', 'Basic recommendations']
        },
        paid: [
          {
            name: 'Designer',
            price: '$14.99/month',
            features: ['Create custom designs', 'Virtual wardrobe', 'Seasonal updates']
          },
          {
            name: 'Fashionista',
            price: '$24.99/month',
            features: ['Priority manufacturing', 'Exclusive designs', 'Personal stylist AI']
          }
        ]
      }
    },
    {
      id: 'quantum-insights',
      name: 'Quantum Insights',
      description: 'Quantum computing applications for business intelligence',
      icon: '/assets/quantum-insights-icon.png',
      color: '#e74c3c',
      features: [
        'Quantum algorithm simulation',
        'Complex problem optimization',
        'Predictive analytics',
        'Quantum machine learning'
      ],
      subscription: {
        free: {
          name: 'Explorer',
          features: ['Basic quantum simulations', 'Educational resources']
        },
        paid: [
          {
            name: 'Researcher',
            price: '$49.99/month',
            features: ['Advanced quantum algorithms', 'Custom problem solving', 'Data integration']
          },
          {
            name: 'Enterprise',
            price: '$199.99/month',
            features: ['Dedicated quantum resources', 'API access', 'Custom development', 'Priority support']
          }
        ]
      }
    }
  ];
  
  const handleAppSelect = (app) => {
    setActiveApp(app);
  };
  
  const handleBackToApps = () => {
    setActiveApp(null);
  };
  
  return (
    <div className="app-integration">
      <h2>SoulCore App Ecosystem</h2>
      
      {activeApp ? (
        <div className="app-detail">
          <button className="back-button" onClick={handleBackToApps}>
            ← Back to Apps
          </button>
          
          <div className="app-header" style={{ backgroundColor: activeApp.color }}>
            <div className="app-icon" style={{ backgroundImage: `url(${activeApp.icon || '/assets/default-app-icon.png'})` }}></div>
            <div className="app-title">
              <h3>{activeApp.name}</h3>
              <p>{activeApp.description}</p>
            </div>
          </div>
          
          <div className="app-content">
            <div className="app-features">
              <h4>Key Features</h4>
              <ul>
                {activeApp.features.map((feature, idx) => (
                  <li key={idx}>{feature}</li>
                ))}
              </ul>
            </div>
            
            <div className="app-subscription">
              <h4>Subscription Plans</h4>
              
              <div className="subscription-cards">
                <div className="subscription-card free">
                  <div className="subscription-name">{activeApp.subscription.free.name}</div>
                  <div className="subscription-price">Free</div>
                  <ul className="subscription-features">
                    {activeApp.subscription.free.features.map((feature, idx) => (
                      <li key={idx}>{feature}</li>
                    ))}
                  </ul>
                  <button className="subscription-button">Get Started</button>
                </div>
                
                {activeApp.subscription.paid.map((plan, idx) => (
                  <div key={idx} className={`subscription-card paid ${idx === activeApp.subscription.paid.length - 1 ? 'premium' : ''}`}>
                    <div className="subscription-name">{plan.name}</div>
                    <div className="subscription-price">{plan.price}</div>
                    <ul className="subscription-features">
                      {plan.features.map((feature, featureIdx) => (
                        <li key={featureIdx}>{feature}</li>
                      ))}
                    </ul>
                    <button className="subscription-button">Subscribe</button>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="app-integration-options">
              <h4>Integration with SoulCore</h4>
              <p>
                Connect {activeApp.name} with SoulCore Society to enable AI agents to access and utilize its features.
              </p>
              <div className="integration-toggles">
                <div className="integration-toggle">
                  <input type="checkbox" id={`data-sharing-${activeApp.id}`} />
                  <label htmlFor={`data-sharing-${activeApp.id}`}>Enable Data Sharing</label>
                </div>
                <div className="integration-toggle">
                  <input type="checkbox" id={`agent-access-${activeApp.id}`} defaultChecked />
                  <label htmlFor={`agent-access-${activeApp.id}`}>Allow Agent Access</label>
                </div>
                <div className="integration-toggle">
                  <input type="checkbox" id={`notifications-${activeApp.id}`} defaultChecked />
                  <label htmlFor={`notifications-${activeApp.id}`}>Enable Notifications</label>
                </div>
              </div>
              <button className="save-integration">Save Integration Settings</button>
            </div>
          </div>
        </div>
      ) : (
        <div className="app-grid">
          {apps.map(app => (
            <div key={app.id} className="app-card" onClick={() => handleAppSelect(app)}>
              <div className="app-card-icon" style={{ backgroundColor: app.color }}>
                <div className="app-icon" style={{ backgroundImage: `url(${app.icon || '/assets/default-app-icon.png'})` }}></div>
              </div>
              <div className="app-card-content">
                <h3>{app.name}</h3>
                <p>{app.description}</p>
              </div>
              <div className="app-card-footer">
                <button className="view-app-button">View Details</button>
              </div>
            </div>
          ))}
          
          <div className="app-card new-app">
            <div className="app-card-icon" style={{ backgroundColor: '#7f8c8d' }}>
              <div className="new-app-plus">+</div>
            </div>
            <div className="app-card-content">
              <h3>Coming Soon</h3>
              <p>New SoulCore apps are in development</p>
            </div>
            <div className="app-card-footer">
              <button className="view-app-button disabled">Stay Tuned</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AppIntegration;
