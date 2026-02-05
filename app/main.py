from fastapi import FastAPI, Header, Request
from app.routes.honeypot import honeypot_endpoint
from app.routes.honeypot import router as honeypot_router

app = FastAPI(title="GUVI Honeypot API")

# Original API route (keep this)
app.include_router(honeypot_router, prefix="/api")


# HEALTH CHECK
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "guvi-honeypot"
    }


# ROOT GET (Safe)
@app.get("/")
def home():
    return {"status": "running"}


# 🚨 EMERGENCY FIX — ROOT POST HANDLER
@app.post("/")
async def root_post(
    request: Request,
    x_api_key: str = Header(None)
):
    # Forward request to honeypot logic
    body = await request.json()

    return await honeypot_endpoint(
        request=body,
        x_api_key=x_api_key
    )
