from infrastructure.database.interface.collection_interface import CollectionInterface
from infrastructure.database.models.historical_data_model import HistoricalDataModel


class HistoricalDataCollection(CollectionInterface):
    collection_name = "historical_data"
    entity_reference = HistoricalDataModel