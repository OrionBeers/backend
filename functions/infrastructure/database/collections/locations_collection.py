from infrastructure.database.interface.collection_interface import CollectionInterface
from infrastructure.database.models.location_model import LocationModel


class LocationsCollection(CollectionInterface):
    collection_name = "locations"
    entity_reference = LocationModel
