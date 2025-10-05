from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from location.create_location import LocationCreate
from location.delete_location import LocationDelete
from location.read_location import LocationDetails
from pydantic import BaseModel

router = APIRouter(
    tags=["locations"],
)


class LocationCreateRequest(BaseModel):
    display_name: str
    latitude: float
    longitude: float
    id_user: str


@router.get("/locations")
async def get_location_details(
    id_user: str = Query(..., description="The ID of the user"),
    location_id: Optional[str] = Query(None, description="The ID of the location"),
):
    try:
        location_details = LocationDetails(id_user=id_user)
        result = location_details.execute(id_location=location_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/locations", status_code=status.HTTP_201_CREATED)
async def create_location(location_data: LocationCreateRequest):
    try:
        create_location_service = LocationCreate(
            display_name=location_data.display_name,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            id_user=location_data.id_user,
        )
        result = create_location_service.execute()

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/locations", status_code=status.HTTP_200_OK)
async def delete_location(
        id_user: str = Query(..., description="The ID of the user"),
        id_location: str = Query(..., description="The ID of the location to delete")
):
    try:
        delete_service = LocationDelete(id_user=id_user, id_location=id_location)
        result = delete_service.execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
