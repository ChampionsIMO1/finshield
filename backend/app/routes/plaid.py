from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from supabase import create_client
from plaid.api import PlaidApi
from plaid.model import LinkTokenCreateRequest, LinkTokenCreateRequestUser, ItemPublicTokenExchangeRequest
from plaid import ApiClient, Configuration
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

router = APIRouter(prefix="/plaid", tags=["plaid"])
security = HTTPBearer()

def get_plaid_client():
    configuration = Configuration(
        host = "https://sandbox.plaid.com" if settings.plaid_env == "sandbox" else "https://production.plaid.com",
        api_key = {
            "clientId": settings.plaid_client_id, 
            "secret": settings.plaid_secret
        }
    )
    return PlaidApi(ApiClient(configuration))

def get_supabase():
    return create_client(settings.supabase_url, settings.supabase_key)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    supabase = get_supabase()
    try:
        user = supabase.auth.get_user(token)
        return user.user
    except:
        raise HTTPException(status_code=401, detail="Invalid/expired token")

@router.post("/create-link-token")
def create_link_token(user = Depends(get_current_user)):
    try: 
        client = get_plaid_client()
        request = LinkTokenCreateRequest(
            user = LinkTokenCreateRequestUser(client_user_id=str(user.id)),
            client_name = "SphinxGuard",
            products = [Products("transactions")],
            country_codes = [CountryCode("CA")],
            language = "en"
        )
        response = client.link_token_create(request)
        return {"link_token": response["link_token"]}
    except:
        raise HTTPException(status_code=400, detail="Link token could not be created")