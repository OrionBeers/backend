from firebase_functions import pubsub_fn
from fastapi import APIRouter
from lib.gcloud.pub_sub import PublishPredictionPayload, publish_prediction, TOPIC_ID_PREDICTION
from publish.predict_planting_date import PredictPlantingDate


router = APIRouter(
    prefix="/publish",
    tags=["publish"]
)

@router.post("/")
def start_prediction(body: PublishPredictionPayload):
    # Publish message to "prediction" topic in Pub/Sub to start prediction background task.
    publish_prediction(body)

    return {"message": "Prediction started"}

# Pub/Sub subscriber
# This is triggered when a message is published to "prediction" topic in Pub/Sub
@pubsub_fn.on_message_published(topic=TOPIC_ID_PREDICTION)
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

    # Start prediction
    PredictPlantingDate(user_id).execute()
