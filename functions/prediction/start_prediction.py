
class StartPrediction:
    def __init__(self, id_user: str):
        self.id_user = id_user

    def start(self):

        predictions = self.model.predict(self.data)
        return predictions