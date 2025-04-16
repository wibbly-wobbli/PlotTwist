import customtkinter as ctk
from models import Book
from database import session

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class BookApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PlotTwist")
        self.geometry("500x500")
        self.current_book = None

        # Filter dropdown
        self.filter_option = ctk.CTkOptionMenu(
            self,
            values=["all", "want", "reading", "finished"],
            command=self.apply_filter
        )
        self.filter_option.set("all")
        self.filter_option.pack(pady=5)

        # Entry fields
        self.entry_title = ctk.CTkEntry(self, placeholder_text="Title")
        self.entry_author = ctk.CTkEntry(self, placeholder_text="Author")
        self.entry_title.pack(pady=5)
        self.entry_author.pack(pady=5)

        # Status dropdown
        self.status_option = ctk.CTkOptionMenu(self, values=["want", "reading", "finished"])
        self.status_option.set("want")
        self.status_option.pack(pady=5)

        # Rating slider
        self.rating_slider = ctk.CTkSlider(self, from_=0, to=5, number_of_steps=5, width=200)
        self.rating_slider.set(0)
        self.rating_slider.pack(pady=5)

        # Add book button
        self.button_add = ctk.CTkButton(self, text="Add New Book", command=self.open_add_book_editor)
        self.button_add.pack(pady=5)

        # Scrollable frame for book buttons
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=580, height=250)
        self.scroll_frame.pack(pady=10)

        # Load all books initially
        self.display_books()

    def open_add_book_editor(self):
        # Create a pop-up editor for adding a new book
        editor = ctk.CTkToplevel(self)
        editor.title("Add New Book")
        editor.geometry("400x400")

        # Title & author
        title_entry = ctk.CTkEntry(editor)
        title_entry.pack(pady=5)
        title_entry.insert(0, "")

        author_entry = ctk.CTkEntry(editor)
        author_entry.pack(pady=5)
        author_entry.insert(0, "")

        # Status
        status_menu = ctk.CTkOptionMenu(editor, values=["want", "reading", "finished"])
        status_menu.set("want")
        status_menu.pack(pady=5)

        # Rating
        rating_slider = ctk.CTkSlider(editor, from_=0, to=5, number_of_steps=5)
        rating_slider.set(0)
        rating_slider.pack(pady=5)

        # Review
        review_box = ctk.CTkTextbox(editor, height=100)
        review_box.pack(pady=5)

        # Save button
        def save_book():
            title = title_entry.get()
            author = author_entry.get()
            status = status_menu.get()
            rating = int(rating_slider.get())
            review = review_box.get("1.0", "end").strip()

            if title and author:
                book = Book(
                    title=title,
                    author=author,
                    genre="Unknown",
                    status=status,
                    rating=rating,
                    review=review
                )
                session.add(book)
                session.commit()
                editor.destroy()
                self.display_books()

        # Save the new book
        ctk.CTkButton(editor, text="Save New Book", command=save_book).pack(pady=5)

    def display_books(self, books=None):
        # Clear previous buttons
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if books is None:
            books = session.query(Book).all()

        for book in books:
            btn_text = f"{book.title} by {book.author} - [{book.status}] ({book.rating}/5)"
            book_button = ctk.CTkButton(
                self.scroll_frame,
                text=btn_text,
                command=lambda b=book: self.open_book_editor(b),
                width=550
            )
            book_button.pack(pady=3)

    def apply_filter(self, choice):
        if choice == "all":
            books = session.query(Book).all()
        else:
            books = session.query(Book).filter_by(status=choice).all()
        self.display_books(books)

    def open_book_editor(self, book):
        # Create a pop-up editor for the selected book
        editor = ctk.CTkToplevel(self)
        editor.title(f"Edit: {book.title}")
        editor.geometry("400x400")

        # Title & author
        title_entry = ctk.CTkEntry(editor)
        title_entry.insert(0, book.title)
        title_entry.pack(pady=5)

        author_entry = ctk.CTkEntry(editor)
        author_entry.insert(0, book.author)
        author_entry.pack(pady=5)

        # Status
        status_menu = ctk.CTkOptionMenu(editor, values=["want", "reading", "finished"])
        status_menu.set(book.status)
        status_menu.pack(pady=5)

        # Rating
        rating_slider = ctk.CTkSlider(editor, from_=0, to=5, number_of_steps=5)
        rating_slider.set(book.rating)
        rating_slider.pack(pady=5)

        # Review
        review_box = ctk.CTkTextbox(editor, height=100)
        review_box.insert("1.0", book.review or "")
        review_box.pack(pady=5)

        # Save button
        def save_book():
            book.title = title_entry.get()
            book.author = author_entry.get()
            book.status = status_menu.get()
            book.rating = int(rating_slider.get())
            book.review = review_box.get("1.0", "end").strip()
            session.commit()
            editor.destroy()
            self.display_books()

        # Delete button
        def delete_book():
            session.delete(book)
            session.commit()
            editor.destroy()
            self.display_books()

        ctk.CTkButton(editor, text="Save Changes", command=save_book).pack(pady=5)
        ctk.CTkButton(editor, text="Delete Book", command=delete_book).pack(pady=5)


if __name__ == "__main__":
    app = BookApp()
    app.mainloop()
