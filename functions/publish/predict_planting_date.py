import os

from infrastructure.database.collections.crops_conditions_collection import CropsConditionCollection
from infrastructure.database.models.crop_condition_model import CropConditionModel
from lib.api.chatgpt.best_condition import get_crop_best_conditions


class PredictPlantingDate:
    def __init__(self, id_user: str, data: dict):
        self.id_user = id_user
        self.request = data

    def execute(self):
        print(f"[PredictPlantingDate worker] start: {self.id_user}")
        print(self.request)
        crop = self.request["crop"]

        try:
            best_conditions = get_crop_best_conditions(crop)
            print(f"[PredictPlantingDate worker] best_conditions: {best_conditions}")

            if not best_conditions:
                raise Exception(f"[PredictPlantingDate worker] No best conditions found")

            # Save best conditions to database
            crop_id = CropsConditionCollection().insert(CropConditionModel(**best_conditions))
            print(f"[PredictPlantingDate worker] crop_id: {crop_id}")




        except Exception as e:
            print(f"[PredictPlantingDate worker] Error: {e}")
            return




        # TODO: Implement prediction
        # TODO: Save prediction result to database
        print("[PredictPlantingDate worker] done")
