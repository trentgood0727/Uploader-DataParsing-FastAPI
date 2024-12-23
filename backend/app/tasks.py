import os
from app.database import SessionLocal
from app.models import UploadedFile, ParsedContent
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from celery_worker import app 
from celery import shared_task
import time

UPLOAD_FOLDER = "../uploads/"

@shared_task
def upload_pdf_task(file_id, file_data):
    db = SessionLocal()
    file_record = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()

    if not file_record:
        print("File record not found")
        return

    try:
        # Save file
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, file_record.file_name)
        with open(file_path, "wb") as buffer:
            buffer.write(file_data)
        
        file_record.status = "Parsing"
        db.commit()
        
        # Next task
        parse_pdf_task(file_id, file_path)
    except Exception as e:
        file_record.status = "Failed"
        db.commit()
        print(f"File processing failed: {str(e)}")

@shared_task
def parse_pdf_task(file_id, file_path):
    db = SessionLocal()

    try:
        file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()

        if not file:
            raise Exception(f"File record with ID {file_id} not found.")
            #return "File not found"
        
        converter = PdfConverter(
            artifact_dict=create_model_dict(),
        )
        rendered = converter(file_path)
        text, _, images = text_from_rendered(rendered)
        parsed_content = ParsedContent(file_id=file_id, content=text)
        db.add(parsed_content)
        db.commit()
        file.status = "Completed"
        db.commit()
        return text
    except Exception as e:
        file.status = "Failed"
        db.commit()
        return str(e)
