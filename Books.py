# Books.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from auth import get_current_active_user, User
from datetime import timedelta

router = APIRouter ()

ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Book model
class Book (BaseModel):
    id: int
    title: str
    author: str
    description: Optional [str] = None


# Make a dynamic list of books
books = [
    Book (id=1, title="The Great Gatsby", author="F. Scott Fitzgerald", description="The story of the fabulously wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan."),
    Book (id=2, title="The Catcher in the Rye", author="J.D. Salinger", description="The story of a young teenager named Holden Caulfield who struggles with his own disillusionment."),
    Book (id=3, title="To Kill a Mockingbird", author="Harper Lee", description="The story of a young female narrator and her brother growing up in the South during the Great Depression."),
    Book (id=4, title="1984", author="George Orwell", description="The story of a dystopian future where critical thought is suppressed by a totalitarian regime."),
    Book (id=5, title="Pride and Prejudice", author="Jane Austen", description="The story of the Bennet family and their five unmarried daughters.")
]


@router.post ("/books/", response_model=Book)
def create_book(book: Book, current_user: User = Depends (get_current_active_user)):
    books.append (book)
    return book


@router.get ("/books/", response_model=List [Book])
def read_books(current_user: User = Depends (get_current_active_user)):
    return books


@router.get ("/books/{book_id}", response_model=Book)
def read_book(book_id: int, current_user: User = Depends (get_current_active_user)):
    for book in books:
        if book.id == book_id:
            return book
    raise HTTPException (status_code=404, detail="Book not found")


@router.put ("/books/{book_id}", response_model=Book)
def update_book(book_id: int, updated_book: Book, current_user: User = Depends (get_current_active_user)):
    for index, book in enumerate (books):
        if book.id == book_id:
            books [index] = updated_book
            return updated_book
    raise HTTPException (status_code=404, detail="Book not found")


@router.delete ("/books/{book_id}", response_model=Book)
def delete_book(book_id: int, current_user: User = Depends (get_current_active_user)):
    for index, book in enumerate (books):
        if book.id == book_id:
            return books.pop (index)
    raise HTTPException (status_code=404, detail="Book not found")
