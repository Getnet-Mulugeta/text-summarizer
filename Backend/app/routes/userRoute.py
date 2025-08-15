from fastapi import APIRouter, HTTPException
from app.database import user_collection
from app.schemas import User
from app.utils import user_helper
from bson import ObjectId

router = APIRouter(prefix="/users",
    tags=["users"])

@router.post("/", response_model=dict)
async def create_user(user: User):
    new_user = await user_collection.insert_one(user.dict())
    created_user = await user_collection.find_one(
        {"_id": new_user.inserted_id}
    )
    return user_helper(created_user)


@router.get("/{id}", response_model=dict)
async def get_user(id: str):
    user = await user_collection.find_one({"_id": ObjectId(id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_helper(user)
