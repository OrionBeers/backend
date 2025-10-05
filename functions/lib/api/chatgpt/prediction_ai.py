"""
DATASET

# | ID          | description                   |
# | ----------- | ----------------------------- |
# | T2M_MAX        | Temperature at 2 Meters Maximum |
# | T2M_MIN        | Temperature at 2 Meters Minimum |
# | RH2M        | Relative Humidity at 2 Meters |
# | PRECTOTCORR | Precipitation Corrected       |
# | GWETROOT    | Root Zone Soil Wetness        |
# | GWETTOP     | Surface Soil Wetness          |
# | PRECSNO     | Snow Precipitation            |
# | TSOIL5      | Soil Temperatures Layer       |
"""

# prediction_ai.py
from __future__ import annotations

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from openai import OpenAI
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import Choice
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DebugInfo:
    """Container for debug information about the API call"""
    request_id: str
    timestamp: str
    input_year: str
    model: str
    response_time: float
    raw_response: Optional[ChatCompletion] = None
    error: Optional[str] = None
    parse_error: Optional[str] = None
    validation_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert debug info to a dictionary for logging"""
        return {
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "input_year": self.input_year,
            "model": self.model,
            "response_time": f"{self.response_time:.2f}s",
            "error": self.error,
            "parse_error": self.parse_error,
            "validation_error": self.validation_error,
            "has_response": self.raw_response is not None,
            "response_choices": len(self.raw_response.choices) if self.raw_response else 0
        }

def validate_response(response: ChatCompletion, debug: DebugInfo) -> Tuple[Optional[Choice], bool]:
    """Validate the OpenAI response"""
    if not response:
        debug.validation_error = "Empty response received"
        return None, False
        
    if not response.choices:
        debug.validation_error = "No choices in response"
        return None, False
        
    choice = response.choices[0]
    if not choice.message:
        debug.validation_error = "No message in first choice"
        return None, False
        
    return choice, True


# ---------- Output schema (exactly your format) ----------

class PredictedData(BaseModel):
    # status: 0.0 (not suitable) .. 1.0 (perfect)
    status: float
    moisture: float
    temperature: float
    precipitation: float
    snow_precipitation: float
    soil_temperature: float
    humidity: float


class ForecastEntry(BaseModel):
    # "YYYYMMDD" as string (as in your examples)
    date: str
    prediction_data: PredictedData


class ForecastResponse(BaseModel):
    forecast: list[ForecastEntry]


# ---------- Public API ----------

def get_month_forecast_array(
  current_year: str,            # "YYYY"
  dataset_nasa: dict,   # NASA POWER-style JSON
  best_conditions: dict,  # best condition JSON for the crop
) -> Optional[list[ForecastEntry]]:
    """
    Returns the parsed `forecast` list from the OpenAI response.
    """
    # Initialize debug info
    debug = DebugInfo(
        request_id=f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        timestamp=datetime.now().isoformat(),
        input_year=current_year,
        model="gpt-4",  # Fixed model name
        response_time=0.0
    )

    try:
        openai_api_key = os.getenv("OPEN_AI_API_KEY")
        if not openai_api_key:
            raise ValueError("Set OPEN_AI_API_KEY or pass api_key.")

        client = OpenAI(api_key=openai_api_key)

        system_prompt = "You are a meteorological prediction assistant specialized in NASA POWER datasets."
        user_prompt = build_user_prompt(
            current_year=current_year, dataset_nasa=dataset_nasa, best_condition=best_conditions
        )

        logger.info(f"Starting API request {debug.request_id}")
        start_time = datetime.now()

        try:
            response = client.chat.completions.create(  # Changed to create from parse
                model="gpt-4",  # Fixed model name
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=4000,
                response_format={ "type": "json_object" }  # Specify JSON response
            )
        except Exception as api_error:
            debug.error = f"API Error: {str(api_error)}"
            logger.error(f"API call failed for {debug.request_id}: {debug.error}")
            return None

        debug.response_time = (datetime.now() - start_time).total_seconds()
        debug.raw_response = response

        # Validate response structure
        choice, is_valid = validate_response(response, debug)
        if not is_valid:
            logger.error(f"Response validation failed for {debug.request_id}: {debug.validation_error}")
            return None

        # Parse the response content
        try:
            # First, parse the raw JSON string
            content = choice.message.content
            if not content:
                debug.parse_error = "Empty message content"
                logger.error(f"Empty content in response for {debug.request_id}")
                return None

            # Try to parse the JSON string
            try:
                raw_json = json.loads(content)
            except json.JSONDecodeError as e:
                debug.parse_error = f"JSON decode error: {str(e)}"
                logger.error(f"JSON parsing failed for {debug.request_id}: {debug.parse_error}")
                logger.error(f"Raw content: {content[:200]}...")  # Log first 200 chars
                return None

            # Validate against our model
            parsed = ForecastResponse.model_validate(raw_json)
            if not parsed or not parsed.forecast:
                debug.validation_error = "Empty forecast after parsing"
                logger.error(f"Empty forecast for {debug.request_id}")
                return None

            # Log success
            logger.info(f"Successfully processed request {debug.request_id}")
            logger.debug(f"Debug info: {json.dumps(debug.to_dict(), indent=2)}")
            
            return parsed.forecast

        except Exception as parse_error:
            debug.parse_error = f"Parse error: {str(parse_error)}"
            logger.error(f"Parsing failed for {debug.request_id}: {debug.parse_error}")
            return None

    except Exception as e:
        debug.error = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error in {debug.request_id}: {debug.error}")
        return None


# ---------- Prompt builder (your prompt verbatim) ----------

def build_user_prompt(current_year: str, dataset_nasa: dict, best_condition: dict) -> str:
    # English prompt: produce predictions from NASA data and compute a status comparing predictions to best_condition
    return f"""
You are an expert agronomist and data scientist. You will receive two JSON inputs: `best_condition` (optimal values for a crop) and `nasa_data` (historical NASA POWER time series from past years). Your job is to:

1) Using the provided historical `nasa_data` as a reference, generate a daily climatological forecast for the requested month for the year {int(current_year) + 1}. The forecast should be based on patterns and trends observed in the historical data. For each day-of-month produce the following predicted values: moisture, temperature, precipitation, snow_precipitation, soil_temperature, humidity.

2) For each forecasted day, compute a numeric `status` between 0.00 and 1.00 that indicates how closely the predicted conditions match the provided `best_condition`. Insert `status` as the FIRST field inside `prediction_data`.

SCORING RULES (apply exactly):
- Temperature (°C): perfect if |pred - best| ≤ 2 → score = 1. Linear decay to 0 when |pred - best| = 10.
  score_temp = clamp(0, 1 - (|pred - best| - 2) / 8, 1)
- Humidity (%): convert percentages to 0..1 scale if necessary. Perfect if within ±5% (0.05) → score 1; linear decay to 0 at ±30%.
  score_hum = clamp(0, 1 - (|pred_h - best_h| - 0.05) / 0.25, 1)
- Root and top soil moisture (0..1): perfect if within ±0.05; decay to 0 at ±0.4.
  score_soil = clamp(0, 1 - (|pred - best| - 0.05) / 0.35, 1)
- Soil temperature: same as Temperature.
- Precipitation (mm/day): perfect if |pred - best| ≤ 1 mm; linear decay to 0 at 10 mm.
- Snow precipitation: if both pred and best are 0 → score 1; otherwise rapid decay.

WEIGHTS (sum = 1.0):
- root_soil_moisture: 0.30
- top_soil_moisture: 0.20
- temperature: 0.20
- soil_temperature: 0.10
- humidity: 0.10
- precipitation: 0.08
- snow_precipitation: 0.02

FINAL STATUS COMPUTATION:
- Compute per-variable scores as above, multiply each by its weight and sum. Round status to two decimals and clamp to [0.00, 1.00].

OUTPUT REQUIREMENTS:
- Return ONLY a JSON object with exactly one key `forecast`. Its value must be an array of entries shaped like below. Each numeric value must be rounded to two decimals.

{{
  "forecast": [
    {{
      "date": "YYYYMMDD",
      "prediction_data": {{
        "status": NN.NN,
        "moisture": NN.NN,
        "temperature": NN.NN,
        "precipitation": NN.NN,
        "snow_precipitation": NN.NN,
        "soil_temperature": NN.NN,
        "humidity": NN.NN
      }}
    }},
    ...
  ]
}}

ADDITIONAL RULES:
- If the requested month is not present in the dataset, return `{{"forecast": []}}` (no error text).
- Use deterministic outputs (temperature=0.0) and ensure valid JSON only.
- If you cannot compute numeric `status` for a day, return `status`: null (no extra fields).

INPUTS (for this run):
best_condition = {best_condition}
nasa_data = {dataset_nasa}

Now produce the requested JSON array following the rules above.
""".strip()
