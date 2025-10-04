from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, EmailStr
from user.create_user import CreateUser
from user.read_user import UserDetails
from user.update_user import UserUpdate
from typing import Optional

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

class UserCreateRequest(BaseModel):
    email: EmailStr
    name: str
    uid: str
    avatar: str = ''

class UserUpdateRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    avatar: Optional[str] = None

@router.get("/")
async def get_user(
    email: str = Query(..., description="User email to search for"), status_code=status.HTTP_200_OK):
    try:
        user_details = UserDetails(email=email)
        result = user_details.execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateRequest):
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


@router.patch("/", status_code=status.HTTP_200_OK)
async def update_user(user_data: UserUpdateRequest):
    try:
        update_service = UserUpdate(
            email=user_data.email,
            name=user_data.name,
            avatar=user_data.avatar
        )
        result = update_service.execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
