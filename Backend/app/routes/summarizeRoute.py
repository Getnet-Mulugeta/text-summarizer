"""
Summarization routes
"""
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas import SummarizeRequest, SummarizeResponse
from app.auth import verify_token
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/api/summarize",
    tags=["summarization"]
)

# Initialize Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)



@router.post("/", response_model=SummarizeResponse)
async def summarize_text(
    request: SummarizeRequest,
    token_data: dict = Depends(verify_token)
):
    """Summarize the provided text using Groq API"""
    text = request.text.strip()
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty"
        )
    
    # If Groq API key is not configured, return placeholder
    if not groq_client:
        summary = f"This is a placeholder summary of your text. Original text length: {len(text)} characters. Please configure GROQ_API_KEY in your .env file."
        return SummarizeResponse(
            summary=summary,
            original_length=len(text),
            summary_length=len(summary)
        )
    
    try:
        # Use Groq API to generate summary
        chat_completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Updated to current Groq model (replaces deprecated llama-3.1-70b-versatile)
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides concise and accurate summaries of text. Summarize the given text in a clear and informative way."
                },
                {
                    "role": "user",
                    "content": f"Please summarize the following text:\n\n{text}"
                }
            ],
            temperature=0.7,
            max_tokens=500,
        )
        
        summary = chat_completion.choices[0].message.content.strip()
        
        return SummarizeResponse(
            summary=summary,
            original_length=len(text),
            summary_length=len(summary)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating summary: {str(e)}"
        )
