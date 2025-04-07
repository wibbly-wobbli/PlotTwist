from models import Book, session

def add_book():
    title = input("Title: ")
    author = input("Author: ")
    genre = input("Genre: ")
    status = input("Status (read/reading/want): ")
    rating = float(input("Rating (0-5): "))
    review = input("Review: ")

    book = Book(
        title=title,
        author=author,
        genre=genre,
        status=status,
        rating=rating,
        review=review
    )
    session.add(book)
    session.commit()
    print("Book added!")
    
def search_books_by_title():
    search = input("Enter book title to search: ")
    results = session.query(Book).filter(Book.title.ilike(f"%{search}%")).all()
    for book in results:
        print(f"{book.title} by {book.author} — {book.rating}/5")
