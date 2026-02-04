from fastapi import FastAPI
from app.routes.honeypot import router as honeypot_router

app = FastAPI(title="GUVI Honeypot API")

app.include_router(honeypot_router, prefix="/api")

@app.get("/")
def home():
    return {"status": "running"}
