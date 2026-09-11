from pathlib import Path
import shutil
import tempfile

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
    status,
)

from backend.services.ingestion_service import IngestionService

router = APIRouter(
    prefix="/ingestion",
    tags=["Document Ingestion"],
)

ingestion_service = IngestionService()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def ingest_document(
    file: UploadFile = File(...),
):
    """
    Upload and ingest a document into the knowledge base.
    """

    temp_path = None

    try:
        suffix = Path(file.filename).suffix

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:

            shutil.copyfileobj(
                file.file,
                temp_file,
            )

            temp_path = temp_file.name

        return ingestion_service.ingest(temp_path)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    finally:
        if temp_path and Path(temp_path).exists():
            Path(temp_path).unlink()