import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv("../.env")

# Reads DATABASE_URL passed by Docker, or falls back to 'mysql-booklog' host
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DB_USER = "root"
    DB_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")
    DB_NAME = os.getenv("MYSQL_DATABASE", "booklog_db")
    DB_HOST = os.getenv("DB_HOST", "mysql-booklog")  # Points to MySQL container
    DB_PORT = os.getenv("DB_PORT", "3306")
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model for Books
class BookModel(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    author = Column(String(255))
    rating = Column(Integer)

# Automatically create the table in MySQL if it doesn't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="BookLog API")

# Enable CORS so your React frontend can talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schema for incoming request validation
class BookCreate(BaseModel):
    title: str
    author: str
    rating: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. ADD a book (POST)
@app.post("/books/")
def add_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = BookModel(title=book.title, author=book.author, rating=book.rating)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# 2. VIEW all books (GET)
@app.get("/books/")
def get_books(db: Session = Depends(get_db)):
    return db.query(BookModel).all()

# 3. DELETE a book by ID (DELETE)
@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted successfully"}
