from fastapi import FastAPI
from routers_rag import rag_endpoints
app = FastAPI()
app.include_router(rag_endpoints.router)