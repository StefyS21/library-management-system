import csv
import os
import random
from datetime import datetime, timedelta

# --- Configuration ---
FILE_NAME = 'library_data.txt'
FIELDNAMES = ['BookID', 'Title', 'Author', 'TotalCopies', 'AvailableCopies']

class Book:
    """Represents a book in the library's collection."""
    def __init__(self, book_id, title, author, total_copies, available_copies):
        self.book_id = str(book_id)
        self.title = title
        self.author = author
        # Ensuring numerical types with exception handling
        try:
            self.total_copies = int(total_copies)
            self.available_copies = int(available_copies)
        except ValueError:
            self.total_copies = 0
            self.available_copies = 0

    def __str__(self):
        """Returns a formatted string of the book's details."""
        return (f"ID: {self.book_id:<5} | Title: {self.title:<30} | Author: {self.author:<20} | "
                f"Total: {self.total_copies:<3} | Available: {self.available_copies:<3}")

    def to_dict(self):
        """Converts the Book object to a dictionary for CSV writing."""
        return {
            'BookID': self.book_id,
            'Title': self.title,
            'Author': self.author,
            'TotalCopies': self.total_copies,
            'AvailableCopies': self.available_copies
        }
        
    def check_out(self):
        """Decrements available copies upon borrowing."""
        if self.available_copies > 0:
            self.available_copies -= 1
            return True
        return False
        
    def check_in(self):
        """Increments available copies upon returning."""
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            return True
        return False

class Library:
    """Manages the entire collection of books and library operations."""
    def __init__(self):
        self.books = self._load_books()
        # This dictionary stores issued books: {BookID: (IssueDate, DueDate)}
        # In a real system, you'd track users too, but this simplifies the core logic.
        self.issued_books = {} 

    # --- File Handling ---

    def _load_books(self):
        """Loads book records from the CSV file."""
        books = []
        if not os.path.exists(FILE_NAME):
            try:
                with open(FILE_NAME, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                    writer.writeheader()
                return books
            except Exception as e:
                print(f"Error creating file: {e}")
                return books

        try:
            with open(FILE_NAME, 'r', newline='') as f:
                reader = csv.DictReader(f, fieldnames=FIELDNAMES)
                next(reader) # Skip the header row
                for row in reader:
                    # Exception Handling for corrupted data rows
                    try:
                        if all(key in row for key in FIELDNAMES):
                            book = Book(
                                row['BookID'], row['Title'], row['Author'], 
                                row['TotalCopies'], row['AvailableCopies']
                            )
                            books.append(book)
                    except Exception as e:
                        print(f"Skipping corrupted book record: {row} -> Error: {e}")
            return books
        except Exception as e:
            print(f"An error occurred during file loading: {e}")
            return books

    def save_books(self):
        """Saves the current list of Book objects back to the CSV file."""
        try:
            with open(FILE_NAME, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()
                for book in self.books:
                    writer.writerow(book.to_dict())
            print(f"\n--- Catalog saved successfully to {FILE_NAME} ---")
        except Exception as e:
            print(f"\n!!! ERROR: Could not save data to file. {e} !!!")

    # --- Utility Functions ---
    
    def _get_next_id(self):
        """Generates a random 4-digit ID for a new book."""
        existing_ids = {book.book_id for book in self.books}
        while True:
            new_id = str(random.randint(1000, 9999))
            if new_id not in existing_ids:
                return new_id

    def _find_book(self, query):
        """Finds a book object by ID or Title (returns the first match)."""
        query = query.lower()
        for book in self.books:
            if query == book.book_id.lower() or query in book.title.lower():
                return book
        return None

    # --- Core Features ---

    def add_book(self):
        """Allows adding a new book to the catalog."""
        print("\n--- Add New Book ---")
        book_id = self._get_next_id()
        title = input("Enter Title: ").strip()
        author = input("Enter Author: ").strip()
        
        while True:
            try:
                # Exception Handling for quantity input
                total_copies = int(input("Enter Total Number of Copies: "))
                if total_copies <= 0:
                    print("Quantity must be a positive number.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a number for quantity.")
        
        # Available copies start equal to total copies
        new_book = Book(book_id, title, author, total_copies, total_copies)
        self.books.append(new_book)
        print(f"\n✅ Book '{title}' added with ID: {book_id}")

    def display_all_books(self):
        """Displays all books in the catalog."""
        print("\n--- Current Library Catalog ---")
        if not self.books:
            print("The library catalog is currently empty.")
            return

        print("-" * 80)
        # Using the __str__ method of the Book class to display
        for book in self.books:
            print(book)
        print("-" * 80)

    def search_book(self):
        """Searches for books by ID or Title."""
        query = input("\nEnter Book ID or Title to search: ").strip()
        if not query:
            return

        found_books = [
            b for b in self.books 
            if query.lower() in b.book_id.lower() or query.lower() in b.title.lower()
        ]

        if found_books:
            print("\n--- Search Results ---")
            for book in found_books:
                print(book)
        else:
            print(f"No book found matching '{query}'.")

    def issue_book(self):
        """Handles the process of checking out a book."""
        query = input("\nEnter Book ID or Title to issue: ").strip()
        book = self._find_book(query)

        if not book:
            print("Book not found in the catalog.")
            return

        if book.check_out():
            due_date = datetime.now() + timedelta(days=14) # Set due date for 14 days
            self.issued_books[book.book_id] = (datetime.now(), due_date)
            print(f"✅ Successfully issued '{book.title}'.")
            print(f"   Due Date: {due_date.strftime('%Y-%m-%d')}")
        else:
            print(f"❌ Cannot issue '{book.title}'. All copies are currently checked out.")

    def return_book(self):
        """Handles the process of returning a book and fine calculation."""
        query = input("\nEnter Book ID or Title to return: ").strip()
        book = self._find_book(query)

        if not book:
            print("Book not found in the catalog.")
            return

        if book.book_id not in self.issued_books:
            print(f"❌ Book ID {book.book_id} was not recorded as issued.")
            # Still check in the book just in case the record was lost
            if book.available_copies < book.total_copies:
                book.check_in()
                print("   (Available copies incremented anyway.)")
            return
        
        # Process the return
        if book.check_in():
            issue_date, due_date = self.issued_books.pop(book.book_id)
            print(f"✅ Successfully returned '{book.title}'.")
            
            # Fine Calculation (Simplified)
            today = datetime.now()
            if today > due_date:
                overdue_days = (today - due_date).days
                fine = overdue_days * 10 # Rs 10 per day fine
                print(f"⚠️ Book is {overdue_days} days overdue. Fine: Rs {fine:.2f}")
            else:
                print("   Returned on time. No fine.")
        else:
            print(f"❌ Error: Cannot return '{book.title}'. Available copies equals total copies.")
            

# --- Main Application Loop ---

def main():
    """The main function to run the Library Management System."""
    library = Library()
    
    while True:
        print("\n==============================================")
        print("    LIBRARY MANAGEMENT SYSTEM (using Python)")
        print("==============================================")
        print("1. Add New Book")
        print("2. Display All Books")
        print("3. Search Book (by ID or Title)")
        print("4. Issue Book")
        print("5. Return Book & Calculate Fine")
        print("6. Exit & Save Catalog")
        print("----------------------------------------------")

        choice = input("Enter your choice (1-6): ").strip()

        if choice == '1':
            library.add_book()
        elif choice == '2':
            library.display_all_books()
        elif choice == '3':
            library.search_book()
        elif choice == '4':
            library.issue_book()
        elif choice == '5':
            library.return_book()
        elif choice == '6':
            library.save_books()
            print("👋 Thank you for using the Library Management System. Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please enter a number between 1 and 6.")

# Execute the main function
if __name__ == "__main__":
    main()