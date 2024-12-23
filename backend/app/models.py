from app.database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class UploadedFile(Base):
    __tablename__ = "file_records"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    status = Column(String(50), default="Uploading")
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to ParsedContent (one-to-many)
    parsed_content = relationship("ParsedContent", back_populates="uploaded_file")

class ParsedContent(Base):
    __tablename__ = "parsed_content"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("file_records.id"), nullable=False)
    content = Column(Text, nullable=False)

    # Relationship back to UploadedFile
    uploaded_file = relationship("UploadedFile", back_populates="parsed_content")

