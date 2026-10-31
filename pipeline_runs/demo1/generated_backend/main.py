from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, ForeignKey, DateTime
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
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class Photo(Base):
    __tablename__ = "photos"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String, ForeignKey("users.id"))
    filename = Column(String)
    description = Column(String)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    photo_id = Column(String, ForeignKey("photos.id"))
    owner_id = Column(String, ForeignKey("users.id"))
    text = Column(String)

Base.metadata.create_all(bind=engine)



class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str

    class Config:
        from_attributes = True

class PhotoCreate(BaseModel):
    owner_id: str
    filename: str
    description: str

class PhotoResponse(BaseModel):
    id: str
    owner_id: str
    filename: str
    description: str

    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    photo_id: str
    owner_id: str
    text: str

class CommentResponse(BaseModel):
    id: str
    photo_id: str
    owner_id: str
    text: str

    class Config:
        from_attributes = True


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
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create user")
    return new_user

@app.post("/auth/login")
def login(credentials: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/photos", response_model=PhotoResponse)
def create_photo(photo: PhotoCreate, db: Session = Depends(get_db)):
    db_photo = Photo(**photo.dict())
    db.add(db_photo)
    try:
        db.commit()
        db.refresh(db_photo)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error")
    return PhotoResponse.from_orm(db_photo)

@app.get("/photos", response_model=list[PhotoResponse])
def list_photos(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(Photo)
    return query.offset(offset).limit(limit).all()

@app.get("/photos/{id}", response_model=PhotoResponse)
def get_photo(id: str, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == id).first()
    if photo:
        return PhotoResponse.from_orm(photo)
    else:
        raise HTTPException(status_code=404, detail="Photo not found")

@app.post("/photos/{id}/comments", response_model=CommentResponse)
def create_photo_comment(id: str, comment: CommentCreate, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    comment_db = Comment(**comment.dict(), photo_id=id)
    db.add(comment_db)
    try:
        db.commit()
        db.refresh(comment_db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid comment data")
    
    return CommentResponse.from_orm(comment_db)

@app.get("/photos/{id}/comments", response_model=list[CommentResponse])
def list_comments(id: str, limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(Comment).filter(Comment.photo_id == id)
    return query.offset(offset).limit(limit).all()