# StylarX Asset Library API Backend

FastAPI backend that connects your Blender addon with Outseta (authentication) and LemonSqueezy (file delivery).

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```env
OUTSETA_DOMAIN=stylarx
OUTSETA_API_KEY=your-key-here
LEMONSQUEEZY_API_KEY=your-key-here
```

### 3. Run Locally

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

### 4. Test the API

Visit: `http://localhost:8000/docs` for interactive API documentation

---

## 📡 API Endpoints

### Authentication

**POST** `/api/auth/login`
```json
Request:
{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "token": "jwt-token-here",
  "user_email": "user@example.com",
  "user_plan": "Premium",
  "message": "Successfully logged in as Premium user"
}
```

### Assets

**GET** `/api/assets?category=3D_MODELS`

Headers: `Authorization: Bearer <token>`

```json
Response:
[
  {
    "id": "123456",
    "name": "Modern Chair",
    "category": "Furniture",
    "asset_type": "3D_MODELS",
    "plan_required": "Free",
    "thumbnail_url": "https://...",
    "file_size": "5.2 MB",
    "file_extension": ".blend"
  }
]
```

**GET** `/api/assets/{asset_id}/download`

Headers: `Authorization: Bearer <token>`

```json
Response:
{
  "download_url": "https://signed-url...",
  "filename": "Modern_Chair.blend",
  "expires_at": "2026-02-07T12:00:00Z"
}
```

**GET** `/api/user/profile`

Headers: `Authorization: Bearer <token>`

```json
Response:
{
  "email": "user@example.com",
  "name": "John Doe",
  "plan": "Premium",
  "uid": "user-uid-123"
}
```

---

## 🔑 Getting API Keys

### Outseta API Key

1. Log in to your Outseta account
2. Go to **Settings > Integrations > API Keys**
3. Click **Create New API Key**
4. Copy the key and add to `.env` as `OUTSETA_API_KEY`
5. Your domain is the subdomain: `https://YOUR-DOMAIN.outseta.com`

### LemonSqueezy API Key

1. Log in to LemonSqueezy: https://app.lemonsqueezy.com
2. Go to **Settings > API**
3. Click **Create API Key**
4. Copy the key and add to `.env` as `LEMONSQUEEZY_API_KEY`

---

## 📦 Setting Up Assets in LemonSqueezy

For the API to work properly, you need to add custom metadata to your LemonSqueezy products:

### Option 1: Using Product Custom Fields (Recommended)

In each LemonSqueezy product, add these custom fields:

```json
{
  "meta": {
    "category": "Furniture",
    "asset_type": "3D_MODELS",
    "plan_required": "Free",
    "thumbnail_url": "https://your-cdn.com/thumbnails/chair.png"
  }
}
```

### Option 2: Using Variant Names (Alternative)

Name your variants with a specific pattern:
```
[CATEGORY] - [ASSET_TYPE] - [PLAN] - Asset Name
Example: Furniture - 3D_MODELS - Free - Modern Chair
```

Then update the `parse_lemonsqueezy_file_to_asset()` function to parse the name.

### Asset Types

- `3D_MODELS`
- `3D_SCENES`
- `GOBOS`
- `GEOMETRY_NODES`
- `3D_MOCKUPS`
- `3D_ANIMATED_MOCKUPS`
- `ADDONS`

### Plan Requirements

- `Free`
- `Basic`
- `Premium`

---

## 🚢 Deployment

### Option 1: Railway (Easiest)

1. Install Railway CLI: `npm i -g @railway/cli`
2. Run: `railway login`
3. Run: `railway init`
4. Run: `railway up`
5. Add environment variables in Railway dashboard
6. Your API is live!

**Cost:** ~$5/month

### Option 2: Render.com

1. Push code to GitHub
2. Go to https://render.com
3. Create new **Web Service**
4. Connect your GitHub repo
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Add environment variables
8. Deploy!

**Cost:** Free tier available, $7/month for paid

### Option 3: DigitalOcean App Platform

1. Push code to GitHub
2. Go to DigitalOcean App Platform
3. Create new app from GitHub
4. Select repository
5. Add environment variables
6. Deploy!

**Cost:** $5/month

### Option 4: Docker (Any Platform)

```bash
docker build -t asset-library-api .
docker run -p 8000:8000 --env-file .env asset-library-api
```

Deploy to:
- AWS ECS
- Google Cloud Run
- Azure Container Instances
- Your own server

---

## 🔧 Customization

### Changing Plan Mapping

Edit the `get_user_subscription_plan()` function to match your Outseta plan names:

```python
if "premium" in plan_name.lower():
    return "Premium"
elif "basic" in plan_name.lower() or "pro" in plan_name.lower():
    return "Basic"
```

### Adding Caching

To improve performance, add Redis caching:

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="asset-cache")
```

### Rate Limiting

Add rate limiting to prevent abuse:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/assets")
@limiter.limit("100/minute")
async def get_assets(...):
    ...
```

---

## 🐛 Troubleshooting

### "Invalid credentials" error

- Check that `OUTSETA_DOMAIN` is correct (just the subdomain, not the full URL)
- Verify `OUTSETA_API_KEY` is valid
- Test login directly in Outseta

### "Could not fetch files" error

- Check that `LEMONSQUEEZY_API_KEY` is valid
- Verify you have products/files in LemonSqueezy
- Check LemonSqueezy API status

### CORS errors

- Make sure CORS middleware is enabled
- In production, update `allow_origins` to your specific domain
- Check browser console for specific CORS error

### Token expired

- Outseta tokens expire after a certain time
- Implement token refresh logic if needed
- Consider storing token expiry time

---

## 📊 Monitoring

### Health Check

Visit: `http://your-api.com/` to check if API is running

### Logs

All errors are logged with Python's logging module:

```bash
# View logs
tail -f /var/log/your-app.log
```

### API Documentation

Visit: `http://your-api.com/docs` for Swagger UI
Visit: `http://your-api.com/redoc` for ReDoc

---

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use HTTPS in production** - Railway/Render provide this automatically
3. **Rotate API keys regularly**
4. **Implement rate limiting**
5. **Add request validation**
6. **Monitor for suspicious activity**
7. **Set CORS to specific domains** in production

---

## 📝 Testing

Test with curl:

```bash
# Health check
curl http://localhost:8000/

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Get assets
curl http://localhost:8000/api/assets?category=3D_MODELS \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Or use the interactive docs at `/docs`

---

## 🤝 Support

If you run into issues:
1. Check the logs for error messages
2. Verify all environment variables are set
3. Test Outseta/LemonSqueezy APIs directly
4. Check this README for troubleshooting steps

---

## 📄 License

Proprietary - StylarX Asset Library

---

## 🎉 Next Steps

After deploying:
1. Get your API URL (e.g., `https://your-app.railway.app`)
2. Update the Blender addon with this URL
3. Test login from Blender
4. Start uploading assets to LemonSqueezy with metadata!
