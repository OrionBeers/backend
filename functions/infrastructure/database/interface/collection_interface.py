import json
from datetime import datetime

from infrastructure.database import database
from infrastructure.database.exceptions import NoChangesMade
from infrastructure.database.interface.model_interface import ModelInterface

database_connection = database.connect()

class CollectionInterface:
    collection_name = None
    entity_reference: ModelInterface = None
    hidden_fields = []

    def __init__(self):

        if self.collection_name is None:
            raise Exception('Interface parameter _collection_name is None. Please set a valid name')

        self._collection = database_connection[self.collection_name]

    def insert(self, entity: ModelInterface):
        return self._collection.insert_one(entity.model_dump(by_alias=True))

    def update(self, filter_by: dict, data_to_update: dict):

        for key, value in data_to_update.items():
            if "$" in key:
                result = self._collection.update_one(filter_by, data_to_update)
                if result.modified_count == 0:
                    raise NoChangesMade(f'No changes made in update for repository {self.collection_name}')
                return

        fields_to_not_update = self.entity_reference.list_fields_to_not_update()

        data_to_update['updated_at'] = datetime.now()

        for item in fields_to_not_update:
            data_to_update.pop(item, None)

        data_flatten = self._flatten_json(data_to_update)

        result = self._collection.update_one(filter_by, {"$set": data_flatten})

        if result.modified_count == 0:
            raise NoChangesMade(f'No changes made in update for repository {self.collection_name}')

    def delete(self, filter_by: dict):
        result = self._collection.delete_one(filter_by)

        if result.deleted_count == 0:
            raise NoChangesMade(f'No documents deleted from repository {self.collection_name}')

        return result.deleted_count

    def delete_many(self, filter_by: dict):
        result = self._collection.delete_many(filter_by)

        if result.deleted_count == 0:
            raise NoChangesMade(f'No documents deleted from repository {self.collection_name}')

        return result.deleted_count

    def get_one(self, filter_by: dict, hidden_fields: list[str], force_show_fields: list[str]):
        hidden_fields_dict = {}

        fields_to_hide = set(hidden_fields or self.hidden_fields) - set(force_show_fields)

        for item in fields_to_hide:
            hidden_fields_dict[item] = 0

        response = self._collection.find_one(filter_by, hidden_fields_dict)

        if response:
            return json.loads(json.dumps(response, default=str))

        return None

    def list(self, filter_by: dict, hidden_fields: list[str], force_show_fields: list[str]) -> list[dict]:
        hidden_fields_dict = {}

        fields_to_hide = set(hidden_fields or self.hidden_fields) - set(force_show_fields)

        for item in fields_to_hide:
            hidden_fields_dict[item] = 0

        response = self._collection.find(filter_by, hidden_fields_dict)

        return [json.loads(json.dumps(item, default=str)) for item in response]

    def aggregate(self, pipeline: [dict]) -> [dict]:
        return json.loads(json.dumps([item for item in self._collection.aggregate(pipeline)], default=str))

    def _flatten_json(self, nested_json, parent_key='', sep='.'):
        items = []
        for k, v in nested_json.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_json(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
