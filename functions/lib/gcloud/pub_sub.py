from google.cloud import pubsub_v1
from pydantic import BaseModel
import json

PROJECT_ID = "orion-beers-backend"
TOPIC_ID_PREDICTION = "prediction"

class PublishPredictionPayload(BaseModel):
    user_id: str

def publish_prediction(payload: PublishPredictionPayload):
    publisher = pubsub_v1.PublisherClient()
    topic = publisher.topic_path(PROJECT_ID, TOPIC_ID_PREDICTION)
    publisher.publish(topic, json.dumps(payload.model_dump()).encode("utf-8"))
