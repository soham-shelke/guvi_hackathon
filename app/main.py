from fastapi import FastAPI, Header, Request, HTTPException
from app.routes.honeypot import honeypot_endpoint, HoneypotRequest
from app.routes.honeypot import router as honeypot_router

app = FastAPI(title="GUVI Honeypot API")

# Keep original router
app.include_router(honeypot_router, prefix="/api")


@app.get("/")
def home():
    return {"status": "running"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "guvi-honeypot"
    }


# 🚨 FIXED ROOT POST HANDLER
@app.post("/")
async def root_post(
    request: Request,
    x_api_key: str = Header(None)
):
    try:
        body = await request.json()

        # Convert dict → Pydantic model
        model_request = HoneypotRequest(**body)

        return await honeypot_endpoint(
            request=model_request,
            x_api_key=x_api_key
        )

    except Exception as e:
        print("ROOT POST ERROR:", e)
        raise HTTPException(status_code=400, detail="Invalid request body")

@app.post("/v2")
async def root_v2_post(
    request: Request,
    x_api_key: str = Header(None)
):
    try:
        body = await request.json()

        model_request = HoneypotRequest(**body)

        return await honeypot_endpoint(
            request=model_request,
            x_api_key=x_api_key
        )

    except Exception as e:
        print("V2 ROOT POST ERROR:", e)
        raise HTTPException(status_code=400, detail="Invalid request body")
