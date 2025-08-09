"""
Authentication routes
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.database import user_collection
from app.auth import get_password_hash, verify_password, create_access_token
from app.utils import user_helper

router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"]
)


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = await user_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = await user_collection.find_one({"username": user.username})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Create user document
    user_doc = {
        "username": user.username,
        "email": user.email,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    }
    
    result = await user_collection.insert_one(user_doc)
    created_user = await user_collection.find_one({"_id": result.inserted_id})
    
    return {"message": "User created successfully", "user": user_helper(created_user)}


@router.post("/login")
async def login(credentials: UserLogin):
    """Login user and return JWT token"""
    user = await user_collection.find_one({"email": credentials.email})
    
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    token_data = {"user_id": str(user["_id"]), "email": user["email"]}
    access_token = create_access_token(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_helper(user)
    }
