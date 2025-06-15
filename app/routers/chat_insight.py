from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.schemas.chat import ChatInsightRequest, ChatInsightResponse
from app.database import get_db
from app.services.insight_generator import generate_insight

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/insight", response_model=ChatInsightResponse)
def chat_insight(data: ChatInsightRequest, request: Request, db: Session = Depends(get_db)):
    try:
        insight = generate_insight(data.prompt, data.context or "", db)
        return ChatInsightResponse(insight=insight)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insight: {str(e)}")