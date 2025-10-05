from firebase_functions import pubsub_fn
from fastapi import APIRouter
from lib.gcloud.pub_sub import PublishPredictionPayload, publish_prediction, TOPIC_ID_PREDICTION
from publish.predict_planting_date import PredictPlantingDate
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["publish"]
)

@router.post("/publish")
def start_prediction(body: PublishPredictionPayload):
    # Publish message to "prediction" topic in Pub/Sub to start prediction background task.
    logger.info(f"Publishing prediction request: {body.model_dump()}")
    publish_prediction(body)

    return {"message": "Prediction started"}

# Pub/Sub subscriber
# This is triggered when a message is published to "prediction" topic in Pub/Sub
@pubsub_fn.on_message_published(topic=TOPIC_ID_PREDICTION)
def start_prediction_worker(event: pubsub_fn.CloudEvent[pubsub_fn.MessagePublishedData]) -> None:
    logger.info("PubSub message received on topic: %s", TOPIC_ID_PREDICTION)
    try:
        data = event.data.message.json
        logger.info(f"Message data: {json.dumps(data, indent=2)}")
        if not data:
            logger.error("No JSON payload in the message")
            return
    except ValueError:
        logger.error("Payload is not valid JSON")
        return
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return

    # Extract user ID from payload
    id_user = data.get("id_user", "unknown")
    logger.info(f"Starting prediction for user: {id_user}")

    # Start prediction
    try:
        PredictPlantingDate(id_user, data).execute()
        logger.info(f"Prediction completed successfully for user: {id_user}")
    except Exception as e:
        logger.error(f"Prediction failed for user {id_user}: {str(e)}")
