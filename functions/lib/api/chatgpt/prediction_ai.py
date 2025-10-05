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
from typing import Optional, List

from openai import OpenAI
from pydantic import BaseModel, RootModel, field_validator


# ---------- Output Schema (matches the prompt specification) ----------

class PredictedData(BaseModel):
    moisture: float        # numeric value (no %)
    temperature: float     # numeric value (no °C)
    precipitation: float   # numeric value (no mm)

    @field_validator("moisture", "temperature", "precipitation")
    @classmethod
    def _round_2(cls, v: float) -> float:
        # Round all numeric outputs to two decimals
        return round(float(v), 2)


class ForecastEntry(BaseModel):
    # date must be a string in format "YYYYMMDD"
    date: str
    prediction_data: PredictedData

    @field_validator("date")
    @classmethod
    def _date_yyyymmdd(cls, v: str) -> str:
        # Simple validation for correct date format
        if len(v) != 8 or not v.isdigit():
            raise ValueError("date must be a string in 'YYYYMMDD' format")
        return v


class ForecastArray(RootModel[List[ForecastEntry]]):
    """The root model is a JSON array (no wrapper object)."""
    root: List[ForecastEntry]


# ---------- Public API ----------

def get_month_forecast_array(
    *,
    month: str,           # "01".."12"
    year: str,            # "YYYY"
    dataset_json: dict,   # NASA POWER-like JSON
    api_key: Optional[str] = None,
) -> Optional[ForecastArray]:
    """
    Returns a forecast array in the format:
    [
      {
        "date": "YYYYMMDD",
        "prediction_data": {
          "moisture": NN.NN,
          "temperature": NN.NN,
          "precipitation": NN.NN
        }
      },
      ...
    ]
    """
    try:
        openai_api_key = api_key or os.getenv("OPEN_AI_API_KEY")
        if not openai_api_key:
            raise ValueError("Set OPEN_AI_API_KEY environment variable or pass api_key.")

        client = OpenAI(api_key=openai_api_key)

        system_prompt = "You are a meteorological prediction assistant."

        # --- Main prompt from user (cleaned and formatted) ---
        user_prompt = f"""
You are a meteorological prediction assistant. 
Use a NASA POWER-style JSON dataset with daily parameters under `properties.parameter`:
- T2M_MAX — Temperature at 2 meters (maximum)
- T2M_MIN — Temperature at 2 meters (minimum)
- RH2M — Relative Humidity at 2 meters (%)
- PRECTOTCORR — Corrected daily precipitation (mm/day)

TASK
Using the provided dataset (containing roughly 5 recent years of data), 
generate a **daily climatological forecast** for the requested future month in the **next calendar year (year + 1)**.

ALGORITHM
1. Identify all records for the requested month (MM) across all available years.
2. Compute the mean for each day-of-month (01–31) across years.
   - Temperature: if both `T2M_MAX` and `T2M_MIN` exist, use the mean of both: `(T2M_MAX + T2M_MIN) / 2`.
   - Moisture: use the mean of `RH2M`.
   - Precipitation: use the mean of `PRECTOTCORR`.
3. Round all numeric outputs to two decimals.
4. If data for a specific day is missing in some years, use the mean of available data.
5. Output only numeric values — no units and no explanatory text.
6. The forecast must always be for **next calendar year (YYYY + 1)**.

OUTPUT FORMAT
Return only a valid JSON array (no text outside it) in this exact structure:

[
  {{
    "date": "YYYYMMDD",
    "prediction_data": {{
      "moisture": NN.NN,
      "temperature": NN.NN,
      "precipitation": NN.NN
    }}
  }},
  ...
]

CONSTRAINTS
- No text, no markdown, no explanations outside the JSON array.
- Values are purely numeric (no °C, %, or mm).
- If the requested month does not exist in the dataset, return:
  []
- Always return one entry per day of the requested month.

INPUT EXAMPLE
{{
  "month": "{month}",
  "year": "{year}",
  "data": {{ ... NASA POWER JSON ... }}
}}

INPUT (actual dataset follows):
{{
  "month": "{month}",
  "year": "{year}",
  "data": {dataset_json}
}}
""".strip()

        # Send the request to OpenAI using structured parsing
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=2500,
            response_format=ForecastArray,   # Parse directly into a list of ForecastEntry
        )

        parsed = response.choices[0].message.parsed
        return parsed if parsed else None

    except Exception as e:
        print(f"Error calling OpenAI API (forecast array): {e}")
        return None