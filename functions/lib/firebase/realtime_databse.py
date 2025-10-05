from firebase_admin import db
from pydantic import BaseModel

# request
# {
#   id_user: str
#   status: str
#   created_at: datetime,
#   updated_at: datetime
# }

#  update for realtime database
# {
#   "[id_user]":{
#     status: str,
#     created_at: datetime,
#     updated_at: datetime
#   }
# }


class UpdateRequest(BaseModel):
    id_user: str
    id_request: str
    status: str
    created_at: str
    updated_at: str


def update(payload: UpdateRequest):

    ref = db.reference(f"{payload.id_user}/{payload.id_request}")

    if ref.get() is None:
        ref.set(
            {
                "status": payload.status,
                "created_at": payload.created_at,
                "updated_at": payload.updated_at,
            }
        )
    else:
        ref.update({"status": payload.status, "updated_at": payload.updated_at})

    return {"is_success": True, "message": "Update successful"}
