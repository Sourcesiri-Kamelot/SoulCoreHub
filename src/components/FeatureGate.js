import React from 'react';
import { useUserPlanContext } from '../context/UserPlanContext';
import { canUseFeature } from '../utils/planUtils';
import './FeatureGate.css';

/**
 * A component that conditionally renders children based on the user's plan
 * 
 * @param {Object} props
 * @param {string} props.feature - The feature name to check against the feature matrix
 * @param {React.ReactNode} props.children - The content to render if the feature is available
 * @param {React.ReactNode} props.fallback - Optional content to render if the feature is not available
 */
export function FeatureGate({ feature, children, fallback }) {
  const { userPlan, loading } = useUserPlanContext();
  
  if (loading) {
    return <div className="feature-gate-loading">Loading...</div>;
  }
  
  const hasAccess = canUseFeature(feature, userPlan);
  
  if (hasAccess) {
    return children;
  }
  
  if (fallback) {
    return fallback;
  }
  
  return (
    <div className="feature-gate-upgrade">
      <div className="feature-gate-message">
        <h4>Feature Unavailable</h4>
        <p>Upgrade your plan to access {feature}.</p>
        <button className="upgrade-button">Upgrade Now</button>
      </div>
    </div>
  );
}
