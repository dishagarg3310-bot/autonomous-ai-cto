from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, ForeignKey, DateTime, Text, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import uuid
import os

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



class Service(Base):
    __tablename__ = "services"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    opening_hours = Column(Text)
    gallery_images = Column(Text)

class ContactMessage(Base):
    __tablename__ = "contact_messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    service_id = Column(String, ForeignKey("services.id"))
    message = Column(String)

Base.metadata.create_all(bind=engine)



class ServiceCreate(BaseModel):
    name: str
    opening_hours: dict
    gallery_images: list

class ServiceResponse(BaseModel):
    id: str
    name: str | None = None
    opening_hours: dict
    gallery_images: list

    class Config:
        from_attributes = True

class ContactMessageCreate(BaseModel):
    service_id: str
    message: str

class ContactMessageResponse(BaseModel):
    id: str
    service_id: str | None = None
    message: str | None = None

    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/services/{id}", response_model=ServiceResponse)
def get_service(id: str, limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(Service).filter(Service.id == id)
    item = query.first()
    if item is None:
        raise HTTPException(status_code=404, detail="Not found")
    return item

@app.get("/services/{id}/opening_hours", response_model=ServiceResponse)
def get_service_opening_hours(id: str, limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(Service).filter(Service.id == id)
    item = query.first()
    if item is None:
        raise HTTPException(status_code=404, detail="Not found")
    return item

@app.get("/services/{id}/gallery_images", response_model=list[ServiceResponse])
def get_service_gallery_images(id: str, limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == id).first()
    if service:
        gallery_images = service.gallery_images
        return gallery_images[offset:offset + limit]
    else:
        raise HTTPException(status_code=404, detail="Service not found")

@app.post("/services/{id}/contact", response_model=ContactMessageResponse)
def submit_contact_message(id: str, contact_message: ContactMessageCreate, db: Session = Depends(get_db)):
    try:
        db_contact_message = ContactMessage(service_id=id, message=contact_message.message)
        db.add(db_contact_message)
        db.commit()
        db.refresh(db_contact_message)
        return ContactMessageResponse.from_orm(db_contact_message)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid data")