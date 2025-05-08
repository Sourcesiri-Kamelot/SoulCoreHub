import React, { createContext, useContext } from 'react';
import { useUserPlan } from '../hooks/useUserPlan';

const UserPlanContext = createContext(null);

export function UserPlanProvider({ children }) {
  const userPlanData = useUserPlan();
  
  return (
    <UserPlanContext.Provider value={userPlanData}>
      {children}
    </UserPlanContext.Provider>
  );
}

export function useUserPlanContext() {
  const context = useContext(UserPlanContext);
  
  if (!context) {
    throw new Error('useUserPlanContext must be used within a UserPlanProvider');
  }
  
  return context;
}
