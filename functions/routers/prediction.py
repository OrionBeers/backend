from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel

from prediction.get_predictions_result import GetPredictionsResult

router = APIRouter(
    tags=["Prediction"],
)

class PredictionCreateRequest(BaseModel):
    crop: str
    latitude: float
    longitude: float
    start_month: int
    id_google: str

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
