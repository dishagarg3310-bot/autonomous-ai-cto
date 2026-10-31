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
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")

class Student(Base):
    __tablename__ = "students"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    name = Column(String)
    grade = Column(String)

class Mark(Base):
    __tablename__ = "marks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"))
    subject = Column(String)
    score = Column(Integer)

Base.metadata.create_all(bind=engine)



class UserCreate(BaseModel):
    email: str
    role: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    role: str | None = None

    class Config:
        from_attributes = True

class StudentCreate(BaseModel):
    user_id: str
    name: str
    grade: str

class StudentResponse(BaseModel):
    id: str
    user_id: str | None = None
    name: str | None = None
    grade: str | None = None

    class Config:
        from_attributes = True

class StudentUpdate(BaseModel):
    user_id: Optional[str] = None
    name: Optional[str] = None
    grade: Optional[str] = None

class MarkCreate(BaseModel):
    student_id: str
    subject: str
    score: int

class MarkResponse(BaseModel):
    id: str
    student_id: str | None = None
    subject: str | None = None
    score: int

    class Config:
        from_attributes = True

class MarkUpdate(BaseModel):
    student_id: Optional[str] = None
    subject: Optional[str] = None
    score: Optional[int] = None


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
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
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

@app.post("/students", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    try:
        db_student = Student(**student.dict())
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return StudentResponse(**db_student.dict())
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Student already exists")

@app.put("/students/{id}", response_model=StudentResponse)
def update_student(id: str, item: StudentUpdate, db: Session = Depends(get_db)):
    existing = db.query(Student).filter(Student.id == id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Not found")
    update_data = item.dict(exclude_unset=True)
    for field_name, value in update_data.items():
        setattr(existing, field_name, value)
    try:
        db.commit()
        db.refresh(existing)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error")
    return existing

@app.post("/marks", response_model=MarkResponse)
def create_mark(mark: MarkCreate, db: Session = Depends(get_db)):
    try:
        db_mark = Mark(**mark.dict())
        db.add(db_mark)
        db.commit()
        db.refresh(db_mark)
        return MarkResponse.from_orm(db_mark)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/marks/{id}", response_model=MarkResponse)
def update_mark(id: str, item: MarkUpdate, db: Session = Depends(get_db)):
    existing = db.query(Mark).filter(Mark.id == id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Not found")
    update_data = item.dict(exclude_unset=True)
    for field_name, value in update_data.items():
        setattr(existing, field_name, value)
    db.commit()
    db.refresh(existing)
    return existing

@app.get("/students/{id}/marks", response_model=MarkResponse)
def get_student_marks(id: str, current_user: Mark = Depends(get_current_user)):
    try:
        marks = Mark.query.filter_by(student_id=id).all()
        return [MarkResponse.from_orm(mark) for mark in marks]
    except Exception as e:
        return {"error": str(e)}