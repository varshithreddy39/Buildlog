from fastapi import FastAPI
from backend.routers.health_check import router as health_router
from backend.routers.ingestion import router as ingestion_router


app=FastAPI()

app.include_router(health_router)
app.include_router(ingestion_router)
    

@app.get("/")
async def root():
    return {
        "message": "Welcome to Agentic Adaptive RAG API"
    }