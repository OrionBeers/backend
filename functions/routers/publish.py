from firebase_functions import pubsub_fn
from fastapi import APIRouter
from google.cloud import pubsub_v1
from publish.predict_planting_date import PredictPlantingDate
from pydantic import BaseModel
import json

PROJECT_ID = "orion-beers-backend"
TOPIC_ID = "prediction"

router = APIRouter(
    prefix="/publish",
    tags=["publish"]
)

class PublishRequest(BaseModel):
    user_id: str

# Start Prediction background task by Pub/Sub
@router.post("/")
def publish_prediction(request: PublishRequest):
    publisher = pubsub_v1.PublisherClient()
    topic = publisher.topic_path(PROJECT_ID, TOPIC_ID)
    publisher.publish(topic, json.dumps({"user_id": request.user_id}).encode("utf-8"))

    return {"message": "Prediction started"}

# Add Pub/Sub worker
# This is triggered when a message is published to "prediction" topic in Pub/Sub
@pubsub_fn.on_message_published(topic="prediction")
def start_prediction_worker(event: pubsub_fn.CloudEvent[pubsub_fn.MessagePublishedData]) -> None:
    try:
        data = event.data.message.json
        if not data:
            print("no json payload")
            return
    except ValueError:
        print("payload is not json")
        return

    # TODO: Update payload
    user_id = data.get("user_id", "unknown")

    PredictPlantingDate(user_id).execute()
