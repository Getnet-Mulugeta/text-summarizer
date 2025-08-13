"""
User profile routes
"""
from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from app.database import user_collection
from app.auth import verify_token
from app.utils import user_helper

router = APIRouter(
    prefix="/api/user",
    tags=["user"]
)


@router.get("/profile")
async def get_user_profile(token_data: dict = Depends(verify_token)):
    """Get current user profile"""
    user_id = token_data["user_id"]
    
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return user_helper(user)
