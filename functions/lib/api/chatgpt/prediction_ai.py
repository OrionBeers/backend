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
from pydantic import BaseModel, RootModel


# ---------- Output schema (exactly your format) ----------

class PredictedData(BaseModel):
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


class ForecastArray(RootModel[List[ForecastEntry]]):
    """Root is a JSON array (no wrapper)."""
    root: List[ForecastEntry]


# ---------- Public API ----------

def get_month_forecast_array(
    *,
    month: str,           # "01".."12"
    year: str,            # "YYYY"
    dataset_json: dict,   # NASA POWER-style JSON
    api_key: Optional[str] = None,
) -> Optional[ForecastArray]:
    """
    Returns a JSON array of entries:
    [
      {
        "date": "YYYYMMDD",
        "prediction_data": {
          "moisture": NN.NN,
          "temperature": NN.NN,
          "precipitation": NN.NN,
          "snow_precipitation": NN.NN,
          "soil_temperature": NN.NN,
          "humidity": NN.NN
        }
      },
      ...
    ]
    """
    try:
        openai_api_key = api_key or os.getenv("OPEN_AI_API_KEY")
        if not openai_api_key:
            raise ValueError("Set OPEN_AI_API_KEY or pass api_key.")

        client = OpenAI(api_key=openai_api_key)

        system_prompt = "You are a meteorological prediction assistant specialized in NASA POWER datasets."
        user_prompt = build_user_prompt(month=month, year=year, dataset_json=dataset_json)

        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=3000,
            response_format=ForecastArray,  # parse directly into list[ForecastEntry]
        )

        parsed = response.choices[0].message.parsed
        return parsed if parsed else None

    except Exception as e:
        print(f"Error calling OpenAI API (forecast array): {e}")
        return None


# ---------- Prompt builder (your prompt verbatim) ----------

def build_user_prompt(*, month: str, year: str, dataset_json: dict) -> str:
    return f"""
You are a meteorological prediction assistant specialized in NASA POWER datasets.

DATA STRUCTURE
The dataset follows this structure:
{{
  "properties": {{
    "parameter": {{
      "T2M_MAX": {{ "20190101": 32.04, ... }},
      "T2M_MIN": {{ "20190101": 19.31, ... }},
      "RH2M": {{ "20190101": 75.22, ... }},
      "PRECTOTCORR": {{ "20190101": 3.34, ... }},
      "GWETROOT": {{ "20190101": 0.64, ... }},
      "GWETTOP": {{ "20190101": 0.62, ... }},
      "PRECSNO": {{ "20190101": 0.00, ... }},
      "TSOIL5": {{ "20190101": 20.82, ... }}
    }}
  }}
}}

TASK
Using the provided dataset (about 5 recent years of data), generate a **daily climatological forecast** for the requested month and for the **next calendar year (year + 1)**.

METHOD
1. Select all daily entries from `properties.parameter` where the date (YYYYMMDD) corresponds to the requested month (MM).
2. For each day-of-month (01–31), calculate the mean of each variable across all available years.
   - temperature = mean of ((T2M_MAX + T2M_MIN) / 2)
   - precipitation = mean of PRECTOTCORR
   - snow_precipitation = mean of PRECSNO
   - soil_temperature = mean of TSOIL5
   - humidity = mean(RH2M) / 100  (convert % to a 0–1 scale)
   - moisture = mean of (0.5 × (GWETROOT + GWETTOP))
3. Handle missing data:
   - If some years lack a value for a given day, average only available data.
   - If a day is missing entirely, use the mean of the whole month for that variable.
4. Round all numeric outputs to two decimals.
5. The forecasted dates must correspond to the **next year (YYYY + 1)** for the same month.
6. Output only numeric values — no units or text.

OUTPUT FORMAT
Return only a valid JSON array with this exact structure:

[
  {{
    "date": "YYYYMMDD",
    "prediction_data": {{
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

RULES
- No markdown, no extra text — JSON array only.
- Round to two decimals.
- If the requested month is not present in the dataset, return an empty array [].
- Always forecast for next calendar year (input year + 1).

INPUT EXAMPLE
{{
  "month": "01",
  "year": "2025",
  "data": {{ ... NASA POWER JSON ... }}
}}

OUTPUT EXAMPLE
[
  {{
    "date": "20260101",
    "prediction_data": {{
      "moisture": 0.63,
      "temperature": 25.45,
      "precipitation": 3.18,
      "snow_precipitation": 0.00,
      "soil_temperature": 20.82,
      "humidity": 0.75
    }}
  }},
  {{
    "date": "20260102",
    "prediction_data": {{
      "moisture": 0.61,
      "temperature": 25.20,
      "precipitation": 2.87,
      "snow_precipitation": 0.00,
      "soil_temperature": 20.70,
      "humidity": 0.74
    }}
  }}
]

ACTUAL INPUT
{{
  "month": "{month}",
  "year": "{year}",
  "data": {dataset_json}
}}
""".strip()