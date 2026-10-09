from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas, crud
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Inventory Management API")

# --- Category Endpoints ---

@app.post("/categories/", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = crud.get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(status_code=400, detail="Category name already exists")
    return crud.create_category(db=db, category=category)

@app.get("/categories/", response_model=List[schemas.CategoryResponse])
def read_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)


# --- Books Endpoints ---

@app.post("/books/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    # Check if category exists
    category = crud.get_category(db, category_id=book.category_id)
    if not category:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot create book. Category ID {book.category_id} does not exist."
        )
    
    # Check if ISBN exists
    db_isbn = crud.get_book_by_isbn(db, isbn=book.isbn)
    if db_isbn:
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists.")
        
    return crud.create_book(db=db, book=book)

@app.get("/books/", response_model=List[schemas.BookResponse])
def read_books(category_id: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.get_books(db, category_id=category_id)

@app.get("/books/{book_id}", response_model=schemas.BookResponse)
def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = crud.get_book(db, book_id=book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found.")
    return db_book

@app.put("/books/{book_id}", response_model=schemas.BookResponse)
def update_book(book_id: int, book_update: schemas.BookUpdate, db: Session = Depends(get_db)):
    if book_update.category_id:
        category = crud.get_category(db, category_id=book_update.category_id)
        if not category:
            raise HTTPException(
                status_code=400, 
                detail=f"Category ID {book_update.category_id} does not exist."
            )

    updated_book = crud.update_book(db, book_id=book_id, book_update=book_update)
    if not updated_book:
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found.")
    return updated_book

@app.delete("/books/{book_id}", status_code=status.HTTP_200_OK)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    success = crud.delete_book(db, book_id=book_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found.")
    return {"message": f"Book with ID {book_id} successfully deleted."}
