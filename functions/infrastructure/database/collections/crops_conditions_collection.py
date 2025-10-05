from infrastructure.database.models.user_model import UsersModel
from infrastructure.database.interface.collection_interface import CollectionInterface
from infrastructure.database.models.crop_condition_model import CropConditionModel



class CropsConditionCollection(CollectionInterface):

    collection_name = 'crops'
    entity_reference = CropConditionModel