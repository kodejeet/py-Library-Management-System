import json
import os
from datetime import date

# --- File Paths ---
BOOKS_FILE = "books.json"
MEMBERS_FILE = "members.json"
BORROWED_FILE = "borrowed.json"
TRANSACTIONS_FILE = "transactions.json"

# --- Data Storage ---
books, members, borrowed_data, transactions = [], [], {}, []

# --- Module V: OOP - Book & Member Classes ---
class Book:
    """Base class for library books."""
    def __init__(self, title, author, isbn, copies=0, year="N/A", desc=""):
        if not all([title, author, isbn]) or not isinstance(copies, int) or copies < 0:
            raise ValueError("Invalid book data.")
        self.title, self.author, self.isbn, self.total_copies = title, author, isbn, copies
        self.available_copies = copies
        self.publication_year, self.description = year, desc

    def display_detailed_info(self): # M5.6: Override method
        return (f"Title: {self.title}, Author: {self.author}, ISBN: {self.isbn}\n"
                f"Copies (Available/Total): {self.available_copies}/{self.total_copies}\n"
                f"Year: {self.publication_year}, Desc: {self.description}")

    def to_dict(self):
        data = self.__dict__.copy()
        data['type'] = 'Book'
        return data

class EBook(Book):
    """Derived class for E-books demonstrating polymorphism."""
    def __init__(self, title, author, isbn, copies, year, desc, format_type, link):
        super().__init__(title, author, isbn, copies, year, desc)
        self.format_type, self.download_link = format_type, link

    def display_detailed_info(self): # M5.7: Polymorphism
        return f"{super().display_detailed_info()}\nFormat: {self.format_type}, Link: {self.download_link}"
    
    def to_dict(self):
        data = super().to_dict()
        data['type'] = 'EBook'
        return data

class Member:
    """Class for library members."""
    def __init__(self, name, member_id, age, m_type="Standard"):
        if not all([name, member_id]) or not isinstance(age, int) or age <= 0:
            raise ValueError("Invalid member data.")
        self.name, self.member_id, self.age, self.membership_type = name, member_id, age, m_type
        # M1.6: Use if-else for membership borrowing limits
        self.borrowing_limit = 5 if m_type == "Premium" else 3

    def to_dict(self):
        return self.__dict__

# --- Helper Functions ---
def find_book(isbn): return next((b for b in books if b.isbn == isbn), None)
def find_member(member_id): return next((m for m in members if m.member_id == member_id), None)

# --- Module V: File Handling ---
def load_data():
    """Loads all data from JSON files."""
    global books, members, borrowed_data, transactions
    try:
        with open(BOOKS_FILE, 'r') as f:
            for item in json.load(f):
                cls = EBook if item.get("type") == "EBook" else Book
                item.pop('type', None)
                books.append(cls(**item))
    except (FileNotFoundError, json.JSONDecodeError): books = []
    try:
        with open(MEMBERS_FILE, 'r') as f: members = [Member(**m) for m in json.load(f)]
    except (FileNotFoundError, json.JSONDecodeError): members = []
    try:
        with open(BORROWED_FILE, 'r') as f: borrowed_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): borrowed_data = {}
    try:
        with open(TRANSACTIONS_FILE, 'r') as f: transactions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): transactions = []
    print("Data loaded from files.")

def save_data():
    """Saves all data to JSON files."""
    # M5.9: Exception handling in file operations
    try:
        with open(BOOKS_FILE, 'w') as f: json.dump([b.to_dict() for b in books], f, indent=2)
        with open(MEMBERS_FILE, 'w') as f: json.dump([m.to_dict() for m in members], f, indent=2)
        with open(BORROWED_FILE, 'w') as f: json.dump(borrowed_data, f, indent=2)
        with open(TRANSACTIONS_FILE, 'w') as f: json.dump(transactions, f, indent=2) # M5.10: Save issue/return transactions
        print("All data saved successfully.")
    except IOError as e: print(f"Error saving data: {e}")

# --- Module I: Basics & Data Handling ---
def add_book():
    """Adds a new book or ebook."""
    try:
        # M1.1: Input book data, M1.4: Validate inputs
        isbn = input("Enter ISBN: ")
        if find_book(isbn): print("Book with this ISBN already exists."); return
        title = input("Enter title: ")
        author = input("Enter author: ")
        copies = int(input("Enter number of copies: "))
        is_ebook = input("Is this an E-book? (y/n): ").lower() == 'y'
        if is_ebook:
            books.append(EBook(title, author, isbn, copies, input("Pub Year: "), input("Desc: "), input("Format: "), input("Link: ")))
        else:
            books.append(Book(title, author, isbn, copies, input("Pub Year: "), input("Desc: ")))
        print(f"Book '{title}' added.")
    except ValueError as e: print(f"Invalid input: {e}") # M5.1: Handle invalid input

def add_member():
    """Adds a new member."""
    try:
        # M1.2: Input member data
        member_id = input("Enter member ID: ")
        if find_member(member_id): print("Member with this ID already exists."); return
        name = input("Enter name: ")
        age = int(input("Enter age: "))
        m_type = input("Membership Type (Standard/Premium): ").capitalize()
        members.append(Member(name, member_id, age, m_type))
        print(f"Member '{name}' added.")
    except ValueError as e: print(f"Invalid input: {e}") # M5.1: Handle invalid input

def issue_book():
    """Issues a book to a member."""
    member = find_member(input("Enter member ID: "))
    book = find_book(input("Enter book ISBN: "))
    if not member or not book: print("Invalid member or book ID."); return
    # M1.5: Check if a book is available
    if book.available_copies < 1: print("No copies available."); return
    borrowed_count = len(borrowed_data.get(member.member_id, [])) # M1.3: Calculate total books borrowed
    if borrowed_count >= member.borrowing_limit: print("Member has reached borrowing limit."); return
    
    book.available_copies -= 1
    borrowed_data.setdefault(member.member_id, []).append(book.isbn)
    transactions.append({'type': 'issue', 'member': member.member_id, 'book': book.isbn, 'date': str(date.today())})
    print(f"'{book.title}' issued to '{member.name}'.")

def return_book():
    """Returns a book from a member."""
    member = find_member(input("Enter member ID: "))
    book = find_book(input("Enter book ISBN: "))
    if not member or not book: print("Invalid member or book ID."); return
    
    if member.member_id in borrowed_data and book.isbn in borrowed_data[member.member_id]:
        book.available_copies += 1 # M3.9: Update copies on return
        borrowed_data[member.member_id].remove(book.isbn)
        if not borrowed_data[member.member_id]: del borrowed_data[member.member_id]
        transactions.append({'type': 'return', 'member': member.member_id, 'book': book.isbn, 'date': str(date.today())})
        print(f"'{book.title}' returned by '{member.name}'.")
    else: print("This book is not borrowed by this member.")

def display_borrowing_summary(): # M1.7: Display borrowing summary
    if not borrowed_data: print("No books are currently borrowed."); return
    for member_id, isbns in borrowed_data.items():
        member_name = find_member(member_id).name if find_member(member_id) else "Unknown"
        print(f"\nMember: {member_name} (ID: {member_id})")
        for isbn in isbns:
            book_title = find_book(isbn).title if find_book(isbn) else "Unknown Book"
            print(f"  - {book_title} (ISBN: {isbn})")

# --- Module II: String Operations ---
def string_operations_menu():
    """Menu for various string manipulation tasks."""
    op_map = {
        '1': ("Reverse Book Titles", lambda: [print(f"'{b.title}' -> '{b.title[::-1]}'") for b in books]),
        '2': ("Remove Vowels from Author Names", lambda: [print(f"'{b.author}' -> '{''.join(c for c in b.author if c.lower() not in 'aeiou')}'") for b in books]),
        '3': ("Count Char Frequency in Titles", lambda: (char := input("Enter char: "), print(f"Count: {sum(b.title.count(char) for b in books)}"))),
        '4': ("Check Title Palindrome", lambda: [print(f"'{b.title}' is {'a palindrome' if (t := ''.join(filter(str.isalnum, b.title)).lower()) == t[::-1] else 'not a palindrome'}") for b in books]),
        '5': ("Search Substring in Titles", lambda: (sub := input("Enter substring: "), [print(b.display_detailed_info()) for b in books if sub.lower() in b.title.lower()])),
        '6': ("Format Member Names", lambda: [setattr(m, 'name', m.name.title()) for m in members] and print("Names formatted.")),
        '7': ("Compare Two Author Names", lambda: (a1 := input("Author 1: "), a2 := input("Author 2: "), print("Same" if a1.lower() == a2.lower() else "Different"))),
        '8': ("Convert Book Titles to Uppercase", lambda: [setattr(b, 'title', b.title.upper()) for b in books] and print("Titles converted to uppercase."))
    }
    print("\n--- String Operations ---")
    for k, v in op_map.items(): print(f"{k}. {v[0]}")
    choice = input("Choose an option: ")
    if choice in op_map: op_map[choice][1]()

# --- Module III: Lists & Dictionaries ---
def list_and_dict_operations():
    """Functions related to lists and dictionaries."""
    print("\n1. List All Books\n2. List All Members\n3. Remove Duplicate Books (by ISBN)\n4. Find Second Most Issued Book\n5. Sort Books by Title")
    choice = input("Choose an option: ")
    if choice == '1':
        for b in books: print(f"\n{b.display_detailed_info()}")
    elif choice == '2':
        for m in members: print(f"\nName: {m.name}, ID: {m.member_id}, Age: {m.age}")
    elif choice == '3':
        unique_books, seen_isbns = [], set()
        for book in books:
            if book.isbn not in seen_isbns:
                unique_books.append(book); seen_isbns.add(book.isbn)
        if len(unique_books) < len(books):
            globals()['books'] = unique_books
            print(f"Removed {len(books) - len(unique_books)} duplicates.")
        else: print("No duplicates found.")
    elif choice == '4':
        issue_counts = {}
        for isbn_list in borrowed_data.values():
            for isbn in isbn_list: issue_counts[isbn] = issue_counts.get(isbn, 0) + 1
        if len(issue_counts) < 2: print("Not enough books issued."); return
        second_most_isbn = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[1][0]
        book = find_book(second_most_isbn)
        print(f"Second most issued book: '{book.title}'")
    elif choice == '5': # M3.6: Sort books by title
        sorted_books = sorted(books, key=lambda b: b.title.lower())
        for b in sorted_books: print(f"- {b.title} by {b.author}")

# --- Module IV: Functions & Sorting ---
def other_operations():
    """Handles various other functionalities."""
    print("\n1. Sort Members by Name (Lambda)\n2. Recursive Factorial Example")
    choice = input("Choose an option: ")
    if choice == '1': # M4.7: Lambda to sort members by name
        sorted_members = sorted(members, key=lambda m: m.name.lower())
        for m in sorted_members: print(f"- {m.name} (ID: {m.member_id})")
    elif choice == '2': # M4.8: Recursive factorial
        def factorial(n): return 1 if n <= 1 else n * factorial(n - 1)
        try:
            num = int(input("Enter number for factorial: "))
            print(f"Factorial of {num} is {factorial(num)}")
        except ValueError: print("Invalid number.")

# --- Main Program Loop ---
def main():
    """Main function to run the Library Management System."""
    load_data()
    
    menu = {
        '1': ('Add Book', add_book),
        '2': ('Add Member', add_member),
        '3': ('Issue Book', issue_book),
        '4': ('Return Book', return_book),
        '5': ('Show Borrowing Summary', display_borrowing_summary),
        '6': ('List & Dictionary Ops', list_and_dict_operations),
        '7': ('String Ops', string_operations_menu),
        '8': ('Other Ops (Sorting/Recursion)', other_operations),
        '9': ('Save All Data', save_data),
        '0': ('Exit', None)
    }

    while True:
        print("\n--- Library Management System ---")
        for key, (desc, _) in menu.items():
            print(f"{key}. {desc}")
        
        choice = input("Enter your choice: ")
        if choice == '0':
            save_data()
            print("Exiting.")
            break
        
        action = menu.get(choice)
        if action:
            try:
                action[1]() # Execute the function
            except Exception as e:
                print(f"An unexpected error occurred: {e}") # General exception handling
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()