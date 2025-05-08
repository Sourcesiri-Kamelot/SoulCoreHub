import pricingConfig from '../config/pricing.json';

/**
 * Check if a feature is available for a given plan
 * @param {string} featureName - Name of the feature to check
 * @param {string} userPlan - User's current plan
 * @returns {boolean} - Whether the feature is available
 */
export function canUseFeature(featureName, userPlan) {
  const { featureMatrix } = pricingConfig;
  
  if (!featureMatrix[featureName]) {
    console.warn(`Feature "${featureName}" not found in feature matrix`);
    return false;
  }
  
  return featureMatrix[featureName].includes(userPlan);
}

/**
 * Check if user's plan is Pro or above
 * @param {string} userPlan - User's current plan
 * @returns {boolean} - Whether the plan is Pro or above
 */
export function isProOrAbove(userPlan) {
  return ['pro', 'business', 'enterprise'].includes(userPlan);
}

/**
 * Check if user's plan is Business or above
 * @param {string} userPlan - User's current plan
 * @returns {boolean} - Whether the plan is Business or above
 */
export function isBusinessOrAbove(userPlan) {
  return ['business', 'enterprise'].includes(userPlan);
}

/**
 * Check if user's plan is Enterprise
 * @param {string} userPlan - User's current plan
 * @returns {boolean} - Whether the plan is Enterprise
 */
export function isEnterprise(userPlan) {
  return userPlan === 'enterprise';
}

/**
 * Get plan details by plan ID
 * @param {string} planId - Plan ID
 * @returns {object|null} - Plan details or null if not found
 */
export function getPlanDetails(planId) {
  return pricingConfig.plans[planId] || null;
}

/**
 * Get daily message limit for a plan
 * @param {string} userPlan - User's current plan
 * @returns {number|string} - Daily message limit
 */
export function getMessageLimit(userPlan) {
  const plan = getPlanDetails(userPlan);
  return plan ? plan.limits.messagesPerDay : 0;
}

/**
 * Get daily deep action limit for a plan
 * @param {string} userPlan - User's current plan
 * @returns {number|string} - Daily deep action limit
 */
export function getDeepActionLimit(userPlan) {
  const plan = getPlanDetails(userPlan);
  return plan ? plan.limits.deepActionsPerDay : 0;
}

/**
 * Get storage limit for a plan
 * @param {string} userPlan - User's current plan
 * @returns {string} - Storage limit
 */
export function getStorageLimit(userPlan) {
  const plan = getPlanDetails(userPlan);
  return plan ? plan.limits.storageLimit : '0';
}

/**
 * Get Stripe plan ID for a plan
 * @param {string} planId - Plan ID
 * @returns {string|null} - Stripe plan ID or null if not found
 */
export function getStripePlanId(planId) {
  return pricingConfig.stripePlanIds[planId] || null;
}
