import { useState, useEffect, useCallback } from 'react';

// Update this URL with your actual API endpoint after deployment
const API_URL = 'https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/user-plan';

export function useUserPlan() {
  const [userPlan, setUserPlan] = useState('free'); // Default to free plan
  const [stripeCustomerId, setStripeCustomerId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check for URL override
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const planOverride = urlParams.get('plan');
    
    if (planOverride) {
      setUserPlan(planOverride);
      setStripeCustomerId('override_mode');
      setLoading(false);
      return;
    }
    
    fetchUserPlan();
  }, []);

  // Fetch user plan from Lambda
  const fetchUserPlan = useCallback(async () => {
    try {
      setLoading(true);
      
      // Get auth token (assuming you have an auth system)
      const token = localStorage.getItem('authToken');
      
      const response = await fetch(API_URL, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch user plan');
      }
      
      const data = await response.json();
      
      setUserPlan(data.userPlan);
      setStripeCustomerId(data.stripeCustomerId);
      
    } catch (err) {
      console.error('Error fetching user plan:', err);
      setError(err);
      // Fallback to free plan on error
      setUserPlan('free');
    } finally {
      setLoading(false);
    }
  }, []);

  // Helper functions for plan checks
  const isProOrAbove = useCallback(() => {
    return ['pro', 'business', 'enterprise'].includes(userPlan);
  }, [userPlan]);
  
  const canUploadImages = useCallback(() => {
    return ['pro', 'business', 'enterprise'].includes(userPlan);
  }, [userPlan]);
  
  const canUseFeature = useCallback((featureName) => {
    // This would check against a feature matrix defined elsewhere
    const featureMatrix = {
      uploadImages: ['pro', 'business', 'enterprise'],
      customBranding: ['business', 'enterprise'],
      apiAccess: ['enterprise']
    };
    
    return featureMatrix[featureName]?.includes(userPlan) || false;
  }, [userPlan]);

  // Force refresh the plan (e.g., after a subscription change)
  const refreshPlan = useCallback(() => {
    fetchUserPlan();
  }, [fetchUserPlan]);

  return {
    userPlan,
    stripeCustomerId,
    loading,
    error,
    isProOrAbove,
    canUploadImages,
    canUseFeature,
    refreshPlan
  };
}
