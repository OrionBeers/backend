class PredictPlantingDate:
    def __init__(self, user_id: str):
        self.user_id = user_id

    def execute(self):
        print(f"[PredictPlantingDate worker] start: {self.user_id}")
        # TODO: Implement prediction
        # TODO: Save prediction result to database
        print("[PredictPlantingDate worker] done")