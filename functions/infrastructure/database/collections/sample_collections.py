
from infrastructure.database.interface.collection_interface import CollectionInterface
from infrastructure.database.models.sample_model import SampleModel


class SampleCollection(CollectionInterface):

    collection_name = 'sample_collection'
    entity_reference = SampleModel