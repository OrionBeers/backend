from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from dashboard.read_dashboard import DashboardDetails
from typing import Optional

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

class DashboardGetRequest(BaseModel):
    uid: str
    history_id: Optional[str] = None

@router.get("/")
async def get_dashboard(
    uid: str = Query(..., description="User UID to search for"),
    history_id: Optional[str] = Query(None, description="History ID to search for"),
):
    try:
        print("get_dashboard")
        print(uid)
        dashboard_details = DashboardDetails(uid=uid, history_id=history_id)
        result = dashboard_details.execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
