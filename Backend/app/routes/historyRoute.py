"""
History routes
"""
from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime
from app.database import history_collection
from app.schemas import ChatHistory
from app.auth import verify_token
from app.utils import history_helper

router = APIRouter(
    prefix="/api/history",
    tags=["history"]
)


@router.post("/")
async def save_chat_history(
    history: ChatHistory,
    token_data: dict = Depends(verify_token)
):
    """Save chat history"""
    user_id = token_data["user_id"]
    
    history_doc = {
        "user_id": user_id,
        "messages": [msg.dict() for msg in history.messages],
        "created_at": datetime.utcnow()
    }
    
    result = await history_collection.insert_one(history_doc)
    created_history = await history_collection.find_one({"_id": result.inserted_id})
    
    return {"message": "History saved", "data": history_helper(created_history)}


@router.get("/")
async def get_chat_history(
    token_data: dict = Depends(verify_token),
    limit: int = 20,
    skip: int = 0
):
    """Get user's chat history with pagination"""
    user_id = token_data["user_id"]
    
    # Get total count for pagination info
    total_count = await history_collection.count_documents({"user_id": user_id})
    
    # Get paginated history
    cursor = history_collection.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
    histories = await cursor.to_list(length=limit)
    
    return {
        "history": [history_helper(hist) for hist in histories],
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total_count
    }


@router.delete("/{history_id}")
async def delete_chat_history(
    history_id: str,
    token_data: dict = Depends(verify_token)
):
    """Delete a specific chat history"""
    user_id = token_data["user_id"]
    
    result = await history_collection.delete_one({
        "_id": ObjectId(history_id),
        "user_id": user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="History not found"
        )
    
    return {"message": "History deleted successfully"}
