from pydantic import BaseModel

class ModelInterface(BaseModel):
    pass

    @staticmethod
    def list_fields_to_not_update() -> [str]:
        return ['_id', 'created_at']