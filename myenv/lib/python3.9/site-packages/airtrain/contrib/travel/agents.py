from typing import Optional, List, Any
from airtrain.core.skills import Skill, ProcessingError
from airtrain.integrations.openai.skills import OpenAIParserSkill, OpenAIParserInput
from .models import (
    ClothingRecommendation,
    HikingOption,
    InternetAvailability,
    FoodOption,
    PersonalizedRecommendation,
)


class TravelAgentBase(OpenAIParserSkill):
    def __init__(self, credentials=None):
        super().__init__(credentials)
        self.model = "gpt-4o"
        self.temperature = 0.0


class ClothingAgent(TravelAgentBase):
    """Agent for clothing recommendations"""

    def get_recommendations(
        self, location: str, duration: int, activities: List[str], season: str
    ) -> ClothingRecommendation:
        prompt = f"""
        Provide clothing recommendations for a {duration}-day trip to {location} during {season}.
        Activities planned: {', '.join(activities)}.
        Include essential items, weather-specific clothing, and cultural considerations.
        """

        input_data = OpenAIParserInput(
            user_input=prompt,
            system_prompt="You are a travel clothing expert. Provide detailed packing recommendations.",
            response_model=ClothingRecommendation,
            model=self.model,
            temperature=self.temperature,
        )

        result = self.process(input_data)
        return result.parsed_response


class HikingAgent(TravelAgentBase):
    """Agent for hiking recommendations"""

    def get_hiking_options(
        self, location: str, difficulty: str, duration_preference: float
    ) -> List[HikingOption]:
        prompt = f"""
        Find hiking trails in {location} that match:
        - Difficulty level: {difficulty}
        - Preferred duration: around {duration_preference} hours
        Provide detailed trail information and safety tips.
        """

        input_data = OpenAIParserInput(
            user_input=prompt,
            system_prompt="You are a hiking expert. Recommend suitable trails with safety considerations.",
            response_model=List[HikingOption],
            model=self.model,
        )

        result = self.process(input_data)
        return result.parsed_response


class InternetAgent(TravelAgentBase):
    """Agent for internet availability information"""

    def get_connectivity_info(
        self,
        location: str,
        duration: int,
        work_requirements: Optional[List[str]] = None,
    ) -> InternetAvailability:
        prompt = f"""
        Provide detailed internet connectivity information for {location} for a {duration}-day stay.
        {f'Work requirements: {", ".join(work_requirements)}' if work_requirements else ''}
        Include public WiFi spots, recommended providers, and connectivity tips.
        """

        input_data = OpenAIParserInput(
            user_input=prompt,
            system_prompt="You are a connectivity expert. Provide detailed internet availability information.",
            response_model=InternetAvailability,
            model=self.model,
            temperature=self.temperature,
        )

        result = self.process(input_data)
        return result.parsed_response


class FoodAgent(TravelAgentBase):
    """Agent for food recommendations"""

    def get_food_recommendations(
        self,
        location: str,
        dietary_restrictions: Optional[List[str]] = None,
        preferences: Optional[List[str]] = None,
        budget_level: str = "medium",
    ) -> FoodOption:
        prompt = f"""
        Provide food recommendations for {location}.
        {f'Dietary restrictions: {", ".join(dietary_restrictions)}' if dietary_restrictions else ''}
        {f'Food preferences: {", ".join(preferences)}' if preferences else ''}
        Budget level: {budget_level}
        Include local specialties, restaurant recommendations, and food safety tips.
        """

        input_data = OpenAIParserInput(
            user_input=prompt,
            system_prompt="You are a culinary expert. Provide detailed food recommendations.",
            response_model=FoodOption,
            model=self.model,
            temperature=self.temperature,
        )

        result = self.process(input_data)
        return result.parsed_response


class PersonalizedAgent(TravelAgentBase):
    """Agent for personalized travel recommendations"""

    def get_personalized_recommendations(
        self,
        location: str,
        duration: int,
        interests: List[str],
        budget_level: str,
        travel_style: str,
        previous_destinations: Optional[List[str]] = None,
    ) -> PersonalizedRecommendation:
        prompt = f"""
        Create personalized travel recommendations for {location} for {duration} days.
        Interests: {', '.join(interests)}
        Travel style: {travel_style}
        Budget level: {budget_level}
        {f'Previous destinations: {", ".join(previous_destinations)}' if previous_destinations else ''}
        Include hidden gems, local events, and a custom itinerary.
        """

        input_data = OpenAIParserInput(
            user_input=prompt,
            system_prompt="You are a personal travel consultant. Provide tailored recommendations.",
            response_model=PersonalizedRecommendation,
            model=self.model,
            temperature=self.temperature,
        )

        result = self.process(input_data)
        return result.parsed_response


# Similar pattern for other agents...

if __name__ == "__main__":
    # Initialize all agents
    clothing_agent = ClothingAgent()
    hiking_agent = HikingAgent()
    internet_agent = InternetAgent()
    food_agent = FoodAgent()
    personalized_agent = PersonalizedAgent()

    # Example location and common parameters
    location = "Kyoto, Japan"
    duration = 7
    season = "spring"

    try:
        # Get clothing recommendations
        clothing_result = clothing_agent.get_recommendations(
            location=location,
            duration=duration,
            activities=["hiking", "temple visits", "city walking", "photography"],
            season=season,
        )
        print("\n=== Clothing Recommendations ===")
        print(f"Essential items: {', '.join(clothing_result.essential_items)}")
        print(f"Weather specific: {', '.join(clothing_result.weather_specific)}")
        print(
            f"Cultural considerations: {', '.join(clothing_result.cultural_considerations)}"
        )

        # Get hiking options
        hiking_result = hiking_agent.get_hiking_options(
            location=location, difficulty="moderate", duration_preference=4.0
        )
        print("\n=== Hiking Options ===")
        for trail in hiking_result:
            print(f"\nTrail: {trail.trail_name}")
            print(f"Difficulty: {trail.difficulty}")
            print(f"Duration: {trail.duration_hours} hours")
            print(f"Distance: {trail.distance_km} km")

        # Get internet availability
        internet_result = internet_agent.get_connectivity_info(
            location=location,
            duration=duration,
            work_requirements=["video calls", "cloud storage access"],
        )
        print("\n=== Internet Availability ===")
        print(f"General availability: {internet_result.general_availability}")
        print(f"Average speed: {internet_result.average_speed_mbps} Mbps")
        print(
            f"Recommended providers: {', '.join(internet_result.recommended_providers)}"
        )

        # Get food recommendations
        food_result = food_agent.get_food_recommendations(
            location=location,
            dietary_restrictions=["vegetarian"],
            preferences=["traditional", "local specialties"],
            budget_level="medium",
        )
        print("\n=== Food Recommendations ===")
        print("Local specialties:", ", ".join(food_result.local_specialties))
        print("Must-try dishes:", ", ".join(food_result.must_try_dishes))
        for restaurant in food_result.recommended_restaurants[:3]:  # Show top 3
            print(f"Restaurant: {restaurant['name']} - {restaurant['type']}")

        # Get personalized recommendations
        personal_result = personalized_agent.get_personalized_recommendations(
            location=location,
            duration=duration,
            interests=["photography", "culture", "nature", "food"],
            budget_level="medium",
            travel_style="balanced",
            previous_destinations=["Tokyo", "Seoul"],
        )
        print("\n=== Personalized Recommendations ===")
        print("Hidden gems:", ", ".join(personal_result.hidden_gems))
        print("\nCustom Itinerary:")
        for day in personal_result.custom_itinerary:
            print(f"Day {day['day']}: {day['activities']}")

    except ProcessingError as e:
        print(f"Error processing travel recommendations: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
