from infrastructure.database.models.dashboard_data_model import DashboardDataModel
from infrastructure.database.interface.collection_interface import CollectionInterface

class DashboardCollection(CollectionInterface):
    collection_name = 'dashboard_data'
    entity_reference = DashboardDataModel