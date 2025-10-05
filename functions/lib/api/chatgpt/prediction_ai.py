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

from __future__ import annotations

import os
from typing import Optional

from openai import OpenAI
from pydantic import BaseModel


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
    predicted_data: PredictedData


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
    try:
        openai_api_key = os.getenv("OPEN_AI_API_KEY")
        
        if not openai_api_key:
            raise ValueError("Set OPEN_AI_API_KEY or pass api_key.")

        client = OpenAI(api_key=openai_api_key)

        system_prompt = "You are a meteorological prediction assistant specialized in NASA POWER datasets."
        user_prompt = build_user_prompt(
            current_year=current_year, dataset_nasa=dataset_nasa, best_conditions=best_conditions
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=4000,
            response_format={"type": "json_object"},
            temperature=0.0  # For consistent outputs
        )

        content = response.choices[0].message.content
        if not content:
            return None
            
        try:
            parsed = ForecastResponse.model_validate_json(content)
            return parsed.forecast
        except Exception as e:
            print(f"Error parsing response JSON: {e}")
            return None

    except Exception as e:
        print(f"Error calling OpenAI API (forecast array): {e}")
        return None


# ---------- Prompt builder (your prompt verbatim) ----------

def build_user_prompt(current_year: str, dataset_nasa: dict, best_conditions: dict) -> str:
    # English prompt: produce predictions from NASA data and compute a status comparing predictions to best_condition
    return f"""
You are an expert agronomist and data scientist. You will receive two JSON inputs: `best_condition` (optimal values for a crop) and `nasa_data` (historical NASA POWER time series from past years). Your job is to:

1) Using the provided historical `nasa_data` as a reference, generate a daily climatological forecast for the requested month for the year {int(current_year) + 1}. The forecast should be based on patterns and trends observed in the historical data. For each day-of-month produce the following predicted values: moisture, temperature, precipitation, snow_precipitation, soil_temperature, humidity.

2) For each forecasted day, compute a numeric `status` between 0.00 and 1.00 that indicates how closely the predicted conditions match the provided `best_condition`. Insert `status` as the FIRST field inside `predicted_data`.

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
      "predicted_data": {{
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
- Use deterministic outputs (temperature=0.0) and ensure valid JSON only.
- If you cannot compute numeric `status` for a day, return `status`: null (no extra fields).

INPUTS (for this run):
current_year = {current_year}
best_condition = {best_conditions}
nasa_data = {dataset_nasa}

Now produce the requested JSON array following the rules above.
""".strip()
