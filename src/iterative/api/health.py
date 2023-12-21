from fastapi import APIRouter


router = APIRouter()

# Add a health check endpoint
@router.get("/health")
def health():
    return {"status": "ok"}