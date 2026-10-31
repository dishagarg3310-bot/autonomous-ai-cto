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



class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String)
    hashed_password = Column(String)

class Note(Base):
    __tablename__ = "notes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String, ForeignKey("users.id"))
    content = Column(Text)
    is_future_review = Column(Boolean)

Base.metadata.create_all(bind=engine)



class UserCreate(BaseModel):
    email: str = Field(..., description="User's email address")
    password: str = Field(..., description="User's password (plain text)")

class UserResponse(BaseModel):
    id: str = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    
    class Config:
        from_attributes = True

class NoteCreate(BaseModel):
    owner_id: str
    content: str
    is_future_review: bool | None = None

class NoteResponse(BaseModel):
    id: str
    owner_id: str
    content: str
    is_future_review: bool
    model_config = ConfigDict(from_attributes=True)

class NoteUpdate(BaseModel):
    owner_id: str | None = None
    content: str | None = None
    is_future_review: bool | None = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# --- Authentication helpers ---
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

security_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme), db: Session = Depends(get_db)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


@app.post("/auth/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(user.password)
    new_user = User(email=user.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/login")
def login(credentials: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/notes", response_model=NoteResponse)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    new_note = Note(**note.dict())
    db.add(new_note)
    try:
        db.commit()
        db.refresh(new_note)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Note already exists")
    return NoteResponse.from_orm(new_note)

@app.get("/notes", response_model=list[NoteResponse])
def list_notes(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(Note)
    return query.offset(offset).limit(limit).all()

@app.get("/notes/future", response_model=list[NoteResponse])
def list_notes(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(Note)
    return query.offset(offset).limit(limit).all()

@app.put("/notes/{id}", response_model=NoteResponse)
def update_note(id: str, item: NoteUpdate, db: Session = Depends(get_db)):
    existing = db.query(Note).filter(Note.id == id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Not found")
    update_data = item.dict(exclude_unset=True)
    for field_name, value in update_data.items():
        setattr(existing, field_name, value)
    db.commit()
    db.refresh(existing)
    return existing

@app.delete("/notes/{id}")
def delete_note(id: str, db: Session = Depends(get_db)):
    existing = db.query(Note).filter(Note.id == id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(existing)
    db.commit()
    return {"message": "Deleted successfully"}