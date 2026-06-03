# app/main.py
from fastapi import FastAPI
from .api import router

app = FastAPI(title="Shivanetra Astrology API", version="1.0")
app.include_router(router, prefix="/v1")

@app.get("/")
def root():
    return {"message": "Shivanetra Engine is running", "status": "active"}
