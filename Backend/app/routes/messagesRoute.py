from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime
from app.database import message_collection, history_collection
from app.schemas import Message
from app.auth import verify_token
from app.utils import message_helper
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/api/messages",
    tags=["messages"]
)

# Initialize Groq client for summarization
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

@router.post("/", response_model=dict)
async def create_message(
    message: Message,
    token_data: dict = Depends(verify_token)
):
    """Save a message to the database, generate AI summary using Groq API as assistant response"""
    user_id = token_data["user_id"]

    # If no history_id, create a new history entry
    if not message.history_id:
        # Create new history
        history_doc = {
            "user_id": user_id,
            "created_at": datetime.utcnow()
        }
        history_result = await history_collection.insert_one(history_doc)
        history_id = str(history_result.inserted_id)
    else:
        history_id = message.history_id

    # Save user's message
    message_dict = {
        "history_id": history_id,
        "role": message.role,
        "content": message.content,
        "timestamp": message.timestamp or datetime.utcnow()
    }
    user_message_result = await message_collection.insert_one(message_dict)
    created_user_message = await message_collection.find_one({"_id": user_message_result.inserted_id})

    # Generate assistant message only if this is a user message
    if message.role == "user":
        # Fetch conversation history for context (like ChatGPT)
        conversation_messages = []
        
        # Get previous messages in this conversation (limit to last 20 messages to avoid token limits)
        # We fetch messages before the current one to get conversation context
        previous_messages_cursor = message_collection.find(
            {"history_id": history_id}
        ).sort("timestamp", 1)
        
        previous_messages = []
        async for msg in previous_messages_cursor:
            # Skip the current message we just saved (it will be added separately)
            if str(msg["_id"]) != str(user_message_result.inserted_id):
                previous_messages.append(msg)
        
        # Limit to last 20 messages to manage token usage (keep most recent context)
        if len(previous_messages) > 20:
            previous_messages = previous_messages[-20:]
        
        # Build conversation history for Groq API
        # Start with system message
        conversation_messages.append({
            "role": "system",
            "content": "You are a helpful AI assistant that provides concise and accurate summaries of text. You can also engage in conversation and answer questions. When asked to summarize text, provide clear and informative summaries. Maintain context from previous messages in the conversation and respond naturally based on the conversation history."
        })
        
        # Add all previous messages to maintain conversation context
        for prev_msg in previous_messages:
            conversation_messages.append({
                "role": prev_msg["role"],
                "content": prev_msg["content"]
            })
        
        # Add the current user message
        conversation_messages.append({
            "role": "user",
            "content": message.content
        })
        
        # Generate response using Groq API with conversation history
        try:
            if groq_client:
                # Use Groq API with full conversation history
                chat_completion = groq_client.chat.completions.create(
                    messages=conversation_messages,
                    model="llama-3.3-70b-versatile",  # Updated to current Groq model
                    temperature=0.7,
                    max_tokens=1000,  # Increased for better responses
                )
                assistant_content = chat_completion.choices[0].message.content.strip()
            else:
                # Fallback if Groq API key is not configured
                assistant_content = f"This is a placeholder response. Original text length: {len(message.content)} characters. Please configure GROQ_API_KEY in your .env file."
        except Exception as e:
            # Fallback on error
            assistant_content = f"Error generating response: {str(e)}. Please check your Groq API configuration."
        
        # Save assistant's message
        assistant_dict = {
            "history_id": history_id,
            "role": "assistant",
            "content": assistant_content,
            "timestamp": datetime.utcnow()
        }
        assistant_message_result = await message_collection.insert_one(assistant_dict)
        created_assistant_message = await message_collection.find_one({"_id": assistant_message_result.inserted_id})
        
        # Return both messages: user message and assistant message
        return {
            "user_message": message_helper(created_user_message),
            "assistant_message": message_helper(created_assistant_message),
            "history_id": history_id
        }
    else:
        # If it's not a user message (e.g., assistant message), just return the saved message
        return {
            "message": message_helper(created_user_message),
            "history_id": history_id
        }

@router.get("/", response_model=dict)
async def get_messages(
    token_data: dict = Depends(verify_token),
    history_id: str = None,
    limit: int = 50
):
    """Get messages, optionally filtered by history_id"""
    user_id = token_data["user_id"]
    
    query = {}
    if history_id:
        query["history_id"] = history_id
    else:
        # Get all histories for user and fetch their messages
        histories = await history_collection.find({"user_id": user_id}).to_list(length=100)
        history_ids = [str(h["_id"]) for h in histories]
        query["history_id"] = {"$in": history_ids}
    
    cursor = message_collection.find(query).sort("timestamp", 1).limit(limit)
    messages = await cursor.to_list(length=limit)
    
    return {"messages": [message_helper(msg) for msg in messages]}

@router.get("/{id}", response_model=dict)
async def get_message(
    id: str,
    token_data: dict = Depends(verify_token)
):
    """Get a specific message by ID"""
    message = await message_collection.find_one({"_id": ObjectId(id)})
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message_helper(message)

@router.get("/history/{history_id}", response_model=list)
async def get_messages_by_history(
    history_id: str,
    token_data: dict = Depends(verify_token)
):
    """Get all messages for a specific history"""
    messages_cursor = message_collection.find({"history_id": history_id}).sort("timestamp", 1)
    messages = []
    async for message in messages_cursor:
        messages.append(message_helper(message))
    return messages
