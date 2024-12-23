from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# docker
DATABASE_URL = "postgresql://admin:123456@db:5432/file_upload_db"
# local
#DATABASE_URL = "postgresql://admin:123456@localhost:5432/file_upload_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
