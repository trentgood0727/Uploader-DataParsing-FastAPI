from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# For uploading and checking status
class UploadedFileBase(BaseModel):
    file_name: str
    file_type: str
    status: str
    uploaded_at: datetime

class UploadedFileCreate(UploadedFileBase):
    pass

class UploadedFileResponse(UploadedFileBase):
    id: int

    class Config:
        orm_mode = True

# For checking
class FileRecordResponse(BaseModel):
    id: int
    file_name: str
    file_type: str
    status: str
    uploaded_at: datetime

    class Config:
        orm_mode = True
        from_attributes=True

# For parsing
class ParsedContentBase(BaseModel):
    file_id: int
    content: str

class ParsedContentCreate(ParsedContentBase):
    pass

class ParsedContentResponse(ParsedContentBase):
    id: int

    class Config:
        orm_mode = True

