from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from location.create_location import LocationCreate
from location.delete_location import LocationDelete
from location.read_location import LocationDetails
from pydantic import BaseModel

router = APIRouter(prefix="/locations", tags=["locations"])


class LocationCreateRequest(BaseModel):
    display_name: str
    latitude: float
    longitude: float
    user_id: str


@router.get("/")
async def get_locations(
    # get id for the location and id for the user
    user_id: str = Query(..., description="The ID of the user"),
    location_id: Optional[str] = Query(None, description="The ID of the location"),
):
    try:
        location_details = LocationDetails(user_id=user_id)
        result = location_details.execute(id=location_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_location(location_data: LocationCreateRequest):
    try:
        create_location_service = LocationCreate(
            display_name=location_data.display_name,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            user_id=location_data.user_id,
        )
        result = create_location_service.execute()

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/", status_code=status.HTTP_200_OK)
async def delete_location(
    location_id: str = Query(..., description="The ID of the location to delete")
):
    try:
        delete_service = LocationDelete(location_id=location_id)
        result = delete_service.execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
