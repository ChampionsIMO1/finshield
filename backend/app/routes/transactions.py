from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from supabase import create_client

router = APIRouter(prefix="/transactions", tags=["transactions"])
security = HTTPBearer()

def get_supabase():
    return create_client(settings.supabase_url, settings.supabase_service_key)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    supabase = get_supabase()
    try:
        user = supabase.auth.get_user(token)
        return user.user
    except:
        raise HTTPException(status_code=401, detail="Invalid/expired token")

@router.get("/")
def get_transactions(user = Depends(get_current_user)):
    supabase = get_supabase()
    try:
        transactions = supabase.table("transactions")\
            .select("*")\
            .eq("user_id", user.id)\
            .order("date", desc=True)\
            .execute()
        fraud_scores = supabase.table("fraud_scores")\
            .select("*")\
            .eq("user_id", user.id)\
            .execute()
        return {
            "transactions": transactions.data,
            "fraud_scores": fraud_scores.data,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))