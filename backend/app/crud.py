from sqlalchemy.orm import Session
from app.models import UploadedFile, ParsedContent
from app.schemas import UploadedFileCreate, ParsedContentCreate, FileRecordResponse
import os

def save_file(db: Session, file: UploadedFileCreate):
    db_file = UploadedFile(
        file_name=file.file_name,
        file_type=file.file_type,
        status=file.status,
        uploaded_at=file.uploaded_at
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_file_status(db: Session, file_id: int):
    return db.query(UploadedFile).filter(UploadedFile.id == file_id).first()

def save_parsed_content(db: Session, content: ParsedContentCreate):
    db_content = ParsedContent(
        file_id=content.file_id,
        content=content.content,
    )
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

def delete_file_by_id(db: Session, file_id: int, uploads_folder: str = "../uploads"):
    file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if file:
        db.query(ParsedContent).filter(ParsedContent.file_id == file_id).delete()

        file_path = os.path.join(uploads_folder, file.file_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"File {file.file_name} successfully deleted.")
            except Exception as e:
                print(f"Error deleting file {file.file_name}: {e}")

        db.delete(file)
        db.commit()

    return file


def get_file_records(db: Session, skip: int = 0, limit: int = 10):
    files = db.query(UploadedFile).offset(skip).limit(limit).all()
    return [FileRecordResponse.from_orm(file) for file in files]
