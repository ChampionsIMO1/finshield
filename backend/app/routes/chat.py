from google import genai
from google.genai import types
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from supabase import create_client
from pydantic import BaseModel

client = genai.Client(api_key=settings.gemini_api_key)

router = APIRouter(prefix="/chat", tags=["chat"])
security = HTTPBearer()

def get_supabase():
    return create_client(settings.supabase_url, settings.supabase_service_key)

class ChatRequest(BaseModel):
    message: str

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    supabase = get_supabase()
    try:
        user = supabase.auth.get_user(token)
        return user.user
    except:
        raise HTTPException(status_code=401, detail="Invalid/expired token")
    
@router.post("/message")
def chat_messages(body: ChatRequest, user = Depends(get_current_user)):
    try:
        supabase = get_supabase()

        transactions = supabase.table("transactions")\
            .select("*")\
            .eq("user_id", str(user.id))\
            .execute()
        
        fraud_scores = supabase.table("fraud_scores")\
            .select("*")\
            .eq("user_id", str(user.id))\
            .execute()
        
        context = f"""
            You are a financial assistant for SphinxGuard, a fraud detection platform.
            The user has {len(transactions.data)} transactions.
            Flagged: {len([f for f in fraud_scores.data if f['is_flagged']])} transactions.
            User question: {body.message}
            Answer concisely.
        """

        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=context
        )
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))