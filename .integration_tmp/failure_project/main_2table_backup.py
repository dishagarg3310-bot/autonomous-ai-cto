from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    email = Column(String)

class Order(Base):
    __tablename__ = "orders"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    item_name = Column(String)
    quantity = Column(Integer)
    status = Column(String)

Base.metadata.create_all(bind=engine)



class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    user_id: str
    item_name: str
    quantity: int
    status: str

class OrderResponse(BaseModel):
    id: str
    user_id: str
    item_name: str
    quantity: int
    status: str

    class Config:
        from_attributes = True

class OrderUpdate(BaseModel):
    user_id: Optional[str] = None
    item_name: Optional[str] = None
    quantity: Optional[int] = None
    status: Optional[str] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/create", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserResponse.from_orm(db_user)

@app.get("/users/{id}", response_model=UserResponse)
def get_user(id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)

@app.post("/orders/create", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return OrderResponse.from_orm(db_order)

@app.get("/orders/{id}", response_model=OrderResponse)
def get_order(id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderResponse.from_orm(order)

@app.put("/orders/{id}", response_model=OrderResponse)
def update_order(id: str, order_update: OrderUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    for field, value in order_update.dict(exclude_unset=True).items():
        setattr(order, field, value)
    try:
        db.commit()
        db.refresh(order)
        return OrderResponse.from_orm(order)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Invalid update")

@app.delete("/orders/{id}", response_model=OrderResponse)
def delete_order(id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    deleted_data = OrderResponse.from_orm(order)
    db.delete(order)
    db.commit()
    return deleted_data