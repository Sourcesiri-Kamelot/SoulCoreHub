from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class ClothingRecommendation(BaseModel):
    """Model for clothing recommendations"""

    essential_items: List[str]
    weather_specific: List[str]
    activity_specific: List[str]
    cultural_considerations: List[str]
    packing_tips: List[str]


class HikingOption(BaseModel):
    """Model for hiking recommendations"""

    trail_name: str
    difficulty: str
    duration_hours: float
    distance_km: float
    elevation_gain_m: float
    best_season: List[str]
    required_gear: List[str]
    safety_tips: List[str]
    highlights: List[str]


class InternetAvailability(BaseModel):
    """Model for internet availability information"""

    general_availability: str
    average_speed_mbps: float
    public_wifi_spots: List[str]
    recommended_providers: List[str]
    connectivity_tips: List[str]
    offline_alternatives: List[str]


class FoodOption(BaseModel):
    """Model for food recommendations"""

    local_specialties: List[str]
    recommended_restaurants: List[Dict[str, str]]
    dietary_considerations: List[str]
    food_safety_tips: List[str]
    price_ranges: Dict[str, str]
    must_try_dishes: List[str]


class PersonalizedRecommendation(BaseModel):
    """Model for personalized recommendations"""

    activities: List[Dict[str, str]]
    hidden_gems: List[str]
    local_events: List[Dict[str, str]]
    custom_itinerary: List[Dict[str, Any]]
    safety_tips: List[str]
    budget_recommendations: Dict[str, str]
