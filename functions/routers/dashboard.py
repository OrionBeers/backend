from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from dashboard.read_dashboard import DashboardDetails
from typing import Optional

router = APIRouter(
    tags=["dashboard"]
)

class DashboardGetRequest(BaseModel):
    uid: str
    history_id: Optional[str] = None

@router.get("/dashboard")
async def get_dashboard(
    uid: str = Query(..., description="User UID to search for"),
    history_id: Optional[str] = Query(None, description="History ID to search for"),
):
    try:
        print("get_dashboard")
        print(f"uid: {uid}")
        print(f"history_id: {history_id}")
        dashboard_details = DashboardDetails(uid=uid, history_id=history_id)
        result = dashboard_details.execute()
        print(f"result: {result}")
        return result
    except Exception as e:
        print(f"Error in get_dashboard: {str(e)}")
        # For specific dashboard with history_id, return 404
        if history_id:
            raise HTTPException(status_code=404, detail=str(e))
        # For general dashboard list, return 404 with more detail
        else:
            raise HTTPException(status_code=404, detail=f"No dashboard data found for user: {uid}")
