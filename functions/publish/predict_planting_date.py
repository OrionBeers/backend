import datetime
import json
import logging
import requests

from infrastructure.database.collections.crops_conditions_collection import CropsConditionCollection
from infrastructure.database.models.crop_condition_model import CropConditionModel
from lib.api.chatgpt.best_condition import get_crop_best_conditions
from lib.api.chatgpt.prediction_ai import get_month_forecast_array

from copy import deepcopy


class PredictPlantingDate:
    def __init__(self, id_user: str, data: dict):
        self.id_user = id_user
        self.request = data

    def execute(self):
        crop = self.request["crop_type"]

        print(f"[PredictPlantingDate worker] start: {self.id_user} with crop: {crop}")
        try:
            crop_id, best_conditions = self._validate_crop_in_db(crop=crop)
            print(f"[PredictPlantingDate worker] crop_id: {crop_id}")

            location_data = {
                "latitude": self.request["latitude"],
                "longitude": self.request["longitude"]
            }

            current_date = datetime.datetime.now()
            start_year = current_date.year - 6
            end_year = current_date.year - 1

            date_range = {
                "start_date": f"{start_year}0101",  # January 1st, 5 years ago
                "end_date": f"{end_year}1231"       # December 31st of last year
            }

            print(f"[PredictPlantingDate worker] Fetching data from {date_range['start_date']} to {date_range['end_date']} for location: {location_data}")

            self._make_prediction(best_conditions=best_conditions,
                                  location_data=location_data,
                                  date_range=date_range,
                                  start_month=self.request["start_month"])

        except Exception as e:
            print(f"[PredictPlantingDate worker] Error: {e}")
            return

        # TODO: Save prediction result to database
        print("[PredictPlantingDate worker] done")

    @staticmethod
    def _validate_crop_in_db(crop: str):
        logging.info(f"[PredictPlantingDate worker] Validating crop in DB: {crop}")

        existing_crop = CropsConditionCollection().get_one(filter_by={"crop_key": crop},hidden_fields=[], force_show_fields=[])
        if existing_crop:
            logging.info(f"[PredictPlantingDate worker] Crop already exists: {crop} with ID: {existing_crop['_id']}")
            return existing_crop["_id"], existing_crop

        else:
            logging.info(f"[PredictPlantingDate worker] Crop does not exist, fetching best conditions for: {crop}")

            best_conditions = get_crop_best_conditions(crop_key=crop)

            logging.info(f"[PredictPlantingDate worker] best_conditions: {best_conditions}")

            if not best_conditions:
                raise Exception(f"[PredictPlantingDate worker] No best conditions found")

            data_to_insert = {
                "crop_key": best_conditions.crop_key,
                "crop_name": best_conditions.crop_name,
                "temperature": best_conditions.temperature,
                "humidity": best_conditions.humidity,
                "root_soil_moisture": best_conditions.root_soil_moisture,
                "top_soil_moisture": best_conditions.top_soil_moisture,
                "soil_temperature": best_conditions.soil_temperature,
                "snow_precipitation": best_conditions.snow_precipitation,
                "rain_precipitation": best_conditions.rain_precipitation,
            }

            crop_id = CropsConditionCollection().insert(CropConditionModel(**data_to_insert))

            return crop_id.inserted_id, best_conditions

    @staticmethod
    def _real_time_database_update():
        pass

    def _make_prediction(self, best_conditions: CropConditionModel, location_data: dict,
                         date_range: dict, start_month: str):
        try:
            nasa_data = self._get_nasa_data(location_data=location_data, data_range=date_range)

            filtered_data = self._filter_dataset_by_month(nasa_data, start_month)

            if not nasa_data:
                raise Exception("[PredictPlantingDate worker] No NASA data found for the given location and date range")


            logging.info("Starting prediction using NASA data and best conditions")
            current_date = datetime.datetime.now()

            result = get_month_forecast_array(best_conditions=best_conditions,
                                              current_year=current_date.year, dataset_nasa=filtered_data)

            payload = [entry.model_dump() for entry in result]
            print(json.dumps(payload, indent=2, ensure_ascii=False))

            if not result:
                raise Exception("[PredictPlantingDate worker] Prediction API returned no data")

            return result


        except Exception as e:
            print(f"[PredictPlantingDate worker] Error making prediction: {e}")
            return None



    @staticmethod
    def _get_nasa_data(location_data:dict, data_range:dict):
        try:
            base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
            params = {
                "parameters": "T2M_MAX,T2M_MIN,RH2M,PRECTOTCORR,GWETROOT,GWETTOP,PRECSNO,TSOIL5",
                "community": "re",
                "longitude": location_data["longitude"],
                "latitude": location_data["latitude"],
                "start": data_range["start_date"],
                "end": data_range["end_date"],
                "format": "json",
                "units": "metric",
                "header": "true"
            }
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[PredictPlantingDate worker] Error fetching NASA data: {e}")
            return None

    @staticmethod
    def _filter_dataset_by_month(dataset: dict, month: str) -> dict:
        month_map = {
            'January': '01', 'February': '02', 'March': '03', 'April': '04',
            'May': '05', 'June': '06', 'July': '07', 'August': '08',
            'September': '09', 'October': '10', 'November': '11', 'December': '12'
        }

        # Get the month number
        if month not in month_map:
            logging.error(f"[PredictPlantingDate worker] Invalid month: {month}")
            return {}

        month_number = month_map[month]

        filtered_dataset = deepcopy(dataset)


        if 'properties' not in dataset or 'parameter' not in dataset['properties']:
            logging.error("[PredictPlantingDate worker] Dataset does not have the expected structure")
            return {}

        for param_name, param_data in filtered_dataset['properties']['parameter'].items():
            filtered_dates = {}

            for date_key, value in param_data.items():
                if len(date_key) == 8 and date_key[4:6] == month_number:
                    filtered_dates[date_key] = value

            filtered_dataset['properties']['parameter'][param_name] = filtered_dates

        return filtered_dataset
