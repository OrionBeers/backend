from infrastructure.database.interface.collection_interface import CollectionInterface
from infrastructure.database.models.request_model import RequestModel


class RequestCollection(CollectionInterface):
    collection_name = "requests"
    entity_reference = RequestModel