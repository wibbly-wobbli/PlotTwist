import customtkinter as ctk
from models import Book
from database import session

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class BookApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PlotTwist")
        self.geometry("600x700")
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
        self.button_add = ctk.CTkButton(self, text="Add Book", command=self.add_book)
        self.button_add.pack(pady=5)

        # Book list
        self.book_listbox = ctk.CTkTextbox(self, width=580, height=250)
        self.book_listbox.pack(pady=10)
        self.book_listbox.bind("<ButtonRelease-1>", self.on_book_select)

        # Review Label + Textbox
        self.review_label = ctk.CTkLabel(self, text="Review (selected book)")
        self.review_label.pack(pady=(10, 0))
        self.review_textbox = ctk.CTkTextbox(self, height=100)
        self.review_textbox.configure(state="disabled")
        self.review_textbox.pack(pady=5)

        # Save/Delete buttons
        self.save_button = ctk.CTkButton(self, text="Save Changes", command=self.save_changes)
        self.delete_button = ctk.CTkButton(self, text="Delete Book", command=self.delete_book)
        self.save_button.pack(pady=5)
        self.delete_button.pack(pady=5)

        # Load all books initially
        self.display_books()

    def add_book(self):
        title = self.entry_title.get()
        author = self.entry_author.get()
        status = self.status_option.get()
        rating = int(self.rating_slider.get())

        if not title or not author:
            return

        book = Book(
            title=title,
            author=author,
            genre="Unknown",
            status=status,
            rating=rating,
            review=""
        )
        session.add(book)
        session.commit()
        self.display_books()
        self.entry_title.delete(0, 'end')
        self.entry_author.delete(0, 'end')

    def display_books(self, books=None):
        self.book_listbox.delete("1.0", "end")
        if books is None:
            books = session.query(Book).all()
        for book in books:
            self.book_listbox.insert(
                "end",
                f"{book.title} by {book.author} - [{book.status}] ({book.rating}/5)\n"
            )

    def apply_filter(self, choice):
        if choice == "all":
            books = session.query(Book).all()
        else:
            books = session.query(Book).filter_by(status=choice).all()
        self.display_books(books)

    def on_book_select(self, event=None):
        try:
            selected_text = self.book_listbox.get("sel.first", "sel.last")
            title = selected_text.split(" by ")[0].strip()
            book = session.query(Book).filter_by(title=title).first()
            if book:
                self.current_book = book
                self.review_textbox.configure(state="normal")
                self.review_textbox.delete("1.0", "end")
                self.review_textbox.insert("1.0", book.review or "")
                self.status_option.set(book.status)
                self.rating_slider.set(book.rating)
        except:
            pass

    def save_changes(self):
        if self.current_book:
            self.current_book.review = self.review_textbox.get("1.0", "end").strip()
            self.current_book.status = self.status_option.get()
            self.current_book.rating = int(self.rating_slider.get())
            session.commit()
            self.display_books()

    def delete_book(self):
        if self.current_book:
            session.delete(self.current_book)
            session.commit()
            self.review_textbox.delete("1.0", "end")
            self.review_textbox.configure(state="disabled")
            self.current_book = None
            self.display_books()


if __name__ == "__main__":
    app = BookApp()
    app.mainloop()
