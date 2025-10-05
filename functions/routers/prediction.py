from fastapi import APIRouter, HTTPException, status, Query
from lib.gcloud.pub_sub import PublishPredictionPayload, publish_prediction
from pydantic import BaseModel
from firebase_functions import pubsub_fn
from lib.gcloud.pub_sub import PublishPredictionPayload, publish_prediction, TOPIC_ID_PREDICTION
from publish.predict_planting_date import PredictPlantingDate
import json
import logging
from prediction.get_predictions_result import GetPredictionsResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    tags=["Prediction"],
)

class PredictionCreateRequest(BaseModel):
    crop: str
    latitude: float
    longitude: float
    start_month: int
    id_user: str

@router.get("/prediction")
async def get_result(
    id_user: str = Query(..., description="Id user from google"),
    id_request: str = Query(..., description="Id user from google"),
    status_code=status.HTTP_200_OK):
    try:
        result = GetPredictionsResult(id_user=id_user, id_request=id_request).execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/prediction")
def start_prediction(body: PublishPredictionPayload):
    # Publish message to "prediction" topic in Pub/Sub to start prediction background task.
    logger.info(f"Publishing prediction request: {body.model_dump()}")

    # Create a copy of the body's data
    body_data = body.model_dump()

    # Set default values only if they don't exist already
    if "prediction_days" not in body_data:
        body_data["prediction_days"] = "full"
    if "continue_to_next_month" not in body_data:
        body_data["continue_to_next_month"] = True

    # Create a new PublishPredictionPayload object with the updated data
    payload = PublishPredictionPayload(**body_data)
    publish_prediction(payload)

    return {"message": "Prediction started"}

# Pub/Sub subscriber
# This is triggered when a message is published to "prediction" topic in Pub/Sub
@pubsub_fn.on_message_published(topic=TOPIC_ID_PREDICTION)
def start_prediction_worker(event: pubsub_fn.CloudEvent[pubsub_fn.MessagePublishedData]) -> None:
    logger.info("PubSub message received on topic: %s", TOPIC_ID_PREDICTION)
    try:
        # Parse JSON data from message
        raw_data = event.data.message.json
        logger.info(f"Raw message data: {json.dumps(raw_data, indent=2)}")

        if not raw_data:
            logger.error("No JSON payload in the message")
            return

        # Convert the raw dictionary to a PublishPredictionPayload model
        data = PublishPredictionPayload(**raw_data)
        logger.info(f"Parsed payload: {data}")
    except ValueError:
        logger.error("Payload is not valid JSON")
        return
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return

    # Extract user ID from payload
    id_user = data.id_user
    logger.info(f"Starting prediction for user: {id_user}")

    # Start prediction
    try:
        PredictPlantingDate(id_user, raw_data).execute()
        logger.info(f"Prediction completed successfully for user: {id_user}")

        # Start next prediction if needed
        # TODO: This should be decided by prediction result
        to_be_continued = False
        if to_be_continued == True:
            start_month = data.start_month
            if data.continue_to_next_month:
                start_month = start_month + 1

            # If continue_to_next_month is False, then continue to next month
            continue_to_next_month = not data.continue_to_next_month

            # Create a new payload dictionary with updated values
            new_data = data.model_dump()
            new_data["id_request"] = data.id_request
            new_data["prediction_days"] = "half"
            new_data["start_month"] = start_month
            new_data["continue_to_next_month"] = continue_to_next_month

            # Create a new PublishPredictionPayload from the dictionary
            new_payload = PublishPredictionPayload(**new_data)
            publish_prediction(new_payload)

    except Exception as e:
        logger.error(f"Prediction failed for user {id_user}: {str(e)}")
