import React from 'react';
import { useUserPlanContext } from '../context/UserPlanContext';
import { getPlanDetails } from '../utils/planUtils';
import './PlanBadge.css';

export function PlanBadge() {
  const { userPlan, loading } = useUserPlanContext();
  
  if (loading) {
    return <div className="plan-badge loading">Loading...</div>;
  }
  
  const planDetails = getPlanDetails(userPlan);
  
  if (!planDetails) {
    return <div className="plan-badge unknown">Unknown Plan</div>;
  }
  
  return (
    <div className={`plan-badge ${userPlan}`}>
      {planDetails.name}
    </div>
  );
}
