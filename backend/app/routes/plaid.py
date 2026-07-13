from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from supabase import create_client
from plaid.api.plaid_api import PlaidApi
from plaid.api_client import ApiClient
from plaid.configuration import Configuration
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest

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
    return create_client(settings.supabase_url, settings.supabase_service_key)

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

@router.post("/exchange-token")
def exchange_token(public_token: str, user = Depends(get_current_user)):
    try:
        supabase = get_supabase()
        client = get_plaid_client()
        response = client.item_public_token_exchange(ItemPublicTokenExchangeRequest(public_token=public_token))
        access_token = response["access_token"]
        accounts = {
            "user_id": str(user.id),
            "plaid_access_token": access_token,
            "plaid_account_id": "pending"
        }
        supabase.table("accounts").insert(accounts).execute()
        return {"message": "Account linked successfully!"}
    except:
        raise HTTPException(status_code=400, detail="Unable to link account")