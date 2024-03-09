from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

#Declare client domain
origins = [
    'http://localhost:3000',
]

#Allow client to access the server
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

#Validate input from client
class TransactionBase(BaseModel):
    amount: float
    category: str
    description: str
    is_income: bool
    date: str

#Inheritance TransactionBase model to interacting with db and will auto convert response to json format
class TransactionModel(TransactionBase):
    id: int

    class Config:
        from_attributes = True

#Db dependency will turn on when get request and will turn off if no request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Obtain a database session
db_dependency = Annotated[Session, Depends(get_db)]

#Creating database tables based on the defined models
models.Base.metadata.create_all(bind=engine)

#Create transaction
@app.post("/transactions/", response_model=TransactionModel)
async def create_transaction(transaction: TransactionBase, db: db_dependency):
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

#Get transaction
@app.get("/transactions/", response_model=List[TransactionModel])
async def read_transactions(db: db_dependency, skip: int = 0, limit: int = 100):
    transactions = db.query(models.Transaction).offset(skip).limit(limit).all()
    return transactions
