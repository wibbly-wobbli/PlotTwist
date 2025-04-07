# database.py
from models import session
from models import Book

def add_book_to_db(book):
    session.add(book)
    session.commit()

def search_books_by_title(title):
    return session.query(Book).filter(Book.title.ilike(f"%{title}%")).all()
