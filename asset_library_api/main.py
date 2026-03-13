"""
Asset Library API Backend
Connects Blender addon with Outseta (auth) and LemonSqueezy (files)
"""

from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from typing import Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="StylarX Asset Library API", version="1.0.0")

# CORS middleware - allows Blender addon to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== CONFIGURATION =====
# TODO: Move these to environment variables before deploying
OUTSETA_DOMAIN = os.getenv("OUTSETA_DOMAIN", "your-domain")  # e.g., "stylarx"
OUTSETA_API_KEY = os.getenv("OUTSETA_API_KEY", "your-outseta-api-key")
LEMONSQUEEZY_API_KEY = os.getenv("LEMONSQUEEZY_API_KEY", "your-lemonsqueezy-api-key")

# Plan hierarchy mapping
PLAN_HIERARCHY = {
    "Free": 0,
    "Basic": 1,
    "Premium": 2
}

# ===== MODELS =====
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user_email: str
    user_plan: str
    message: str

class Asset(BaseModel):
    id: str
    name: str
    category: str
    asset_type: str
    plan_required: str
    thumbnail_url: Optional[str] = None
    file_size: Optional[str] = None
    file_extension: Optional[str] = None

class DownloadResponse(BaseModel):
    download_url: str
    filename: str
    expires_at: Optional[str] = None


# ===== HELPER FUNCTIONS =====

async def verify_outseta_token(token: str) -> dict:
    """Verify token with Outseta and return user info"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://{OUTSETA_DOMAIN}.outseta.com/api/v1/profile",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Token verification failed: {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        return None


async def get_user_subscription_plan(user_uid: str, token: str) -> str:
    """Get user's subscription plan from Outseta"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://{OUTSETA_DOMAIN}.outseta.com/api/v1/billing/subscriptions",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                params={"AccountUid": user_uid}
            )
            
            if response.status_code == 200:
                subscriptions = response.json().get("items", [])
                if subscriptions:
                    # Get the first active subscription
                    for sub in subscriptions:
                        if sub.get("SubscriptionStatus") == "Active":
                            plan_name = sub.get("Plan", {}).get("Name", "Free")
                            # Map plan name to your tier system
                            if "premium" in plan_name.lower():
                                return "Premium"
                            elif "basic" in plan_name.lower() or "pro" in plan_name.lower():
                                return "Basic"
                
                return "Free"
            else:
                logger.warning(f"Could not fetch subscription: {response.status_code}")
                return "Free"
                
    except Exception as e:
        logger.error(f"Error fetching subscription: {str(e)}")
        return "Free"


def has_access_to_asset(user_plan: str, asset_plan_required: str) -> bool:
    """Check if user's plan allows access to an asset"""
    user_level = PLAN_HIERARCHY.get(user_plan, 0)
    required_level = PLAN_HIERARCHY.get(asset_plan_required, 0)
    return user_level >= required_level


async def fetch_lemonsqueezy_files() -> List[dict]:
    """Fetch all files from LemonSqueezy"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.lemonsqueezy.com/v1/files",
                headers={
                    "Authorization": f"Bearer {LEMONSQUEEZY_API_KEY}",
                    "Accept": "application/vnd.api+json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                logger.error(f"LemonSqueezy API error: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Error fetching LemonSqueezy files: {str(e)}")
        return []


def parse_lemonsqueezy_file_to_asset(file_data: dict) -> Optional[Asset]:
    """Convert LemonSqueezy file data to Asset model"""
    try:
        attributes = file_data.get("attributes", {})
        
        # Extract custom metadata from variant or product
        # You'll need to add these as custom fields in LemonSqueezy
        meta = attributes.get("meta", {})
        
        # File ID from LemonSqueezy
        file_id = file_data.get("id", "")
        
        # Build asset object
        asset = Asset(
            id=file_id,
            name=attributes.get("name", "Unnamed Asset"),
            category=meta.get("category", "Uncategorized"),
            asset_type=meta.get("asset_type", "3D_MODELS"),
            plan_required=meta.get("plan_required", "Free"),
            thumbnail_url=meta.get("thumbnail_url"),
            file_size=attributes.get("size_formatted"),
            file_extension=attributes.get("extension", ".blend")
        )
        
        return asset
        
    except Exception as e:
        logger.error(f"Error parsing file data: {str(e)}")
        return None


# ===== API ENDPOINTS =====

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "StylarX Asset Library API",
        "version": "1.0.0"
    }


@app.post("/api/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Authenticate user with Outseta
    
    This endpoint:
    1. Validates credentials with Outseta
    2. Gets user's subscription plan
    3. Returns auth token and user info
    """
    try:
        async with httpx.AsyncClient() as client:
            # Authenticate with Outseta
            response = await client.post(
                f"https://{OUTSETA_DOMAIN}.outseta.com/api/v1/tokens",
                json={
                    "username": credentials.email,
                    "password": credentials.password
                },
                headers={
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                
                # Get user profile to fetch subscription
                user_info = await verify_outseta_token(access_token)
                
                if user_info:
                    user_uid = user_info.get("Uid")
                    user_plan = await get_user_subscription_plan(user_uid, access_token)
                    
                    return LoginResponse(
                        token=access_token,
                        user_email=credentials.email,
                        user_plan=user_plan,
                        message=f"Successfully logged in as {user_plan} user"
                    )
                else:
                    raise HTTPException(status_code=401, detail="Could not verify user")
            
            elif response.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            else:
                logger.error(f"Outseta login error: {response.status_code} - {response.text}")
                raise HTTPException(status_code=500, detail="Authentication service error")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@app.get("/api/assets", response_model=List[Asset])
async def get_assets(
    category: Optional[str] = Query(None, description="Filter by asset category"),
    authorization: Optional[str] = Header(None)
):
    """
    Get list of assets filtered by category and user's plan
    
    Requires: Authorization header with Bearer token
    """
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Extract token
    token = authorization.replace("Bearer ", "")
    
    # Verify token and get user info
    user_info = await verify_outseta_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Get user's plan
    user_uid = user_info.get("Uid")
    user_plan = await get_user_subscription_plan(user_uid, token)
    
    # Fetch files from LemonSqueezy
    files = await fetch_lemonsqueezy_files()
    
    # Convert to assets
    assets = []
    for file_data in files:
        asset = parse_lemonsqueezy_file_to_asset(file_data)
        if asset:
            # Filter by category if specified
            if category and asset.asset_type != category:
                continue
            
            # Note: We return ALL assets but the Blender addon will show upgrade prompts
            # for assets the user doesn't have access to
            assets.append(asset)
    
    logger.info(f"Returning {len(assets)} assets for {user_plan} user")
    return assets


@app.get("/api/assets/{asset_id}/download", response_model=DownloadResponse)
async def get_download_url(
    asset_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Get signed download URL for an asset
    
    This endpoint:
    1. Verifies user has access
    2. Fetches download URL from LemonSqueezy
    3. Returns signed URL
    """
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Extract token
    token = authorization.replace("Bearer ", "")
    
    # Verify token and get user info
    user_info = await verify_outseta_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Get user's plan
    user_uid = user_info.get("Uid")
    user_plan = await get_user_subscription_plan(user_uid, token)
    
    try:
        async with httpx.AsyncClient() as client:
            # Fetch file details from LemonSqueezy
            response = await client.get(
                f"https://api.lemonsqueezy.com/v1/files/{asset_id}",
                headers={
                    "Authorization": f"Bearer {LEMONSQUEEZY_API_KEY}",
                    "Accept": "application/vnd.api+json"
                }
            )
            
            if response.status_code == 200:
                file_data = response.json().get("data", {})
                attributes = file_data.get("attributes", {})
                meta = attributes.get("meta", {})
                
                # Check if user has access to this asset
                plan_required = meta.get("plan_required", "Free")
                if not has_access_to_asset(user_plan, plan_required):
                    raise HTTPException(
                        status_code=403,
                        detail=f"This asset requires {plan_required} plan. Please upgrade at https://stylarx.com/pricing"
                    )
                
                # Get download URL
                download_url = attributes.get("download_url")
                if not download_url:
                    raise HTTPException(status_code=404, detail="Download URL not available")
                
                return DownloadResponse(
                    download_url=download_url,
                    filename=attributes.get("name", "asset.blend"),
                    expires_at=attributes.get("expires_at")
                )
            
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Asset not found")
            else:
                logger.error(f"LemonSqueezy error: {response.status_code}")
                raise HTTPException(status_code=500, detail="Could not fetch download URL")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download URL error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get download URL: {str(e)}")


@app.get("/api/user/profile")
async def get_user_profile(authorization: Optional[str] = Header(None)):
    """Get current user's profile and subscription info"""
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    token = authorization.replace("Bearer ", "")
    user_info = await verify_outseta_token(token)
    
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_uid = user_info.get("Uid")
    user_plan = await get_user_subscription_plan(user_uid, token)
    
    return {
        "email": user_info.get("Email"),
        "name": f"{user_info.get('FirstName', '')} {user_info.get('LastName', '')}".strip(),
        "plan": user_plan,
        "uid": user_uid
    }


# ===== ERROR HANDLERS =====

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom error response format"""
    return {
        "error": True,
        "message": exc.detail,
        "status_code": exc.status_code
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
