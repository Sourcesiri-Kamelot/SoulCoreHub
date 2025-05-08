import React from 'react';
import { Route, Routes } from 'react-router-dom';
import { FintechLayout } from './layout/FintechLayout';
import { MarketDashboard } from './pages/MarketDashboard';
import { TradingSignals } from './pages/TradingSignals';
import { PortfolioAnalysis } from './pages/PortfolioAnalysis';
import { RiskManagement } from './pages/RiskManagement';
import { MarketNews } from './pages/MarketNews';
import { FintechSettings } from './pages/FintechSettings';
import { FeatureGate } from '../components/FeatureGate';

/**
 * Routes for the fintech/trading section of SoulCoreHub
 */
export function FintechRoutes() {
  return (
    <Routes>
      <Route path="/" element={<FintechLayout />}>
        <Route index element={
          <FeatureGate feature="marketWhisperer" fallback={<FintechUpgrade />}>
            <MarketDashboard />
          </FeatureGate>
        } />
        <Route path="signals" element={
          <FeatureGate feature="tradingSignals" fallback={<FintechUpgrade />}>
            <TradingSignals />
          </FeatureGate>
        } />
        <Route path="portfolio" element={
          <FeatureGate feature="portfolioOptimization" fallback={<FintechUpgrade type="trader-pro" />}>
            <PortfolioAnalysis />
          </FeatureGate>
        } />
        <Route path="risk" element={
          <FeatureGate feature="riskManagement" fallback={<FintechUpgrade />}>
            <RiskManagement />
          </FeatureGate>
        } />
        <Route path="news" element={<MarketNews />} />
        <Route path="settings" element={<FintechSettings />} />
      </Route>
    </Routes>
  );
}

/**
 * Component shown when a user needs to upgrade to access a feature
 */
function FintechUpgrade({ type = 'trader' }) {
  return (
    <div className="fintech-upgrade">
      <div className="upgrade-content">
        <h2>Upgrade to {type === 'trader-pro' ? 'Trader Pro' : 'Trader'}</h2>
        <p>
          {type === 'trader-pro' 
            ? 'This feature requires a Trader Pro subscription to access advanced trading tools and analytics.'
            : 'Access Market Whisperer AI and get real-time trading signals with a Trader subscription.'}
        </p>
        <div className="pricing">
          <div className="price">
            <span className="amount">${type === 'trader-pro' ? '39.99' : '19.99'}</span>
            <span className="period">/month</span>
          </div>
        </div>
        <button className="upgrade-button">Upgrade Now</button>
        <p className="features-preview">
          {type === 'trader-pro' 
            ? 'Includes advanced technical analysis, custom trading strategies, and portfolio optimization'
            : 'Includes real-time trading signals, market analysis, and risk assessment tools'}
        </p>
      </div>
    </div>
  );
}
