from typing import Literal, Optional
from google.cloud import pubsub_v1
from pydantic import BaseModel
import json

from infrastructure.database.collections.request_collections import RequestCollection
from infrastructure.database.models.request_model import RequestModel
from lib.firebase.realtime_databse import update, UpdateRequest

PROJECT_ID = "orion-beers-backend"
TOPIC_ID_PREDICTION = "prediction"

class PublishPredictionPayload(BaseModel):
    id_user: str
    latitude: float
    longitude: float
    crop_type: str
    start_month: str
    id_request: Optional[str] = None
    prediction_days: Literal["full", "half"] = "full"
    continue_to_next_month: Optional[bool] = False


def publish_prediction(payload: PublishPredictionPayload):
    ## Trying to insert at request Collection in Firestore
    try:
        data_to_insert = {
            "id_user": payload.id_user,
            "data": {
                "latitude": payload.latitude,
                "longitude": payload.longitude,
                "crop_type": payload.crop_type,
                "start_month": payload.start_month
            }
        }

        request_id = RequestCollection().insert(RequestModel(**data_to_insert))

        update_payload = {
            "id_user": payload.id_user,
            "id_request": request_id.inserted_id,
            "status": "pending",
            "created_at": str(RequestModel(**data_to_insert).created_at),
            "updated_at": str(RequestModel(**data_to_insert).updated_at)
        }

        ## Inserting data in the realtime database
        update_request = UpdateRequest(**update_payload)
        update(update_request)

        # Set id_request to continue the prediction
        # Using direct attribute access instead of .get() since payload is a Pydantic model
        if payload.id_request is None:
            # Need to update the model directly with new id_request
            payload_dict = payload.model_dump()
            payload_dict["id_request"] = request_id.inserted_id
            # Create a new instance with the updated id_request
            updated_payload = PublishPredictionPayload(**payload_dict)

            publisher = pubsub_v1.PublisherClient()
            topic = publisher.topic_path(PROJECT_ID, TOPIC_ID_PREDICTION)
            publisher.publish(topic, json.dumps(updated_payload.model_dump()).encode("utf-8"))
        else:
            publisher = pubsub_v1.PublisherClient()
            topic = publisher.topic_path(PROJECT_ID, TOPIC_ID_PREDICTION)
            publisher.publish(topic, json.dumps(payload.model_dump()).encode("utf-8"))

    except Exception as e:
        print(f"Error inserting request to Firestore: {e}")
