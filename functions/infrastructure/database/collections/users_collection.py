from infrastructure.database.models.user_model import UsersModel
from infrastructure.database.interface.collection_interface import CollectionInterface

class UsersCollection(CollectionInterface):
    collection_name = 'users'
    entity_reference = UsersModel