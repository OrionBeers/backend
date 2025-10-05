from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel

from prediction.get_predictions_result import GetPredictionsResult
from prediction.start_prediction import StartPrediction

router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"],
)

class PredictionCreateRequest(BaseModel):
    crop: str
    latitude: float
    longitude: float
    start_month: int
    id_google: str

@router.get("/")
async def get_result(
    id_user: str = Query(..., description="Id user from google"), status_code=status.HTTP_200_OK):
    try:
        result = GetPredictionsResult(id_user=id_user).execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_prediction(user_data: PredictionCreateRequest):
    try:
        create_user_service = CreateUser(
            email=user_data.email,
            name=user_data.name,
            uid=user_data.uid,
            avatar=user_data.avatar,
        )
        result = create_user_service.execute()

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
