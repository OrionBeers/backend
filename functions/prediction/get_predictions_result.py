from infrastructure.database.collections.dashboard_collection import DashboardCollection
from infrastructure.database.collections.historical_data_collection import HistoricalDataCollection
from datetime import datetime

from infrastructure.database.models.dashboard_data_model import DashboardDataModel


class GetPredictionsResult:
    def __init__(self, id_user: str, id_request: str):
        self.id_user = id_user
        self.id_request = id_request

    def execute(self):
        try:
            user_predictions_by_id = HistoricalDataCollection().list(filter_by={"id_user": self.id_user,
                                                                          "id_request": self.id_request},
                                                                     hidden_fields=[],
                                                                     force_show_fields=[])
            if not user_predictions_by_id:
                raise Exception("No predictions found for the given user ID and request ID.")

            normalized_data = self._normalize_data(user_predictions_by_id)

            start_date_formatted = self._format_date_month_year(normalized_data.get('start_date'))
            end_date_formatted = self._format_date_month_year(normalized_data.get('end_date'))

            final_data = {
                "id_user": normalized_data.get('id_user', ''),
                "date_range": {
                    "start_date": start_date_formatted,
                    "end_date": end_date_formatted
                },
                "crop": normalized_data.get('crop_types', 'crop'),
                "calendar": normalized_data.get('normalized_timestamps', {}).get('calendar', []),
            }


            dashboard_id =  self._save_prediction(final_data)

            return {"_id":dashboard_id, "data":{final_data}}

        except Exception as e:
            raise Exception(f"Error retrieving predictions: {str(e)}")

    @staticmethod
    def _format_date_month_year(date):
        if not date:
            return ""

        if isinstance(date, str):
            try:
                date = datetime.fromisoformat(date)
            except (ValueError, TypeError):
                return date

        if isinstance(date, datetime):
            month_abbr = {
                1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
                5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
                9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
            }


            return f"{month_abbr[date.month]} - {date.year}"

        return str(date)

    @staticmethod
    def _normalize_data(data):
        month_names = {
            "01": "janeiro", "02": "fevereiro", "03": "março",
            "04": "abril", "05": "maio", "06": "junho",
            "07": "julho", "08": "agosto", "09": "setembro",
            "10": "outubro", "11": "novembro", "12": "dezembro"
        }

        all_timestamps = []

        for item in data:
            all_timestamps.extend(item.get('timestamps', []))

        if data:
            first_item = data[0]
            normalized_data = {
                "_id": first_item.get('_id'),
                "id_user": first_item.get('id_user'),
                "id_request": first_item.get('id_request'),
                "latitude": first_item.get('latitude'),
                "longitude": first_item.get('longitude'),
                "start_date": first_item.get('start_date'),
                "end_date": first_item.get('end_date'),
                "crop_types": first_item.get('crop_types'),
                "best_condition": first_item.get('best_condition'),
                "step_block": first_item.get('step_block'),
                "created_at": first_item.get('created_at'),
                "updated_at": first_item.get('updated_at'),
                "normalized_timestamps": {
                    "calendar": {}
                }
            }

            for ts_data in all_timestamps:
                date_str = ts_data.get('date')

                if date_str:
                    if isinstance(date_str, datetime):

                        date_str = date_str.strftime("%Y%m%d")
                    else:

                        date_str = str(date_str)

                    if len(date_str) == 8:
                        year = date_str[:4]
                        month = date_str[4:6]
                        day = date_str[6:]

                        month_name = month_names.get(month, f"mês{month}")

                        timestamp_entry = {
                            "date": date_str,
                            "status": ts_data.get('status'),
                            "prediction_data": ts_data.get('prediction_data', {})
                        }

                        if month_name not in normalized_data["normalized_timestamps"]['calendar']:
                            normalized_data["normalized_timestamps"]['calendar'][month_name] = []

                        normalized_data["normalized_timestamps"]['calendar'][month_name].append(timestamp_entry)

            return normalized_data
        else:
            return {}

    @staticmethod
    def _save_prediction(prediction):
        try:
            data_to_insert = DashboardDataModel(**prediction)
            dashboard_id = DashboardCollection().insert(data_to_insert)
            return dashboard_id
        except Exception as e:
            raise Exception(f"Error saving prediction: {str(e)}")