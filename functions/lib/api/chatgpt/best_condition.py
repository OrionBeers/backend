import os
from typing import Dict, Any, Optional
from openai import OpenAI

from infrastructure.database.models.crop_condition_model import CropConditionModel


def get_crop_best_conditions(
    crop_key: str, api_key: Optional[str] = None
) -> Optional[CropConditionModel]:
    """
    Get optimal growing conditions for a specific crop using OpenAI API.

    Args:
        crop_key: The key identifier for the crop (e.g., "tomato", "lettuce")
        api_key: Optional OpenAI API key (uses environment variable if not provided)

    Returns:
        Dictionary containing AI-generated optimal conditions or None if error
    """
    try:
        # Initialize OpenAI client with API key from environment variable or parameter
        openai_api_key = api_key or os.getenv("OPEN_AI_API_KEY")
        if not openai_api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPEN_AI_API_KEY environment variable or pass api_key parameter."
            )

        client = OpenAI(api_key=openai_api_key)

        # Create optimized prompt for the crop focusing on transplanting/planting conditions
        prompt = f"""
        Provide optimal environmental conditions for {crop_key} at the initial planting/transplanting stage.
        
        Focus specifically on the best conditions needed during the first few weeks after planting or transplanting seedlings.
        This is the critical establishment period when plants are most vulnerable and need optimal conditions to develop strong root systems.
        
        Please provide the ideal conditions with precise numerical values in the following units:
        
        - crop_name: Simple common name (e.g., if input is "tomato", return "Tomato")
        - temperature: Air temperature in degrees Celsius (°C) - provide single optimal value
        - humidity: Relative humidity as percentage (%) - provide single optimal value  
        - root_soil_moisture: Root zone soil wetness as decimal (0.0-1.0, where 1.0 = fully saturated)
        - top_soil_moisture: Surface soil wetness as decimal (0.0-1.0, where 1.0 = fully saturated)
        - soil_temperature: Soil temperature in degrees Celsius (°C) - provide single optimal value
        - rain_precipitation: Daily rainfall in millimeters per day (mm/day) - provide single optimal value
        - snow_precipitation: Daily snowfall in millimeters per day (mm/day) - usually 0.0 for most crops
        
        Base your recommendations on:
        1. Scientific research on crop establishment phases
        2. Commercial transplanting best practices  
        3. Conditions that minimize transplant shock
        4. Early-stage growth requirements specific to {crop_key}
        
        Return realistic numerical values that farmers can use for monitoring and planning planting operations.
        Ensure all values are appropriate for the initial planting/transplanting period.
        """

        # Call OpenAI API
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert agricultural scientist and agronomist with extensive knowledge of crop cultivation requirements. Provide precise, science-based recommendations for optimal growing conditions. Your responses should be based on peer-reviewed research and established agricultural practices.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            response_format=CropConditionModel,
        )

        # Extract structured response
        crop_condition = response.choices[0].message.parsed

        if not crop_condition:
            return None

        # Override crop_key with original request value and return the Pydantic model
        crop_condition.crop_key = (
            crop_key  # Use original request crop_key instead of AI-generated one
        )

        return crop_condition

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None
