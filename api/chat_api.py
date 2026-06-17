from fastapi import APIRouter
from pydantic import BaseModel
from services.response_service import generate_response

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: int


class ChatResponse(BaseModel):
    answer: str
    confidence: float | None = None
    tokens_used: int | None = None
    model_name: str = "rag-keyword-v1"


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = generate_response(request.message, request.session_id)
    return ChatResponse(**result)