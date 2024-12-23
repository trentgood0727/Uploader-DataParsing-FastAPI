from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app import crud, models, schemas, database, tasks
from app.database import SessionLocal
from app.models import ParsedContent
import os
from datetime import datetime
from fastapi.responses import HTMLResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
models.Base.metadata.create_all(bind=database.engine)

#UPLOAD_FOLDER = "uploads/"
UPLOAD_FOLDER = "../uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload/", response_model=schemas.FileRecordResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        print(f"Received file: {file.filename}")
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

        status = "Uploading"
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to DB
        record = schemas.UploadedFileCreate(
            file_name=file.filename,
            file_type=file.content_type.split("/")[-1],
            status=status,
            uploaded_at=currentTime
        )
        created_file = crud.save_file(db, record)
        db.commit()
        db.refresh(created_file)
        
        # Call Celery Worker to do task
        tasks.upload_pdf_task.delay(created_file.id, file.file.read())

        return created_file
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/files/", response_model=list[schemas.FileRecordResponse])
def read_files(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    
    return crud.get_file_records(db, skip=skip, limit=limit)

@app.get("/status/{file_id}")
def get_status(file_id: int, db: Session = Depends(get_db)):
    file = crud.get_file_status(db, file_id)
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return UploadedFileResponse.from_orm(file)

@app.delete("/delete/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    file = crud.delete_file_by_id(db, file_id)
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {"message": "File deleted successfully"}

@app.get("/parsed_content/{file_id}")
def get_parsed_content(file_id: int, db: Session = Depends(get_db)):
    parsed_content = db.query(ParsedContent).filter(ParsedContent.file_id == file_id).first()
    
    if not parsed_content:
        raise HTTPException(status_code=404, detail="Parsed content not found")
    
    processed_content = parsed_content.content.replace("\n", "<br>")
    html_content = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h1>File ID: {file_id}</h1>
        <div>
            {processed_content}
        </div>
    </div>
    """
    
    return HTMLResponse(content=html_content)
