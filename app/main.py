from fastapi import FastAPI
from app.routes.honeypot import router as honeypot_router

app = FastAPI(title="GUVI Honeypot API")

# Include Honeypot Routes
app.include_router(honeypot_router, prefix="/api")


# Root Endpoint (Optional but Good)
@app.get("/")
def home():
    return {"status": "running"}


# Health Endpoint (For UptimeRobot)
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "guvi-honeypot",
        "uptime": "active"
    }
