from fastapi import (APIRouter,
    UploadFile,
    File,
    HTTPException,
    
)

from pydantic import BaseModel



from services_rag.pipline import (
    handle_upload,
    question_answer_pipeline
)


router = APIRouter(
)



class Prompt(BaseModel):
    text: str




@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...)):

    
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )
    content = await file.read()
    result = handle_upload(
        file_content=content,
        filename=file.filename
    )
    return result




@router.post("/ask")
def ask_question(
    prompt: Prompt,
):

    answer = question_answer_pipeline(
        query=prompt.text,
    )

    return answer
    







