from fastapi import APIRouter, status

router = APIRouter(
    prefix="/health",
    tags=["Health Check"],
)

@router.get("/", status_code=status.HTTP_200_OK)
async def health_router():
    return {"status": "healthy"}