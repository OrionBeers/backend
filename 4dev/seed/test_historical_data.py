from datetime import datetime, timedelta
from bson.objectid import ObjectId
from functions.infrastructure.database.models.historical_data_model import HistoricalDataModel
from functions.infrastructure.database.collections.historical_data_collection import HistoricalDataCollection
from functions.prediction.get_predictions_result import GetPredictionsResult

def test_normalization():
    """Testa a função de normalização"""
    # Obtém os dados normalizados
    normalizer = GetPredictionsResult(id_user="68e1b151d4c84c71068b5064", id_request="123456789")
    normalized_data = normalizer.execute()

    # Imprime os dados normalizados
    print("\nDados Normalizados:")
    print(f"ID Request: {normalized_data.get('id_request')}")
    print(f"Step Block: {normalized_data.get('step_block')}")

    timestamps = normalized_data.get('normalized_timestamps', {})

    print(timestamps)

if __name__ == "__main__":
    print("\nTestando normalização...")
    test_normalization()
